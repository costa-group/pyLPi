
from fractions import gcd
from functools import reduce
from ppl import C_Polyhedron as PPL_C_Polyhedron
from ppl import Linear_Expression
from ppl import Variable


class C_Polyhedron:

    def __init__(self, constraints=[], variables=[], constraint_system=None, dim=None):
        """
        Closed Polyhedron

        :param constraints: list of constraints
        :type constraints: `list` of `lpi.Constraint`
        :param variables: list of variables names.
        :type variables: `list` of `string`
        """
        from ppl import Constraint_System
        if constraint_system is not None or dim is not None or isinstance(constraints, Constraint_System):
            raise Exception("Deprecated!")
        self._cons_mode = "int"  # a > b  --> a + 1 >= b
        # self._cons_mode = "rat"  # a > b  --> a >= b
        self._existsPoly = False
        self._updated = True
        self._constraints = [c.normalize(mode=self._cons_mode) for c in constraints]
        self._variables = variables[:]
        self._dimension = len(variables)
        self._poly = None

    def copy(self):
        """
        :returns: a copy of the polyhedron
        """
        return C_Polyhedron(constraints=self.get_constraints(self._variables),
                            variables=self.get_variables())

    def _convert(self, pplitem):
        from lpi import Expression
        from ppl import Generator
        from ppl import point
        if isinstance(pplitem, (Generator, point)):
            exp = Expression(0)
            for i in range(len(self._variables)):
                exp += int(pplitem.coefficient(Variable(i))) * Expression(self._variables[i])
            return exp, int(pplitem.divisor())
        raise Exception("CONVERT NOT IMPLEMENTED")

    @classmethod
    def transform(cls, expression, vars_):
        """
        :param expression:
        :type expression: `lpi.Expression` or `lpi.Constraint`
        """
        if isinstance(expression, list):
            return [cls.transform(e, vars_) for e in expression]

        def toVar(v):
            if v in vars_:
                return Variable(vars_.index(v))
            else:
                raise ValueError("{} is not a variable.".format(v))

        return expression.get(toVar, int, Linear_Expression)

    def _update_constraints(self):
        if self._poly is None and self._updated:
            return
        from lpi import Expression
        vars_ = self._variables

        def parse_cons(c):
            equation = Expression(c.inhomogeneous_term())
            for i in range(self._dimension):
                cf = int(c.coefficient(Variable(i)))
                if cf != 0:
                    equation += cf * Expression(vars_[i])
            if c.is_equality():
                return equation == 0
            else:
                return equation >= 0

        self._constraints = [parse_cons(c) for c in self._poly.constraints()]
        self._updated = True

    def _build_poly(self):
        if self._poly is None:
            from ppl import Constraint_System
            cs = Constraint_System(self.transform(self._constraints, self._variables))
            self._existsPoly = True
            self._poly = PPL_C_Polyhedron(self._dimension)
            self._poly.add_constraints(cs)

    def add_constraint(self, constraint):
        """Adds a constraint.

        :param constraint: Constraint to be added.
        :type constraint: `lpi.Constraint`
        """
        self.add_constraints([constraint])

    def add_constraints(self, constraints):
        """Adds a list of constraints.

        :param constraints: List to be added.
        :type constraints: `list` of `lpi.Constraint`
        """
        cs = [c.normalize(mode=self._cons_mode) for c in constraints]
        self._constraints += cs
        if self._existsPoly:
            self._poly.add_constraints(self.transform(cs, self._variables))

    def get_dimension(self):
        """Returns the dimension of the vector space enclosing
        """
        return int(self._dimension)

    def get_variables(self):
        """Returns the list of variables of the polyhedron.
        """
        return self._variables[:]

    def get_constraints(self, variables=None):
        """Returns the list of constraints.

        :param variables: Optional parameter to rename variables
        :type variables: `listp` of `string`
        """
        self._update_constraints()
        if variables is None:
            return self._constraints
        else:
            return [c.renamed(self._variables, variables)
                    for c in self._constraints]

    def get_point(self):
        self._build_poly()
        if self._poly.is_empty():
            return None, 1
        q = PPL_C_Polyhedron(self._poly)
        x = Variable(0)
        e = Linear_Expression(x)
        q.add_constraint(x >= 0)
        r = q.minimize(e)
        if r['bounded']:
            return self._convert(r['generator'])
        q = PPL_C_Polyhedron(self._poly)
        q.add_constraint(x <= 0)
        r = q.maximize(e)
        return self._convert(r['generator'])

    def get_generators(self):
        self._build_poly()
        # TODO: Transform results
        return self._poly.generators()

    def contains(self, other):
        self._build_poly()
        other._build_poly()
        return self._poly.contains(other._poly)

    def contains_integer_point(self):
        self._build_poly()
        return self._poly.contains_integer_point()

    def get_relative_interior_point(self, variables=None):
        self._build_poly()
        if self.is_empty():
            return None, 1
        dimension = self.get_dimension()
        vars_ = [str(v) for v in self._variables]
        if variables is None:
            vs = [i for i in range(dimension)]
        else:
            vs = []
            for v in variables:
                try:
                    vs.append(vars_.index(str(v)))
                except ValueError:
                    raise ValueError("Variable ({}) is not on this polyhedron.".format(v))
        q = PPL_C_Polyhedron(self._poly)

        from fractions import Fraction
        from math import ceil
        from math import floor

        coeffs = [Fraction(0, 1) for __ in range(dimension)]
        for i in vs:
            li = Variable(i)
            exp_li = Linear_Expression(li)
            # minimize li with respect q
            left = q.minimize(exp_li)
            # maximize li with respect q
            right = q.maximize(exp_li)
            if not left['bounded'] and not right['bounded']:
                ci = Fraction(0, 1)
            elif not left['bounded']:
                lim_r = right['sup_n'] / (1.0 * right['sup_d'])
                if lim_r >= 0:
                    ci = Fraction(0, 1)
                else:
                    ci = Fraction(ceil(lim_r - 1.0), 1)
            elif not right['bounded']:
                lim_l = left['inf_n'] / (1.0 * left['inf_d'])
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
                    mid = (lim_r - lim_l) / 2 + lim_l
                    aux1 = ceil(mid)
                    aux2 = floor(mid)
                    if aux1 < lim_r:  # aux1 is in (a, b) ??
                        ci = Fraction(aux1, 1)
                    elif lim_l < aux2:  # aux2 is in (a, b) ??
                        ci = Fraction(aux2, 1)
                    else:  # no integers in (a, b)
                        ci = mid

            coeffs[i] = ci
            q.add_constraint(li * ci.denominator == ci.numerator)
        # build POINT
        divisor = reduce(gcd, [f.denominator for f in coeffs])
        from lpi import Expression
        exp = Expression(0)
        for v in variables:
            i = vars_.index(v)
            ci = int(coeffs[i].numerator) * (divisor / int(coeffs[i].denominator))
            exp += ci * Expression(v)
        return exp, divisor

    def minimize(self, expression):
        self._build_poly()
        result = self._poly.minimize(self.transform(expression, self._variables))
        answer = dict(result)
        if result['bounded']:
            answer['generator'] = self._convert(result["generator"])
        return answer

    def maximize(self, expression):
        self._build_poly()
        result = self._poly.maximize(self.transform(expression, self._variables))
        answer = dict(result)
        if result['bounded']:
            answer['generator'] = self._convert(result["generator"])
        return answer

    def is_empty(self):
        self._build_poly()
        return self._poly.is_empty()

    def is_disjoint_from(self, other):
        self._build_poly()
        other._build_poly()
        return self._poly.is_disjoint_from(other._poly)

    def minimized_constraints(self):
        self._build_poly()
        self._poly.minimized_constraints()
        self._updated = False

    def upper_bound_assign(self, other):
        self._build_poly()
        other._build_poly()
        self._poly.upper_bound_assign(other._poly)
        self._updated = False

    def poly_hull_assign(self, other):
        self._build_poly()
        other._build_poly()
        self._poly.poly_hull_assign(other._poly)
        self._updated = False

    def widening_assign(self, other, tp=0):
        self._build_poly()
        other._build_poly()
        self._poly.widening_assign(other._poly, tp)
        self._updated = False

    def extrapolation_assign(self, other, cs, tp=0, limited=False):
        self._build_poly()
        other._build_poly()
        from ppl import Constraint_System
        if isinstance(cs, Constraint_System):
            raise Exception("Deprecated!")
        cons = Constraint_System(self.transform(cs, self._variables))
        if limited:
            self._poly.limited_H79_extrapolation_assign(other._poly, cons, tp)
        else:
            self._poly.bounded_H79_extrapolation_assign(other._poly, cons, tp)
        self._updated = False

    def add_dimensions(self, dim, variables):
        if len(variables) != dim:
            raise ValueError("The number of variables must be the same as the number of dimensions you want to add.")
        for v in variables:
            if v in self._variables:
                raise ValueError("Polyhedron cann't be extended with variable {} because is already in it.".format(v))
        self._variables += variables
        self._dimension += dim

    def remove_dimensions(self, var_set):
        self._build_poly()
        from ppl import Variables_Set
        var_s = Variables_Set()
        for v in var_set:
            var_s.insert(Variable(self._variables.index(v)))
        self._poly.remove_space_dimensions(var_s)
        self._dimension = self._poly.space_dimension()
        self._variables = [v for v in self._variables if v not in var_set]
        self._updated = False

    def project(self, var_set):
        self._build_poly()
        from ppl import Variables_Set
        if isinstance(var_set, (Variables_Set, Variable, int)):
            raise Exception("Deprecated!")
        vs = Variables_Set()
        if isinstance(var_set, str):
            var_set = [var_set]
        do_it = False
        for i in range(self._dimension):
            if self._variables[i] not in var_set:
                do_it = True
                vs.insert(Variable(i))
        p = self.copy()
        if do_it:
            p._build_poly()
            p._poly.remove_space_dimensions(vs)
            p._dimension = p._poly.space_dimension()
            p._variables = var_set[:]
            p._updated = False
        return p

    def expand_space_dimension(self, var, m):
        self._build_poly()
        v = Variable(self._variables.index(var))
        self._poly.expand_space_dimension(v, m)
        self._dimension = self._poly.space_dimension()
        self._updated = False

    def intersection_assign(self, other):
        self._build_poly()
        other._build_poly()
        self._poly.intersection_assign(other._poly)
        self._updated = False

    def unconstraint(self, var):
        self._build_poly()
        v = Variable(self._variables.index(var))
        self._poly.unconstrain(v)
        self._updated = False

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

    def renamed(self, old_names, new_names):
        self._update_constraints()
        ncs = [c.renamed(old_names, new_names) for c in self._constraints]
        return C_Polyhedron(constraints=ncs, variables=new_names)

    def toString(self, eq_symb="==", geq_symb=">="):
        """Returns an string representing the polyhedron

        :param eq_symb: symbol for equalities
        :type eq_symb: `string`
        :param geq_symb: symbol for inequalities of type greater than or equal to.
        :type geq_symb: `string`
        """
        self._update_constraints()
        return [c.toString(lambda x: x, int, eq_symb=eq_symb, geq_symb=geq_symb)
                for c in self._constraints]

    def __repr__(self):
        cs = self.toString()
        if len(cs) == 0:
            return "{}"
        return "{\n\t" + ",\n\t".join(cs) + "\n}"
