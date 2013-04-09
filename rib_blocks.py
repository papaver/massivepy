#------------------------------------------------------------------------------
#
#             DO WHAT THE FUCK YOU WANT TO PUBLIC LICENSE
#                     Version 2, December 2004
#
#  Copyright (C) 2013 Electronic Dreams <maverick.babylon.drifter@gmail.com>
#
#  Everyone is permitted to copy and distribute verbatim or modified
#  copies of this license document, and changing it is allowed as long
#  as the name is changed.
#
#             DO WHAT THE FUCK YOU WANT TO PUBLIC LICENSE
#    TERMS AND CONDITIONS FOR COPYING, DISTRIBUTION AND MODIFICATION
#
#   0. You just DO WHAT THE FUCK YOU WANT TO.
#
#------------------------------------------------------------------------------

#------------------------------------------------------------------------------
# rib_blocks.py - Blocks found in Massive rib files. (.rib)
#------------------------------------------------------------------------------

import re

from scanf import sscanf
from scanf import IncompleteCaptureError

#------------------------------------------------------------------------------
# class AntBlock
#------------------------------------------------------------------------------

class AntBlock(object):
    """Ant entry in a rib file.
    """

    #--------------------------------------------------------------------------
    # statics
    #--------------------------------------------------------------------------

    _sPattern = '(?P<type>\w+)\s"(?P<mode>\w+)"\s' \
                '\["(?P<program>[^\s]+)"\s"(?P<id>\d+)\s(?P<cdl>[^\s]+)\s(?P<apf>[^\s]+)\s' \
                '(?P<frame>-?\d+)\s(?P<vars>.+?)"]\s(?P<transform>\[.+?])'

    _sTransformFormatting = "[%g %g %g %g %g %g]"

    #--------------------------------------------------------------------------
    # methods
    #--------------------------------------------------------------------------

    def __init__(self, block):
        """Initialize self with scene data.
        """
        super(AntBlock, self).__init__()

        # parse the entry using regex pattern
        match        = re.match(AntBlock._sPattern, block)
        self.type    = match.group('type')
        self.mode    = match.group('mode')
        self.program = match.group('program')
        self.id      = int(match.group('id'))
        self.cdl     = match.group('cdl')
        self.apf     = match.group('apf')
        self.frame   = int(match.group('frame'))

        # parse variable data
        variableData = match.group('vars').split(' ')
        names        = variableData[0::2]
        values       = variableData[1::2]

        # use dictionary to manage variables
        self.variables = {}
        self._varOrder = names
        for name, value in zip(names, values):
            if name not in self.variables:
                self.variables[name], = sscanf(value, "%f")
            else:
                raise ValueError("Duplicate variable name '%s' found, ant %s from %s" % \
                        (name, self.id, self.cdl))

        # parse transform
        transform                 = match.group('transform')
        formatting                = AntBlock._sTransformFormatting.replace('%g', '%f')
        (tx, ty, tz, rx, ry, rz)  = sscanf(transform, formatting)
        self.tx, self.ty, self.tz = tx, ty, tz
        self.rx, self.ry, self.rz = rx, ry, rz

    #--------------------------------------------------------------------------

    def __str__(self):
        data      = self._dataStr()
        transform = AntBlock._sTransformFormatting % \
                    (self.tx, self.ty, self.tz, self.rx, self.ry, self.rz)
        block     = '%s "%s" %s %s' % (self.type, self.mode, data, transform)
        return block

    #--------------------------------------------------------------------------
    # methods
    #--------------------------------------------------------------------------

    def _variablesStr(self):
        """Convert dictionary of data into a string. Making sure order is
        preserved.
        """

        order = []

        # add all the originally parsed variables
        for name in self._varOrder:
            if name in self.variables:
                order.append(name)

        # add all the new variables
        for name in self.variables.keys():
            if name not in self._varOrder:
                order.append(name)

        # join together
        return " ".join(["%s %g" % (name, self.variables[name]) for name in order])

    #--------------------------------------------------------------------------

    def _dataStr(self):
        """Convert data section into a string.
        """

        # setup args for template
        args = {
            'program' : self.program,
            'id'      : self.id,
            'cdl'     : self.cdl,
            'apf'     : self.apf,
            'frame'   : self.frame,
            'vars'    : self._variablesStr()
        }

        # replace args in template
        template = '["%(program)s" "%(id)s %(cdl)s %(apf)s %(frame)s %(vars)s"]'
        return template % args

