EMPTY_SET_RE = 0
EMPTY_STRING_RE = 1
SYMBOL_RE = 2
STAR_RE = 3
CONCATENATION_RE = 4
ALTERNATION_RE = 5

_SIMPLE_TYPES_RE = {EMPTY_SET_RE, EMPTY_STRING_RE, SYMBOL_RE}


def str_paranthesize(parent_type, re):
    if parent_type > re.type or parent_type == re.type and parent_type != STAR_RE:
        return str(re)
    else:
        return "({!s})".format(str(re))


class RegularExpression(object):
    """Model a Regular Expression TDA

    The member "type" is always available, indicating the type of the
    RegularExpression. Its value dictates which other members (if any) are
    defined:

        - EMPTY_SET_RE:
        - EMPTY_STRING_RE:
        - SYMBOL_RE: "SYMBOL_RE" is the SYMBOL_RE
        - STAR_RE: "lhs" is the RegularExpression
        - CONCATENATION_RE: "lhs" and "rhs" are the RegularExpressions
        - ALTERNATION_RE: "lhs" and "rhs" are the RegularExpressions

    """
    def __init__(self, type, obj1=None, obj2=None):
        """Create a Regular Expression

        The value of the "type" parameter influences the interpretation of the
        other two paramters:

            - EMPTY_SET_RE: obj1 and obj2 are unused
            - EMPTY_STRING_RE: obj1 and obj2 are unused
            - SYMBOL_RE: obj1 should be a SYMBOL_RE; obj2 is unused
            - STAR_RE: obj1 should be a RegularExpression; obj2 is unused
            - CONCATENATION_RE: obj1 and obj2 should be RegularExpressions
            - ALTERNATION_RE: obj1 and obj2 should be RegularExpressions

        """
        self.type = type
        if type in _SIMPLE_TYPES_RE:
            if type == SYMBOL_RE:
                assert obj1 is not None
                self.symbol = obj1
        else:
            assert isinstance(obj1, RegularExpression)
            self.lhs = obj1
            if type == CONCATENATION_RE or type == ALTERNATION_RE:
                assert isinstance(obj2, RegularExpression)
                self.rhs = obj2

    def __str__(self):
        if self.type == EMPTY_SET_RE:
            return "∅"
        elif self.type == EMPTY_STRING_RE:
            return "ε"
        elif self.type == SYMBOL_RE:
            return str(self.symbol)
        elif self.type == CONCATENATION_RE:
            slhs = str_paranthesize(self.type, self.lhs)
            srhs = str_paranthesize(self.type, self.rhs)
            return slhs + srhs
        elif self.type == ALTERNATION_RE:
            slhs = str_paranthesize(self.type, self.lhs)
            srhs = str_paranthesize(self.type, self.rhs)
            return slhs + "|" + srhs
        elif self.type == STAR_RE:
            slhs = str_paranthesize(self.type, self.lhs)
            return slhs + "*"
        else:
            return ""

    def __mul__(self, rhs):
        """CONCATENATION_RE"""
        if isinstance(rhs, str) and len(rhs) == 1:
            rhs = RegularExpression(SYMBOL_RE, rhs)

        assert isinstance(rhs, RegularExpression)
        return RegularExpression(CONCATENATION_RE, self, rhs)

    __rmul__ = __mul__

    def __or__(self, rhs):
        """Alteration"""
        if isinstance(rhs, str) and len(rhs) == 1:
            rhs = RegularExpression(SYMBOL_RE, rhs)

        assert isinstance(rhs, RegularExpression)
        return RegularExpression(ALTERNATION_RE, self, rhs)

    __ror__ = __or__

    def STAR_RE(self):
        return RegularExpression(STAR_RE, self)

    def is_simple_type(self):
        return self.type in _SIMPLE_TYPES_RE
