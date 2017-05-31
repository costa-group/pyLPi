from ppl import Variable
from ppl import Linear_Expression
from ppl import Constraint
from ppl import Constrain_System
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

    def contains_integer_point(self):
        return self._poly.contains_integer_point()

    def is_disjoint_from(self, polyhedron):
        return self._poly.is_disjoint_from(polyhedron)

    def is_empty(self):
        return self._poly.is_empty()

    def constraints(self):
        return self._poly.constraints()

    def get_point(self):
        pass

    def minimize(self):
        pass

    def maximize(self):
        pass
