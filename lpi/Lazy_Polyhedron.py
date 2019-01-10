from fractions import gcd
from functools import reduce
from ppl import C_Polyhedron as PPL_C_Polyhedron
from ppl import Constraint
from ppl import Constraint_System
from ppl import Linear_Expression
from ppl import Variable
from ppl import point


def _lcm(numbers):
    """Return lowest common multiple."""
    def lcm(a, b):
        return (a * b) // gcd(a, b)
    return reduce(lcm, numbers, 1)


def _constraints_to_z3(cons):
    from z3 import Real
    if isinstance(cons, (Constraint_System, list)):
        cs = []
        for c in cons:
            cs.append(_constraints_to_z3(c))
        return cs
    elif isinstance(cons, Constraint):
        equation = cons.inhomogeneous_term()
        dim = cons.space_dimension()
        for i in range(dim):
            cf = cons.coefficient(Variable(i))
            if cf != 0:
                equation += cf * Real(str(i))
        if cons.is_equality():
            return equation == 0
        else:
            return equation >= 0
    else:
        raise ValueError("This method only allows PPL constraints")


class C_Polyhedron:

    _existsPoly = False
    _poly = None
    _constraints = None
    _dimension = 0

    def __init__(self, constraint_system=None, dim=-1):
        if constraint_system is None:
            constraint_system = Constraint_System()
        cdim = constraint_system.space_dimension()
        if dim < cdim:
            dim = cdim

        self._existsPoly = False
        self._constraints = constraint_system
        self._dimension = dim

    def _build_poly(self):
        if self._poly is None:
            self._existsPoly = True
            self._poly = PPL_C_Polyhedron(self._dimension)
            self._poly.add_constraints(self._constraints)

    def is_sat(self):
        from z3 import Solver
        from z3 import sat
        z3cons = _constraints_to_z3(self._constraints)
        s = Solver()
        for c in z3cons:
            s.insert(c)
        return s.check() == sat

    def expand_space_dimension(self, var, m):
        self._build_poly()
        self._poly.expand_space_dimension(var, m)
        self._dimension = self._poly.space_dimension()
        self._constraints = self._poly.constraints()

    def intersection_assign(self, other):
        self._build_poly()
        other._build_poly()
        self._poly.intersection_assign(other._poly)
        self._constraints = self._poly.constraints()

    def unconstraint(self, var):
        self._build_poly()
        self._poly.unconstrain(var)
        self._constraints = self._poly.constraints()

    def __ge__(self, other):
        self._build_poly()
        other._build_poly()
        return self._poly.contains(other._poly)

    def __le__(self, other):
        self._build_poly()
        other._build_poly()
        return other._poly.contains(self._poly)

    def __eq__(self, other):
        if self.get_dimension() != other.get_dimension():
            return False
        self._build_poly()
        other._build_poly()
        return other._poly.contains(self._poly) and self._poly.contains(other._poly)

    def toString(self, vars_name=None, eq_symb="==", geq_symb=">="):
        cs = self._constraints
        dim = self._dimension
        if vars_name is None:
            vars_name = []
        for i in range(len(vars_name), dim):
            vars_name.append("x" + str(i))
        cs_str = []
        for c in cs:
            local_dim = c.space_dimension()
            first = True
            c_str = ""
            for v in range(local_dim):
                coeff = c.coefficient(Variable(v))
                if not first:
                    if coeff > 0:
                        c_str += " + "
                if coeff != 0:
                    first = False
                    if coeff < 0:
                        c_str += " - "
                        coeff = - coeff
                    if coeff != 1:
                        c_str += str(coeff)
                        c_str += " * "
                    c_str += vars_name[v]
            coeff = c.inhomogeneous_term()
            if first or coeff != 0:
                if not first:
                    if coeff >= 0:
                        c_str += " + "
                if coeff < 0:
                    c_str += " - "
                    coeff = - coeff
                c_str += str(coeff)
            if c.is_inequality():
                c_str += " {} ".format(geq_symb)
            else:
                c_str += " {} ".format(eq_symb)
            c_str += "0"
            cs_str.append(c_str)
        return cs_str
