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
# common.py - Common objects found in Massive files.
#------------------------------------------------------------------------------

#------------------------------------------------------------------------------
# class Variable
#------------------------------------------------------------------------------

class Variable(object):
    """Massive agent varaible.
    """

    #--------------------------------------------------------------------------
    # methods
    #--------------------------------------------------------------------------

    def __init__(self, name):
        self.name    = name;
        self.default = 0.0
        self.min     = 0.0
        self.max     = 1.0
        self.expr    = ""

    #--------------------------------------------------------------------------

    def __init__(self, name, default, min, max, expr=""):
        self.name    = name
        self.default = default
        self.max     = max
        self.min     = min
        self.expr    = expr

    #--------------------------------------------------------------------------

    def __str__(self):
        if (self.expr == ""):
            data = (self.name, self.default, self.min, self.max)
            return "variable %s %f [%f %f]" % data
        else:
            data = (self.name, self.default, self.min, self.max, self.expr)
            return "variable %s %f [%f %f] %s" % data

