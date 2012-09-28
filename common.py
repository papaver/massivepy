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

