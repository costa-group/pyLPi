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
        self._init_poly()
        return self._poly.space_dimension()

    def get_constraints(self):
        self._init_poly()
        return self._poly.constraints()

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

    def get_relative_interior_point(self, dimension=None):
        self._init_poly()
        if self._poly.is_empty():
            return None
        if dimension is None or dimension > self.get_dimension():
            dimension = self.get_dimension()
        q = C_Polyhedron(self._poly)
        point = [0]
        for i in range(1, dimension):
            ci = None
            li = Variable(i)
            exp_li = Linear_Expression(li)
            # minimize li with respect q
            ra = q.minimize(exp_li)
            # maximize li with respect q
            rb = q.maximize(exp_li)
            if not ra['bounded'] and not rb['bounded']:
                ci = 0
            elif not ra['bounded']:
                b = rb['generator'].coefficient(li)
                ci = 0 if (b > 0) else ceil(b - 1.0)
            elif not rb['bounded']:
                a = ra['generator'].coefficient(li)
                ci = 0 if (a < 0) else floor(a + 1.0)
            else:
                a = ra['generator'].coefficient(li)
                b = rb['generator'].coefficient(li)
                if a == b:
                    ci = a
                elif a < 0 and b > 0:
                    ci = 0
                else:
                    mid = (b-a) / 2.0 + a
                    aux1 = ceil(mid)
                    aux2 = floor(mid)
                    if aux1 < b:  # aux1 is in (a, b) ??
                        ci = aux1
                    elif a < aux2:  # aux2 is in (a, b) ??
                        ci = aux2
                    else:  # no integers in (a, b)
                        ci = mid

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
