from math import ceil
from math import floor
from ppl import Variable
from ppl import Linear_Expression
from ppl import Constraint
from ppl import Constraint_System
from ppl import Polyhedron
from ppl import C_Polyhedron


class LPPolyhedron:

    _existsPoly = False
    _poly = None
    _constraints = None
    _dimension = 0

    def __init__(self, constraint_system, dim=-1):
        if constraint_system is None:
            constraint_system = Constraint_System()
        cdim = constraint_system.space_dimension()
        if dim < cdim:
            dim = cdim

        self._existsPoly = False
        self._constraints = constraint_system
        self._dimension = dim

    def _init_poly(self):
        if self._poly is None:
            self._existsPoly = True
            self._poly = C_Polyhedron(self._dimension)
            self._poly.add_constraints(self._constraints)

    def add_constraint(self, constraint):
        if self._existsPoly:
            self._poly.add_constraint(constraint)
        self._constraints.insert(constraint)

    def add_constraints(self, constraints):
        if self._existsPoly:
            self._poly.add_constraints(constraints)
        for c in constraints:
            self._constraints.insert(c)

    def add_constraint_system(self, constraint_system):
        if self._existsPoly:
            self._poly.add_constraint_system(constraint_system)
        new_constraints = [c for c in constraint_system]
        for c in new_constraints:
            self._constraints.insert(c)

    def get_dimension(self):
        if self._existsPoly:
            return self._poly.space_dimension()
        return self._dimension

    def get_constraints(self):
        if self._existsPoly:
            return self._poly.constraints()
        return [c for c in self._constraints]

    def get_point(self):
        self._init_poly()
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
        self._init_poly()
        return self._poly.get_generators()

    def contains_integer_point(self):
        self._init_poly()
        return self._poly.contains_integer_point()

    def get_integer_point(self):
        pass

    def get_relative_interior_point(self):
        self._init_poly()
        if self._poly.is_empty():
            return None
        q = C_Polyhedron(self._poly)
        point = [0]
        for i in range(1, self._dimension):
            ci = None
            li = Variable(i)
            exp_li = Linear_Expression(li)
            # minimize li with respect q
            ra = q.minimize(exp_li)
            if ra['bounded']:
                a = ra['generator'].coefficient(li)
            else:
                a = None  # a = -Inf

            # maximize li with respect q
            rb = q.maximize(exp_li)
            if rb['bounded']:
                b = rb['generator'].coefficient(li)
                if a is None:  # (-inf, b) is equivalent to (b-N, b)
                    a = b - 10
            else:
                if a is None:  # (-inf, inf) is equivalent to (-N, N)
                    a = -5
                b = a + 10  # (a, inf) is equivalent to (a, a+N)

            # select ci
            if a == b:
                ci = a
            elif a < 0 and b > 0:
                ci = 0
            else:
                aux1 = ceil(a+1e-12)   # smallest integer greater than a
                aux2 = floor(b-1e-12)  # biggest integer lower than b
                if aux1 < b:  # aux1 is in (a, b) ??
                    ci = aux1
                elif a < aux2:  # aux2 is in (a, b) ??
                    ci = aux2
                else:  # no integers in (a, b)
                    ci = (b-a) / 2.0 + a

            point.append(ci)
            q.add_constraint(li == ci)
        l0 = Variable(0)
        exp_l0 = Linear_Expression(l0)
        r = q.minimize(exp_l0)
        c0 = r['generator'].coefficient(l0)
        point[0] = c0
        return point

    def minimize(self, expression):
        self._init_poly()
        return self._poly.minimize(expression)

    def maximize(self, expression):
        self._init_poly()
        return self._poly.maximize(expression)

    def is_empty(self):
        self._init_poly()
        return self._poly.is_empty()

    def is_implied(self, constraint):
        pass

    def is_disjoint_from(self, polyhedron):
        self._init_poly()
        return self._poly.is_disjoint_from(polyhedron)

    def __repr__(self):
        self._init_poly()
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
