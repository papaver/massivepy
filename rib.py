#------------------------------------------------------------------------------
# rib.py - Massive rib file. (.rib)
#------------------------------------------------------------------------------

from rib_blocks import *

#------------------------------------------------------------------------------
# class RibFile
#------------------------------------------------------------------------------

class RibFile(object):
    """Massive rib file.
    """

    #--------------------------------------------------------------------------
    # statics
    #--------------------------------------------------------------------------

    #--------------------------------------------------------------------------
    # methods
    #--------------------------------------------------------------------------

    def __init__(self, path):
        """Open file at path, read contents into memory, and close.
        """
        super(RibFile, self).__init__()

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

        # open the file and write out rib
        with open(path, 'w') as rib_file:
            rib_file.write("\n".join(map(str, self.ants)))
            rib_file.write("\n")

    #--------------------------------------------------------------------------
    # helper methods
    #--------------------------------------------------------------------------

    def _read(self, path):
        """Parses the contents of the file at the given path.
        """

        # parse the contents of the file ('U' deals with newlines cross-platformly)
        with open(path, 'rU') as rib_file:
            entries = rib_file.readlines()

            # read all of the available ants
            self.ants = []
            for entry in entries:
                ant = AntBlock(entry)
                self.ants.append(ant)

