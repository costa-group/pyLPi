from ppl import Variable
from ppl import Linear_Expression
from ppl import Constraint
from ppl import Constraint_System
from ppl import Polyhedron
from ppl import C_Polyhedron


class LPPolyhedron:

    _poly = None

    def __init__(self, constraint_system, dim=-1):
        if dim < 0:
            dim = constraint_system.space_dimension()
        self._poly = C_Polyhedron(constraint_system, dim)

    def add_constraint(self, constraint):
        self._poly.add_constraint(constraint)

    def add_constraints(self, constraints):
        self._poly.add_constraints(constraints)

    def add_constraint_system(self, constraint_system):
        self._poly.add_constraint_system(constraint_system)
        
    def get_dimension(self):
        return self._poly.space_dimension()

    def get_constraints(self):
        return self._poly.constraints()

    def get_point(self):
        pass
    
    def get_generators(self):
        return self._poly.get_generators()

    def contains_integer_point(self):
        return self._poly.contains_integer_poin()

    def get_integer_point(self):
        pass

    def get_relative_interior_point():
        pass

    def minimize(self):
        pass

    def maximize(self):
        pass

    def is_empty(self):
        return self._poly.is_empty()

    def is_implied(self, constraint):
        pass

    def is_disjoint_from(self, polyhedron):
        return self._poly.is_disjoint_from(polyhedron)

    def __repr__(self):
        return self._poly.__repr__()

    def int_minimize(self, something):
        pass

    def int_maximize(self, something):
        pass

    def is_bounded(self):
        # return self._poly.is_bounded()
        pass

    def minimize_constraint_system():
        pass
