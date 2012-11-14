#------------------------------------------------------------------------------
# mas.py - Massive scene file. (.mas)
#------------------------------------------------------------------------------

import re

from scanf import sscanf
from scanf import IncompleteCaptureError

from mas_blocks import *

#------------------------------------------------------------------------------
# class MasFile
#------------------------------------------------------------------------------

class MasFile(object):
    """Massive scene file.
    """

    #--------------------------------------------------------------------------
    # statics
    #--------------------------------------------------------------------------

    _sVersionFormatting = "# Massive %s setup file."
    _sUnitsFormatting   = "units %s"

    _sBlocks = [
        ("Display options", DisplayOptionsBlock),
        ("Terrains",        TerrainsBlock),
        ("Cameras",         CamerasBlock),
        ("Lighting",        LightingBlock),
        ("Renders",         RendersBlock),
        ("Dynamics",        DynamicsBlock),
        ("Flow",            FlowBlock),
        ("Lane",            LaneBlock),
        ("Sims",            SimsBlock),
        ("Place",           PlaceBlock)
    ]

    #--------------------------------------------------------------------------
    # methods
    #--------------------------------------------------------------------------

    def __init__(self, path):
        """Open file at path, read contents into memory, and close.
        """
        super(MasFile, self).__init__()

        # save path to file
        self._path = path

        # read in file contents
        self._read(path)

    #--------------------------------------------------------------------------

    def write(self, path=None):
        """Write the file to the given path.
        """

        # use read path if path not specified
        if path == None:
            path = self._path

        # open the file and write out scene
        with open(path, 'w') as mas_file:

            # version
            version = MasFile._sVersionFormatting % self.version
            mas_file.write("%s\n" % version)

            # units 
            units = MasFile._sUnitsFormatting % self.units
            mas_file.write("%s" % units)

            # write out all of the available blocks
            for block_name, cls in MasFile._sBlocks:

                # get blocks attribute name
                attribute_name = self._getAttrbuteName(block_name)
                
                # skip empty blocks
                block = getattr(self, attribute_name)
                if block == None:
                    continue

                # write block to file
                mas_file.write("\n\n%s" % str(block))

    #--------------------------------------------------------------------------
    # helper methods
    #--------------------------------------------------------------------------

    def _getAttrbuteName(self, block_name):
        return "%s_block" % block_name.replace(' ', '_').lower()

    #--------------------------------------------------------------------------

    def _read(self, path):
        """Parses the contents of the file at the given path.
        """

        # parse the contents of the file ('U' deals with newlines cross-platformly)
        with open(path, 'rU') as scene_file:
            scene = scene_file.read()

            # parse out the inital comment
            version, scene = scene.partition('\n')[::2]
            self.version   = sscanf(version, MasFile._sVersionFormatting);
        
            # parse out the units specifier
            units, scene = scene.partition('\n')[::2]
            self.units   = sscanf(units, MasFile._sUnitsFormatting);

            # read all of the available blocks
            for block_name, cls in MasFile._sBlocks:

                # extract the block from the file
                block, scene = self._extractBlock(block_name, scene)

                # get blocks attribute name
                attribute_name = self._getAttrbuteName(block_name)

                # set attribute with block
                if block:
                    setattr(self, attribute_name, cls(block))
                else:
                    setattr(self, attribute_name, None)

    #--------------------------------------------------------------------------

    def _extractBlock(self, block_name, scene):
        """Parses a block of data from the scene data.  
        """

        # matches entire text to allow extracting block from scene data
        pattern = "(?P<start>.*)%s\n(?P<block>.*)%s\n?(?P<end>.*)"

        # use start/end tags for the block extraction
        block_end     = "End %s" % block_name.lower()
        block_pattern = pattern % (block_name, block_end)

        # extract block from scene data
        match = re.match(block_pattern, scene, re.S)
        if match:

            # remove indent from block
            block = re.compile(r"^    ", re.M).sub("", match.group('block'))

            # compile rest of scene data
            rest  = match.group('start') + match.group('end')

            return (block, rest)

        # block not found
        else:
            return (None, scene)

