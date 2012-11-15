#------------------------------------------------------------------------------
# cdl_blocks.py - Blocks found in Massive agent files. (.cdl)
#------------------------------------------------------------------------------

import os
import re

from scanf import sscanf
from scanf import IncompleteCaptureError

from block  import Block
from common import Variable

#------------------------------------------------------------------------------
# class Object Block
#------------------------------------------------------------------------------

class ObjectBlock(Block):
    """Object block holding all agent data.
    """

    #--------------------------------------------------------------------------
    # statics
    #--------------------------------------------------------------------------

    _sBlockFormatting = [
        "id     %d",
        "colour %f",
        "sprites %s %d-%d %fx%f",
        "angles %s",                    # degrees, radians, revolutions
        "order %s",
        "macro_style %s",
        "variable %s %f [%f %f] %s",
        "variable %s %f [%f %f]",
        "scale_var %s",
        "thick_var %s",
        "tx_var %s",
        "ty_var %s",
        "tz_var %s",
        "muscle_inc_per_sec %d",
        "muscle_gravity %g",
        "ribs %s",
        "grunt_shader_path %s",
        "bind_pose %s",
        "render_pass %s",
        "rib_include %i %s %s",
        "bounding_box_tolerance %g",
        "script %s",
        "dso %s",
        "collisions %s",                # off, normal, no_reaction
        "vision_zplane_distance",
        "z_factor %g",
        "vision %g %g %d %d",
        "geo_visible %d",
        "display geometry",
        "movement absolute",
        "dynamics",
        "translate %f %f %f",
        "transform",
        "_seperator_",                  # seperator for write formatting
        "afield",
        "standin",
        "segment",
        "spring",
        "material %s",
        "cloth %s",
        "geometry %s",
        "option",
        "hair %s",
        "bone %s",
        "fuzzy %s",
        "action %s",
        "action_binary %s",
        "default_action %d %s %s",
        "_seperator_",                  # seperator for write formatting
        "tree active %d",
        "_seperator_",                  # seperator for write formatting
        "motion tree"
    ]

    #--------------------------------------------------------------------------
    # methods
    #--------------------------------------------------------------------------

    def __init__(self, block):
        """Initialize self with scene data.
        """
        super(ObjectBlock, self).__init__()

        # initialize fields
        self.variables   = []
        self.dynamics    = None
        self.transform   = None
        self.afields     = []
        self.standins    = []
        self.segments    = []
        self.springs     = []
        self.materials   = []
        self.clothes     = []
        self.geometries  = []
        self.options     = []
        self.hairs       = []
        self.bones       = []
        self.fuzzies     = []
        self.actions     = []
        self.motiontrees = []

        # fix block formatting for consistancy
        block = self._processBlock(block, "pre")

        # remove the block header
        header, block = block.partition('\n')[::2]
        self._parseHeader(header)

        # remove indent from block
        block = self._removeIndent(block)

        # setup special parse list
        special_list = {
            "render_pass" : self._parseAttributeString,
            "variable"    : self._parseVariable,
            "dynamics"    : self._parseDynamics,
            "transform"   : self._parseTransform,
            "afield"      : self._parseAField,
            "standin"     : self._parseStandin,
            "segment"     : self._parseSegment,
            "spring"      : self._parseSpring,
            "material"    : self._parseMaterial,
            "cloth"       : self._parseCloth,
            "geometry"    : self._parseGeometry,
            "option"      : self._parseOption,
            "hair"        : self._parseHair,
            "bone"        : self._parseBone,
            "fuzzy"       : self._parseFuzzy,
            "action"      : self._parseAction,
            "motion"      : self._parseMotionTree
        }

        # setup skip list
        skip_list = ['end']

        # parse the attributes
        self.parseAttributes(
            block, ObjectBlock._sBlockFormatting, special_list, skip_list)

    #--------------------------------------------------------------------------

    def __str__(self):
        """Reconstructs object data in a text block.
        """

        # setup special parse list
        special_list = {
            "variable"    : self._printVariable,
            "dynamics"    : self._printDynamics,
            "transform"   : self._printTransform,
            "afield"      : self._printAField,
            "standin"     : self._printStandin,
            "segment"     : self._printSegment,
            "spring"      : self._printSpring,
            "material"    : self._printMaterial,
            "cloth"       : self._printCloth,
            "geometry"    : self._printGeometry,
            "option"      : self._printOption,
            "hair"        : self._printHair,
            "bone"        : self._printBone,
            "fuzzy"       : self._printFuzzy,
            "action"      : self._printAction,
            "motion"      : self._printMotionTree,
            "_seperator_" : lambda: ""
        }

        # reconstruct the object block
        header = "object %s" % self.name
        block  = self.printAttributes(
            ObjectBlock._sBlockFormatting, special_list)
        block  = "%s\n%send object" % (header, self._addIndent(block))

        # post process to add back its fucked up ness (thanks massive)
        block = self._processBlock(block, "post")

        return block

    #--------------------------------------------------------------------------
    # helper methods
    #--------------------------------------------------------------------------

    def _processBlock(self, block, mode):
        """Attempts to fix the fucked up indenting that the cdl file uses.
        """

        # we can either pre or post process the block
        if mode == "pre":
            addIndent    = self._addIndent
            removeIndent = self._removeIndent
        elif mode == "post":
            addIndent    = self._removeIndent
            removeIndent = self._addIndent

        # split up the block into lines
        lines = block.split('\n')

        # run through each line fixing the indentation
        new_lines     = []
        in_main_block = True
        in_dynamics   = False
        in_motiontree = True
        skip_count    = 0
        for index in range(len(lines)):
            line = lines[index]

            # - context checking -

            # mark entrance into dynamics block
            if line.startswith("    dynamics"):
                in_dynamics = True
            elif line.startswith("    end dynamics"):
                in_dynamics = False

            # mark entrance into motion tree
            elif line.startswith("motion tree"):
                in_motiontree = True

            # check for main block exit
            elif in_main_block and (line == ''):
                in_main_block = False

            # - formatting -

            if skip_count > 0:
                skip_count -= 1
                pass

            # skip start object tag
            elif line.startswith("object"):
                pass

            # main block formatting
            elif in_main_block:

                # special processing for dynamics block
                if in_dynamics:
                    if line.lstrip(' ').startswith("rbd_solver"):
                        lines[index] = addIndent(line)

                # variables should be unindented by one tab
                elif line.lstrip(' ').startswith("variable"):
                    lines[index] = removeIndent(line)

                # skip end dynamics tag
                elif line.lstrip(' ').startswith("end dynamics"):
                    pass

                # skip translate tag
                elif line.lstrip(' ').startswith("translate"):
                    pass

                # skip transform tag
                elif line.lstrip(' ').startswith("transform"):
                    skip_count = 4
                    pass

                # default to adding an indent
                else:
                    lines[index] = addIndent(line)

            # add indent to first motion tree line seperator
            elif in_motiontree and (line == ''):
                if mode == "pre":
                    lines[index]  = "        "
                in_motiontree = False

            # skip object end tag
            elif line.startswith("end object"):
                pass

            elif (mode == "post") and line.lstrip(' ').startswith('\t'):
                lines[index] = line.lstrip(' ')

            # default to adding an indent
            else:
                lines[index] = addIndent(line)

        # return newly formatted block
        return "\n".join(lines)

    #--------------------------------------------------------------------------

    def _parseHeader(self, header):
        """Object block header contains object name.
        """
        formating    = "object %s"
        (self.name,) = sscanf(header, formating)

    #--------------------------------------------------------------------------

    def _parseVariable(self, block):
        """Collate all of the agent variables.
        """
        formatting = ObjectBlock._sBlockFormatting[6:8]
        data       = self._parseAttributeScanf(block, formatting)
        self.variables.append(Variable(*data))

    #--------------------------------------------------------------------------

    def _printVariable(self):
        variables = "\n".join(map(str, self.variables))
        return variables

    #--------------------------------------------------------------------------

    def _parseDynamics(self, block):
        self.dynamics = DynamicsBlock(block)

    #--------------------------------------------------------------------------

    def _printDynamics(self):
        block = str(self.dynamics)
        return block

    #--------------------------------------------------------------------------

    def _parseTransform(self, block):
        header, block  = block.partition('\n')[::2]
        block          = self._removeIndent(block).rstrip('\n')
        self.transform = map(float, re.compile('\s+').sub(' ', block).split(' '))

    #--------------------------------------------------------------------------

    def _printTransform(self):
        block = ""
        if self.transform:
            header     = "transform"
            formatting = "%.7f\t%.7f\t%.7f\t%.7f"
            vectors    = [self.transform[i:i+4] for i in range(0, 16, 4)]
            transform  = "\n".join([formatting % tuple(v) for v in vectors])
            block      = "%s\n%s" % (header, self._addIndent(transform))
        return block

    #--------------------------------------------------------------------------

    def _parseAField(self, block):
        self.afields.append(AFieldBlock(block))

    #--------------------------------------------------------------------------

    def _printAField(self):
        block = "\n".join(map(str, self.afields))
        return block

    #--------------------------------------------------------------------------

    def _parseStandin(self, block):
        self.standins.append(StandinBlock(block))

    #--------------------------------------------------------------------------

    def _printStandin(self):
        block = "\n".join(map(str, self.standins))
        return block

    #--------------------------------------------------------------------------

    def _parseSegment(self, block):
        self.segments.append(SegmentNode(block))

    #--------------------------------------------------------------------------

    def _printSegment(self):
        block = "\n".join(map(str, self.segments))
        return block

    #--------------------------------------------------------------------------

    def _parseSpring(self, block):
        self.springs.append(SpringNode(block))

    #--------------------------------------------------------------------------

    def _printSpring(self):
        block = "\n".join(map(str, self.springs))
        return block

    #--------------------------------------------------------------------------

    def _parseMaterial(self, block):
        self.materials.append(MaterialNode(block))

    #--------------------------------------------------------------------------

    def _printMaterial(self):
        block = "\n".join(map(str, self.materials))
        return block

    #--------------------------------------------------------------------------

    def _parseCloth(self, block):
        self.clothes.append(ClothNode(block))

    #--------------------------------------------------------------------------

    def _printCloth(self):
        block = "\n".join(map(str, self.clothes))
        return block

    #--------------------------------------------------------------------------

    def _parseGeometry(self, block):
        self.geometries.append(GeometryNode(block))

    #--------------------------------------------------------------------------

    def _printGeometry(self):
        block = "\n".join(map(str, self.geometries))
        return block

    #--------------------------------------------------------------------------

    def _parseOption(self, block):
        self.options.append(OptionNode(block))

    #--------------------------------------------------------------------------

    def _printOption(self):
        block = "\n".join(map(str, self.options))
        return block

    #--------------------------------------------------------------------------

    def _parseHair(self, block):
        self.hairs.append(HairNode(block))

    #--------------------------------------------------------------------------

    def _printHair(self):
        block = "\n".join(map(str, self.hairs))
        return block

    #--------------------------------------------------------------------------

    def _parseBone(self, block):
        self.bones.append(BoneBlock(block))

    #--------------------------------------------------------------------------

    def _printBone(self):
        block = "\n".join(map(str, self.bones))
        return '' if block == '' else block + '\n'

    #--------------------------------------------------------------------------

    def _parseFuzzy(self, block):
        self.fuzzies.append(FuzzyNode(block))

    #--------------------------------------------------------------------------

    def _printFuzzy(self):
        block = "\n".join(map(str, self.fuzzies))
        return block

    #--------------------------------------------------------------------------

    def _parseAction(self, block):
        self.actions.append(ActionBlock(block))

    #--------------------------------------------------------------------------

    def _printAction(self):
        block = "\n".join(map(str, self.actions))[0:-1]
        return '' if block == '' else '\n' + block

    #--------------------------------------------------------------------------

    def _parseMotionTree(self, block):
        self.motiontrees.append(MotionTreeBlock(block))

    #--------------------------------------------------------------------------

    def _printMotionTree(self):
        block = "\n".join(map(str, self.motiontrees))
        return block

