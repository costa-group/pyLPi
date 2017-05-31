from ppl import Variable
from ppl import Linear_Expression
from ppl import Constraint
from ppl import Constrain_System
import z3


class LPPolyhedron:

    def __init__(self, constraint_system, dim=-1):
        if dim < 0:
            dim = constraint_system.space_dimension()
        pass

    def add_constraint(self, constraint):
        pass

    def add_constraints(self, constraints):
        pass

    def contains_integer_point(self):
        pass

    def is_disjoint_from(self, polyhedron):
        pass

    def is_empty(self):
        pass

    def constraints(self):
        pass

    def get_point(self):
        pass

    def minimize(self):
        pass

    def maximize(self):
        pass

