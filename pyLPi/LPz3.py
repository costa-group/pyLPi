from ppl import Variable
from ppl import Linear_Expression
from ppl import Constraint
from ppl import Constraint_System
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

    def add_constraint_system(self, constraint_system):
        pass
        
    def get_dimension(self):
        pass

    def get_constraints(self):
        pass

    def get_point(self):
        pass
    
    def get_generators(self):
        pass

    def contains_integer_point(self):
        pass

    def get_integer_point(self):
        pass

    def get_relative_interior_point():
        pass

    def minimize(self):
        pass

    def maximize(self):
        pass

    def is_empty(self):
        pass

    def is_implied(self, constraint):
        pass

    def is_disjoint_from(self, polyhedron):
        pass

    def __repr__(self):
        pass

    def int_minimize(self, something):
        pass

    def int_maximize(self, something):
        pass

    def is_bounded(self):
        pass

    def minimize_constraint_system():
        pass