#------------------------------------------------------------------------------
# class DynamicsBlock
#------------------------------------------------------------------------------

class DynamicsBlock(Block):
    """Defines agents dynamics settings.
    """

    #--------------------------------------------------------------------------
    # statics
    #--------------------------------------------------------------------------

    _sBlockFormatting = [
    ]

    #--------------------------------------------------------------------------
    # methods
    #--------------------------------------------------------------------------

    def __init__(self, block):
        """Initialize self with agent data.
        """
        super(DynamicsBlock, self).__init__()

        # remove the block header
        header, block = block.partition('\n')[::2]
        self._parseHeader(header)

        # remove indent from block
        block = self._removeIndent(block)

        # save attributes
        self._raw = block

    #--------------------------------------------------------------------------

    def __str__(self):
        block = self._raw
        return "dynamics\n%s\nend dynamics" % self._addIndent(block)

    #--------------------------------------------------------------------------
    # methods
    #--------------------------------------------------------------------------

    def _parseHeader(self, header):
        """Dynamics header contains nothing but start tag.
        """
        formating = "dynamics"
        sscanf(header, formating)

#------------------------------------------------------------------------------
# class AFieldBlock
#------------------------------------------------------------------------------

class AFieldBlock(Block):
    """Defines an agent field.
    """

    #--------------------------------------------------------------------------
    # statics
    #--------------------------------------------------------------------------

    _sBlockFormatting = [
    ]

    #--------------------------------------------------------------------------
    # methods
    #--------------------------------------------------------------------------

    def __init__(self, block):
        """Initialize self with agent data.
        """
        super(AFieldBlock, self).__init__()

        # remove the block header
        header, block = block.partition('\n')[::2]
        self._parseHeader(header)

        # remove indent from block
        block = self._removeIndent(block)

        # save attributes
        self._raw = block

    #--------------------------------------------------------------------------

    def __str__(self):
        header = "afield %s %s" % (self.type, self.name)
        block  = self._raw
        return "%s\n%s\nend afield\n" % (header, self._addIndent(block))

    #--------------------------------------------------------------------------
    # methods
    #--------------------------------------------------------------------------

    def _parseHeader(self, header):
        """Segment node header may contain segment name.
        """
        formatting = "afield %s %s"
        (self.type, self.name) = sscanf(header, formatting)

