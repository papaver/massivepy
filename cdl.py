#------------------------------------------------------------------------------
# cdl.py - Massive agent file. (.cdl)
#------------------------------------------------------------------------------

import re

from scanf import sscanf
from scanf import IncompleteCaptureError

from cdl_blocks import *

#------------------------------------------------------------------------------
# class CdlFile
#------------------------------------------------------------------------------

class CdlFile(object):
    """Massive agent file.
    """

    #--------------------------------------------------------------------------
    # statics
    #--------------------------------------------------------------------------

    _sVersionFormatting = "# CDL created with massive v%s"
    _sUnitsFormatting   = "units %s"

    #--------------------------------------------------------------------------
    # methods
    #--------------------------------------------------------------------------

    def __init__(self, path):
        """Open file at path, read contents into memory, and close.
        """
        super(CdlFile, self).__init__()

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
        with open(path, 'w') as cdl_file:

            # version
            version = CdlFile._sVersionFormatting % self.version
            cdl_file.write("%s\n\n" % version)

            # units
            units = CdlFile._sUnitsFormatting % self.units
            cdl_file.write("%s\n\n" % units)

            # write object block to file
            cdl_file.write("%s" % str(self.object_block))

    #--------------------------------------------------------------------------
    # helper methods
    #--------------------------------------------------------------------------

    def _read(self, path):
        """Parses the contents of the file at the given path.
        """

        # parse the contents of the file ('U' deals with newlines cross-platformly)
        with open(path, 'rU') as agent_file:
            scene = agent_file.read()

            # parse out the inital comment
            version, scene = scene.partition('\n')[::2]
            self.version   = sscanf(version, CdlFile._sVersionFormatting)

            # eat single newline
            scene = scene.partition('\n')[2]

            # parse out the units specifier
            units, scene = scene.partition('\n')[::2]
            self.units   = sscanf(units, CdlFile._sUnitsFormatting)

            # eat single newline
            scene = scene.partition('\n')[2]

            # parse object block
            self.object_block = ObjectBlock(scene)
