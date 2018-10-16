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
        self._build_poly()
        return self._poly.space_dimension()

    def get_constraints(self, use_z3=False):
        self._build_poly()
        cons = self._poly.constraints()
        if use_z3:
            return _constraints_to_z3(cons)
        else:
            return cons

    def get_point(self, use_z3=False):
        if use_z3:
            from z3 import Real
            from z3 import Solver
            from z3 import sat
            z3cons = _constraints_to_z3(self._constraints)
            s = Solver()
            for c in z3cons:
                s.insert(c)
            if s.check() == sat:
                # build POINT
                coeffs = s.model()

                exp = Linear_Expression(0)
                divisor = _lcm([int(str(coeffs[f].denominator()))
                                for f in coeffs])

                for i in range(self._dimension):
                    if coeffs[Real(str(i))] is None:
                        exp += Variable(i) * 0
                    else:
                        v = Real(str(i))
                        ci = int(str(coeffs[v].numerator()))
                        ci *= (divisor / int(str(coeffs[v].denominator())))
                        exp += Variable(i) * ci

                return point(exp, divisor)
            else:
                return None
        self._build_poly()
        if self._poly.is_empty():
            return None
        q = PPL_C_Polyhedron(self._poly)
        x = Variable(0)
        e = Linear_Expression(x)
        q.add_constraint(x >= 0)
        r = q.minimize(e)

        if r['bounded']:
            return r['generator']

        q = PPL_C_Polyhedron(self._poly)
        q.add_constraint(x <= 0)
        r = q.maximize(e)

        return r['generator']

    def get_generators(self):
        self._build_poly()
        return self._poly.get_generators()

    def contains(self, other):
        self._build_poly()
        other._build_poly()
        return self._poly.contains(other._poly)

    def contains_integer_point(self):
        self._build_poly()
        return self._poly.contains_integer_point()

    def get_integer_point(self):
        pass

    def get_relative_interior_point(self, variables=None):
        self._build_poly()
        if self._poly.is_empty():
            return None
        dimension = self.get_dimension()
        if variables is None:
            variables = [i for i in range(dimension)]
        for v in variables:
            if v < 0 or v >= dimension:
                raise Exception("Wrong dimension")
        q = PPL_C_Polyhedron(self._poly)

        from fractions import Fraction
        from math import ceil
        from math import floor

        coeffs = [Fraction(0, 1) for _ in range(dimension)]
        for i in variables:
            li = Variable(i)
            exp_li = Linear_Expression(li)
            # minimize li with respect q
            left = q.minimize(exp_li)
            # maximize li with respect q
            right = q.maximize(exp_li)
            if not left['bounded'] and not right['bounded']:
                ci = Fraction(0, 1)
            elif not left['bounded']:
                lim_r = right['sup_n'] / (1.0*right['sup_d'])
                if lim_r >= 0:
                    ci = Fraction(0, 1)
                else:
                    ci = Fraction(ceil(lim_r - 1.0), 1)
            elif not right['bounded']:
                lim_l = left['inf_n'] / (1.0*left['inf_d'])
                if lim_l <= 0:
                    ci = Fraction(0, 1)
                else:
                    ci = Fraction(floor(lim_l + 1.0), 1)
            else:
                lim_r = Fraction(right['sup_n'], right['sup_d'])
                lim_l = Fraction(left['inf_n'], left['inf_d'])
                if lim_r == lim_l:
                    ci = lim_r
                elif lim_l < 0 and lim_r > 0:
                    ci = Fraction(0, 1)
                else:
                    mid = (lim_r-lim_l) / 2 + lim_l
                    aux1 = ceil(mid)
                    aux2 = floor(mid)
                    if aux1 < lim_r:  # aux1 is in (a, b) ??
                        ci = Fraction(aux1, 1)
                    elif lim_l < aux2:  # aux2 is in (a, b) ??
                        ci = Fraction(aux2, 1)
                    else:  # no integers in (a, b)
                        ci = mid

            coeffs[i] = ci
            q.add_constraint(li*ci.denominator == ci.numerator)

        # build POINT
        exp = Linear_Expression(0)
        divisor = reduce(gcd, [f.denominator for f in coeffs])
        for v in variables:
            ci = coeffs[v].numerator * (divisor / coeffs[v].denominator)
            exp += Variable(v) * ci

        return point(exp, divisor)

    def minimize(self, expression):
        self._build_poly()
        return self._poly.minimize(expression)

    def maximize(self, expression):
        self._build_poly()
        return self._poly.maximize(expression)

    def is_empty(self):
        self._build_poly()
        return self._poly.is_empty()

    def is_implied(self, constraint):
        pass

    def is_disjoint_from(self, polyhedron):
        self._build_poly()
        return self._poly.is_disjoint_from(polyhedron)

    def __repr__(self):
        self._build_poly()
        return self._poly.__repr__()

    def int_minimize(self, something):
        pass

    def int_maximize(self, something):
        pass

    def is_bounded(self):
        # return self._poly.is_bounded()
        pass

    def minimized_constraints(self):
        self._build_poly()
        self._poly.minimized_constraints()
        self._constraints = self._poly.constraints()

    def upper_bound_assign(self, other):
        self._build_poly()
        other._build_poly()
        self._poly.upper_bound_assign(other._poly)
        self._constraints = self._poly.constraints()

    def poly_hull_assign(self, other):
        self._build_poly()
        other._build_poly()
        self._poly.poly_hull_assign(other._poly)
        self._constraints = self._poly.constraints()

    def widening_assign(self, other, tp=0):
        self._build_poly()
        other._build_poly()
        self._poly.widening_assign(other._poly, tp)
        self._constraints = self._poly.constraints()

    def extrapolation_assign(self, other, cs, tp=0, limited=False):
        self._build_poly()
        other._build_poly()
        if not isinstance(cs, (Constraint_System)):
            raise ValueError("cs argument must be a Constraint System")
        if limited:
            self._poly.limited_H79_extrapolation_assign(other._poly, cs, tp)
        else:
            self._poly.bounded_H79_extrapolation_assign(other._poly, cs, tp)
        self._constraints = self._poly.constraints()

    def add_dimensions(self, dim):
        self._build_poly()
        self._poly.add_space_dimensions_and_embed(dim)
        self._dimension = self._poly.space_dimension()
        self._constraints = self._poly.constraints()

    def remove_dimensions(self, var_set):
        self._build_poly()
        self._poly.remove_space_dimensions(var_set)
        self._dimension = self._poly.space_dimension()
        self._constraints = self._poly.constraints()
        
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

    def __le__(self, other):
        self._build_poly()
        other._build_poly()
        return other._poly.contains(self._poly)

    def toString(self, vars_name=None, eq_symb="==", geq_symb=">="):
        cs = self._constraints
        dim = self._dimension
        if vars_name is None:
            vars_name = []
        for i in range(len(vars_name), dim):
            vars_name.append("x"+str(i))
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