#------------------------------------------------------------------------------
# class StandinBlock
#------------------------------------------------------------------------------

class StandinBlock(Block):
    """Defines agent standins.
    """

    #--------------------------------------------------------------------------
    # statics
    #--------------------------------------------------------------------------

    _sBlockFormatting = [
    ]

    #--------------------------------------------------------------------------
    # methods
    #--------------------------------------------------------------------------

    def __init__(self, block):
        """Initialize self with agent data.
        """
        super(StandinBlock, self).__init__()

        # remove the block header
        header, block = block.partition('\n')[::2]
        self._parseHeader(header)

        # remove indent from block
        block = self._removeIndent(block)

        # save attributes
        self._raw = block

    #--------------------------------------------------------------------------

    def __str__(self):
        header = "standin %s" % self.name
        block  = self._raw
        return "%s\n%s\n" % (header, self._addIndent(block))

    #--------------------------------------------------------------------------
    # methods
    #--------------------------------------------------------------------------

    def _parseHeader(self, header):
        """Segment node header may contain segment name.
        """
        formatting = "standin %s"
        (self.name,) = sscanf(header, formatting)

#------------------------------------------------------------------------------
# class SegmentNode
#------------------------------------------------------------------------------

class SegmentNode(Block):
    """Defines an agent joint.
    """

    #--------------------------------------------------------------------------
    # statics
    #--------------------------------------------------------------------------

    _sBlockFormatting = [
    ]

    #--------------------------------------------------------------------------
    # methods
    #--------------------------------------------------------------------------

    def __init__(self, block):
        """Initialize self with agent data.
        """
        super(SegmentNode, self).__init__()

        # remove the block header
        header, block = block.partition('\n')[::2]
        self._parseHeader(header)

        # remove indent from block
        block = self._removeIndent(block)

        # save attributes
        self._raw = block

    #--------------------------------------------------------------------------

    def __str__(self):
        header = ("segment %s" % self.name) if self.name else "segment"
        block  = self._raw
        return "%s\n%s\n" % (header, self._addIndent(block))

    #--------------------------------------------------------------------------
    # methods
    #--------------------------------------------------------------------------

    def _parseHeader(self, header):
        """Segment node header may contain segment name.
        """

        named     = "segment %s"
        anonymous = "segment"

        # check if segment named
        try:
            (self.name,) = sscanf(header, named)
        except IncompleteCaptureError, e:
            sscanf(header, anonymous)
            self.name = None

