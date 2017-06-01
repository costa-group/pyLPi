from ppl import Variable, Linear_Expression, Constraint
# from RankConfig import getLPMod
import LPppl

class C_Polyhedron:
    _poly = None
    def __init__(self, cons, dim=-1[,lplib=None]):
        if lplib is None:
            lplib = get_LP_lib_name()
        if lplib == "ppl":
        
        P = getLPPolyhedronClass()
        _poly = P(cons,dim)

        _poly = getLPPolyhedron(cons,dim)
