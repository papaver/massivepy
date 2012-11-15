#------------------------------------------------------------------------------
# block.py - Base class for blocks found in Massive files.
#------------------------------------------------------------------------------

import re

from scanf import sscanf
from scanf import IncompleteCaptureError

#------------------------------------------------------------------------------
# class Block
#------------------------------------------------------------------------------

class Block(object):
    """Base class for blocks of data in massive files.
    """

    #--------------------------------------------------------------------------
    # initialization
    #--------------------------------------------------------------------------

    def __init__(self):
        pass

    #--------------------------------------------------------------------------
    # helper methods
    #--------------------------------------------------------------------------

    def _removeIndent(self, block, count=1):
        """Removes 4 space indents from the block.
        """
        return re.compile(r"^%s" % "    " * count, re.M).sub("", block)

    #--------------------------------------------------------------------------

    def _addIndent(self, block, count=1):
        """Adds 4 space indents to the block.
        """
        return re.compile(r"^((?!$))", re.M).sub("    " * count, block)

    #--------------------------------------------------------------------------
    # attribute handler methods
    #--------------------------------------------------------------------------

    def _createAttributeFormattingMap(self, scanf_list, reformat=True):
        """Convert the scanf formatting list into a hash for easy lookup.

        If multiple entrys are found for an attribute they are placed into a
        list in the order found. Order of entries are also returned.
        """

        order     = []
        scanf_map = {}
        for entry in scanf_list:

            # grab attribute
            attribute = re.split('\s', entry)[0]

            # add to order
            if attribute.startswith('_') or (not attribute in order):
                order.append(attribute)

            # reformat entry since sscanf doesn't support %g
            if reformat:
                entry = entry.replace('%g', '%f')

            # make format entry into list if multiple formats exist
            if attribute in scanf_map:
                formats = scanf_map[attribute]
                if not isinstance(formats, list):
                    scanf_map[attribute] = [formats]
                scanf_map[attribute].append(entry)
            else:
                scanf_map[attribute] = entry

        return scanf_map, order

    #--------------------------------------------------------------------------

    def _setAttribute(self, attribute, value):
        """Sets the value for the given attribute.

        If the attribute already exists, the attribute will be converted into
        a list to accomadate multiple values.
        """

        # if multiple values found
        if hasattr(self, attribute):

            # make sure attribute is a list
            values = getattr(self, attribute)
            if not isinstance(values, list):
                setattr(self, attribute, [values])

            # append value to list
            getattr(self, attribute).append(value)

        # single value found
        else:
            setattr(self, attribute, value)

    #--------------------------------------------------------------------------

    def _parseAttributeString(self, line):
        """Value after the attribute is treated as a single string.
        """
        attribute, value = line.partition(' ')[::2]
        self._setAttribute(attribute, value)

    #--------------------------------------------------------------------------

    def _parseAttributeScanf(self, line, formatting):
        """Use scanf to parse the data from the line.

        Formatting can be a single entry or a list of entrys.  If multiple
        entrys are available the first matching entry will be returned.
        """

        # multiple entrys
        if isinstance(formatting, list):
            for scanf_format in formatting:
                try:
                    #print "<<<----", scanf_format, line
                    return sscanf(line, scanf_format)
                except IncompleteCaptureError, e:
                    pass

        # single entry
        else:
            return sscanf(line, formatting)

        # problem if none of the formats worked
        raise IncompleteCaptureError("Format error for %s" % line)

    #--------------------------------------------------------------------------

    def parseAttributes(self, block, scanf_list, special_list={}, skip_list=[]):
        """Parses block for attributes using the formatting.
        """

        # remove trailing newlines
        block = block.strip('\n')

        # create a hash of the attributes for easy lookup
        scanf_map, order = self._createAttributeFormattingMap(scanf_list)

        # loop over the block line by line
        index = 0
        rest  = []
        lines = block.split('\n')
        while index < len(lines):

            # grab line and increment
            line   = lines[index]
            index += 1

            # gather up indented child lines
            children = []
            while (index < len(lines)) and re.match('^(?:\t|    )', lines[index]):
                children.append(lines[index])
                index += 1

            # add children to line
            children.insert(0, line)
            line = "\n".join(children)

            # use proper seperator to grab the attribute name
            attribute = re.split('\s', line)[0]

            # skip attribute
            if attribute in skip_list:
                #print "skip_list-> ", attribute, line
                rest.append(line)

            # use special formatter
            elif attribute in special_list:
                #print "special_list-> ", attribute, line
                special_list[attribute](line)

            # use scanf formatter
            elif attribute in scanf_map:
                #print "scanf-> ", attribute, line
                value = self._parseAttributeScanf(line, scanf_map[attribute])

                # remove from tuple if single value
                if len(value) == 1:
                    value = value[0]

                # set attribute
                self._setAttribute(attribute, value)

            # attribute not found
            else:
                #print "rest-> ", attribute, line
                rest.append(line)

        # add default entires for missing attibutes
        for attribute in scanf_map.keys():
            if not hasattr(self, attribute):
                setattr(self, attribute, None)

        # return unused lines
        return "\n".join(rest) + "\n"

    #--------------------------------------------------------------------------

    def _printAttributePrintf(self, formatting, value):
        """Use printf (%) to export the data from the line.

        Formatting can be a single entry or a list of entrys.  If multiple
        entrys are available the first matching entry will be returned.
        """

        # multiple entrys
        if isinstance(formatting, list):

            for scanf_format in formatting:
                try:
                    #print "-->>", scanf_format, value
                    return scanf_format % value
                except TypeError, e:
                    pass

        # single entry
        else:
            return formatting % value

        # problem if none of the formats worked
        raise TypeError("Valid format not found for values.")

    #--------------------------------------------------------------------------

    def printAttributes(self, scanf_list, special_list={}):
        """Prints out all of the attributes in the list.
        """

        # create a hash of the attributes for easy lookup
        scanf_map, order = self._createAttributeFormattingMap(scanf_list, False)

        # print out all of the attributes
        block = ""
        for attribute in order:

            # seperator
            if attribute == "_seperator_":
                block += '\n'
                continue

            # use special formatter
            if attribute in special_list:
                special_block = special_list[attribute]()
                if special_block != '':
                    block += special_block + '\n'
                continue

            # only process attributes that exist on the object
            if not hasattr(self, attribute):
                continue

            # skip empty attributes
            value = getattr(self, attribute)
            if value == None:
                continue

            # add attribute to block
            formatting = scanf_map[attribute]
            if isinstance(value, list):
                for entry in value:
                    block += self._printAttributePrintf(formatting, entry) + "\n"
            else:
                block += self._printAttributePrintf(formatting, value) + "\n"

        return block