#------------------------------------------------------------------------------
# class SpringNode
#------------------------------------------------------------------------------

class SpringNode(Block):
    """Defines an agent spring.
    """

    #--------------------------------------------------------------------------
    # statics
    #--------------------------------------------------------------------------

    _sBlockFormatting = [
    ]

    #--------------------------------------------------------------------------
    # methods
    #--------------------------------------------------------------------------

    def __init__(self, block):
        """Initialize self with agent data.
        """
        super(SpringNode, self).__init__()

        # remove the block header
        header, block = block.partition('\n')[::2]
        self._parseHeader(header)

        # remove indent from block
        block = self._removeIndent(block)

        # save attributes
        self._raw = block

    #--------------------------------------------------------------------------

    def __str__(self):
        header = ("spring %s" % self.name) if self.name else "spring"
        block  = self._raw
        return "%s\n%s\n" % (header, self._addIndent(block))

    #--------------------------------------------------------------------------
    # methods
    #--------------------------------------------------------------------------

    def _parseHeader(self, header):
        """Spring node header may contain spring name.
        """

        named     = "spring %s"
        anonymous = "spring"

        # check if spring named
        try:
            (self.name,) = sscanf(header, named)
        except IncompleteCaptureError, e:
            sscanf(header, anonymous)
            self.name = None

