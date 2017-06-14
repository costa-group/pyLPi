from ppl import Variable
from ppl import Linear_Expression
from ppl import Constraint
from ppl import Constraint_System
from ppl import Polyhedron
from ppl import C_Polyhedron


class LPPolyhedron:

    _poly = None

    def __init__(self, constraint_system, dim=-1):
	if constraint_system is None:
            constraint_system = Constraint_System()
	cdim = constraint_system.space_dimension()
        if dim < cdim:
            dim = cdim

	self._poly = C_Polyhedron(dim)
        self._poly.add_constraints(constraint_system)

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
        if self._poly.is_empty():
            return None
        q = C_Polyhedron(self._poly)
        x = Variable(0)
        e = Linear_Expression(x)
        q.add_constraint(x >= 0)
        r = q.minimize(e)

        if r['bounded']:
            return r['generator']

        q = C_Polyhedron(self._poly)
        q.add_constraint(x <= 0)
        r = q.maximize(e)

        return r['generator']

    def get_generators(self):
        return self._poly.get_generators()

    def contains_integer_point(self):
        return self._poly.contains_integer_poin()

    def get_integer_point(self):
        pass

    def get_relative_interior_point():
        pass

    def minimize(self, expression):
        return self._poly.minimize(expression)

    def maximize(self, expression):
        return self._poly.maximize(expression)

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