#------------------------------------------------------------------------------
# class MaterialNode
#------------------------------------------------------------------------------

class MaterialNode(Block):
    """Defines an agent material.
    """

    #--------------------------------------------------------------------------
    # statics
    #--------------------------------------------------------------------------

    _sBlockFormatting = [
    ]

    #--------------------------------------------------------------------------
    # methods
    #--------------------------------------------------------------------------

    def __init__(self, block):
        """Initialize self with agent data.
        """
        super(MaterialNode, self).__init__()

        # remove the block header
        header, block = block.partition('\n')[::2]
        self._parseHeader(header)

        # remove indent from block
        block = self._removeIndent(block)

        # save attributes
        self._raw = block

    #--------------------------------------------------------------------------

    def __str__(self):
        header = ("material %s" % self.name) if self.name else "material"
        block  = self._raw
        return "%s\n%s\n" % (header, self._addIndent(block))

    #--------------------------------------------------------------------------
    # methods
    #--------------------------------------------------------------------------

    def _parseHeader(self, header):
        """Material node header may contain material name.
        """

        named     = "material %s"
        anonymous = "material"

        # check if material named
        try:
            (self.name,) = sscanf(header, named)
        except IncompleteCaptureError, e:
            sscanf(header, anonymous)
            self.name = None

#------------------------------------------------------------------------------
# class ClothNode
#------------------------------------------------------------------------------

class ClothNode(Block):
    """Defines agent cloth.
    """

    #--------------------------------------------------------------------------
    # statics
    #--------------------------------------------------------------------------

    _sBlockFormatting = [
    ]

    #--------------------------------------------------------------------------
    # methods
    #--------------------------------------------------------------------------

    def __init__(self, block):
        """Initialize self with agent data.
        """
        super(ClothNode, self).__init__()

        # remove the block header
        header, block = block.partition('\n')[::2]
        self._parseHeader(header)

        # remove indent from block
        block = self._removeIndent(block)

        # save attributes
        self._raw = block

    #--------------------------------------------------------------------------

    def __str__(self):
        header = ("cloth %s" % self.name) if self.name else "cloth"
        block  = self._raw
        return "%s\n%s\n" % (header, self._addIndent(block))

    #--------------------------------------------------------------------------
    # methods
    #--------------------------------------------------------------------------

    def _parseHeader(self, header):
        """Cloth node header may contain cloth name.
        """

        named     = "cloth %s"
        anonymous = "cloth"

        # check if cloth named
        try:
            (self.name,) = sscanf(header, named)
        except IncompleteCaptureError, e:
            sscanf(header, anonymous)
            self.name = None

#------------------------------------------------------------------------------
# class GeometryNode
#------------------------------------------------------------------------------

class GeometryNode(Block):
    """Defines agent geometry.
    """

    #--------------------------------------------------------------------------
    # statics
    #--------------------------------------------------------------------------

    _sBlockFormatting = [
    ]

    #--------------------------------------------------------------------------
    # methods
    #--------------------------------------------------------------------------

    def __init__(self, block):
        """Initialize self with agent data.
        """
        super(GeometryNode, self).__init__()

        # remove the block header
        header, block = block.partition('\n')[::2]
        self._parseHeader(header)

        # remove indent from block
        block = self._removeIndent(block)

        # save attributes
        self._raw = block

    #--------------------------------------------------------------------------

    def __str__(self):
        header = ("geometry %s" % self.name) if self.name else "geometry"
        block  = self._raw
        return "%s\n%s\n" % (header, self._addIndent(block))

    #--------------------------------------------------------------------------
    # methods
    #--------------------------------------------------------------------------

    def _parseHeader(self, header):
        """Geometry node header may contain geometry name.
        """

        named     = "geometry %s"
        anonymous = "geometry"

        # check if geometry named
        try:
            (self.name,) = sscanf(header, named)
        except IncompleteCaptureError, e:
            sscanf(header, anonymous)
            self.name = None

#------------------------------------------------------------------------------
# class OptionNode
#------------------------------------------------------------------------------

class OptionNode(Block):
    """Defines an agent option.
    """

    #--------------------------------------------------------------------------
    # statics
    #--------------------------------------------------------------------------

    _sBlockFormatting = [
    ]

    #--------------------------------------------------------------------------
    # methods
    #--------------------------------------------------------------------------

    def __init__(self, block):
        """Initialize self with agent data.
        """
        super(OptionNode, self).__init__()

        # remove the block header
        header, block = block.partition('\n')[::2]
        self._parseHeader(header)

        # remove indent from block
        block = self._removeIndent(block)

        # save attributes
        self._raw = block

    #--------------------------------------------------------------------------

    def __str__(self):
        header = ("option %s" % self.name) if self.name else "option"
        block  = self._raw
        return "%s\n%s\n\n" % (header, self._addIndent(block))

    #--------------------------------------------------------------------------
    # methods
    #--------------------------------------------------------------------------

    def _parseHeader(self, header):
        """Option node header may contain option name.
        """
        _, _, name = header.partition(' ')
        self.name  = None if name == '' else name

#------------------------------------------------------------------------------
# class HairNode
#------------------------------------------------------------------------------

class HairNode(Block):
    """Defines agent hair.
    """

    #--------------------------------------------------------------------------
    # statics
    #--------------------------------------------------------------------------

    _sBlockFormatting = [
    ]

    #--------------------------------------------------------------------------
    # methods
    #--------------------------------------------------------------------------

    def __init__(self, block):
        """Initialize self with agent data.
        """
        super(HairNode, self).__init__()

        # remove the block header
        header, block = block.partition('\n')[::2]
        self._parseHeader(header)

        # remove indent from block
        block = self._removeIndent(block)

        # save attributes
        self._raw = block

    #--------------------------------------------------------------------------

    def __str__(self):
        header = ("hair %s" % self.name) if self.name else "hair"
        block  = self._raw
        return "%s\n%s\n" % (header, self._addIndent(block))

    #--------------------------------------------------------------------------
    # methods
    #--------------------------------------------------------------------------

    def _parseHeader(self, header):
        """Hair node header may contain hair name.
        """

        named     = "hair %s"
        anonymous = "hair"

        # check if hair named
        try:
            (self.name,) = sscanf(header, named)
        except IncompleteCaptureError, e:
            sscanf(header, anonymous)
            self.name = None

#------------------------------------------------------------------------------
# class BoneBlock
#------------------------------------------------------------------------------

class BoneBlock(Block):
    """Defines an agent bone.
    """

    #--------------------------------------------------------------------------
    # statics
    #--------------------------------------------------------------------------

    _sBlockFormatting = [
    ]

    #--------------------------------------------------------------------------
    # methods
    #--------------------------------------------------------------------------

    def __init__(self, block):
        """Initialize self with agent data.
        """
        super(BoneBlock, self).__init__()

        # remove the block header
        header, block = block.partition('\n')[::2]
        self._parseHeader(header)

        # remove indent from block
        block = self._removeIndent(block)

        # save attributes
        self._raw = block

    #--------------------------------------------------------------------------

    def __str__(self):
        header = "bone %s" % self.name
        block  = self._raw
        return "%s\n%s" % (header, self._addIndent(block))

    #--------------------------------------------------------------------------
    # methods
    #--------------------------------------------------------------------------

    def _parseHeader(self, header):
        """Bone node header contains bone name.
        """
        formatting = "bone %s"
        (self.name,) = sscanf(header, formatting)

#------------------------------------------------------------------------------
# class FuzzyNode
#------------------------------------------------------------------------------

class FuzzyNode(Block):
    """Defines an agent brain node.
    """

    #--------------------------------------------------------------------------
    # statics
    #--------------------------------------------------------------------------

    _sBlockFormatting = [
    ]

    #--------------------------------------------------------------------------
    # methods
    #--------------------------------------------------------------------------

    def __init__(self, block):
        """Initialize self with agent data.
        """
        super(FuzzyNode, self).__init__()

        # remove the block header
        header, block = block.partition('\n')[::2]
        self._parseHeader(header)

        # remove indent from block
        block = self._removeIndent(block)

        # save attributes
        self._raw = block

    #--------------------------------------------------------------------------

    def __str__(self):
        header = "fuzzy %s" % self.type
        block  = self._raw
        return "%s\n%s" % (header, self._addIndent(block))

    #--------------------------------------------------------------------------
    # methods
    #--------------------------------------------------------------------------

    def _parseHeader(self, header):
        """Fuzzy node header contains brain node type.
        """
        formatting = "fuzzy %s"
        (self.type,) = sscanf(header, formatting)

#------------------------------------------------------------------------------
# class ActionBlock
#------------------------------------------------------------------------------

class ActionBlock(Block):
    """Defines an agent mocap animation.
    """

    #--------------------------------------------------------------------------
    # statics
    #--------------------------------------------------------------------------

    _sBlockFormatting = [
    ]

    #--------------------------------------------------------------------------
    # methods
    #--------------------------------------------------------------------------

    def __init__(self, block):
        """Initialize self with agent data.
        """
        super(ActionBlock, self).__init__()

        # remove the block header
        header, block = block.partition('\n')[::2]
        self._parseHeader(header)

        # remove indent from block
        block = self._removeIndent(block)

        # save attributes
        self._raw = block

    #--------------------------------------------------------------------------

    def __str__(self):
        header = "action %s" % self.name
        block  = self._raw
        return "%s\n%s\n" % (header, self._addIndent(block))

    #--------------------------------------------------------------------------
    # methods
    #--------------------------------------------------------------------------

    def _parseHeader(self, header):
        """Action block header contains action name.
        """
        formatting = "action %s"
        (self.name,) = sscanf(header, formatting)

#------------------------------------------------------------------------------
# class MotionTreeBlock
#------------------------------------------------------------------------------

class MotionTreeBlock(Block):
    """Defines an agent motion tree.
    """

    #--------------------------------------------------------------------------
    # statics
    #--------------------------------------------------------------------------

    _sBlockFormatting = [
    ]

    #--------------------------------------------------------------------------
    # methods
    #--------------------------------------------------------------------------

    def __init__(self, block):
        """Initialize self with agent data.
        """
        super(MotionTreeBlock, self).__init__()

        # remove the block header
        header, block = block.partition('\n')[::2]
        self._parseHeader(header)

        # remove indent from block
        block = self._removeIndent(block)

        # save attributes
        self._raw = block

    #--------------------------------------------------------------------------

    def __str__(self):
        block  = self._raw
        return "motion tree\n%s\n" % self._addIndent(block)

    #--------------------------------------------------------------------------
    # methods
    #--------------------------------------------------------------------------

    def _parseHeader(self, header):
        """MotionTree block header only contains start tag.
        """
        formatting = "motion tree"
        sscanf(header, formatting)

