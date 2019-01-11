"""
Created on January 2019

@author: Jesús J. Doménech
"""
from lpi.lp import lpInterface
from ppl import C_Polyhedron as PPL_C_Polyhedron
from ppl import Linear_Expression
from ppl import Constraint_System
from ppl import Variable


class ppllib(lpInterface):
    # TODO: Define lib
    """
    >>> ppllib()
    Traceback (most recent call last):
    ...
    Exception: Can NOT be instantiate.
    """
    _ID = "ppl"

    @staticmethod
    def _transform_polyhedron(polyhedron):
        """
        :param poly:
        :type poly: `lpi.C_Polyhedron`
        """
        # TODO: DOC Return value _transform poly
        vs = polyhedron.get_variables()
        dim = polyhedron.get_dimension()

        def toVar(v):
            if v in vs:
                return Variable(vs.index(v))
            else:
                raise ValueError("{} is not a variable.".format(v))
        p = PPL_C_Polyhedron(Constraint_System([c.get(toVar, int, Linear_Expression)
                                                for c in polyhedron.get_constraints()]))
        return (p, vs, dim)

    @staticmethod
    def _transform_expression(expression):
        """
        :param expression:
        :type expression: `lpi.Expression`
        """
        vs = expression.get_variables()

        def toVar(v):
            if v in vs:
                return Variable(vs.index(v))
            else:
                raise ValueError("{} is not a variable.".format(v))

        exp = expression.get(toVar, int, Linear_Expression)
        return exp, vs

    @staticmethod
    def _convert_into_polyhedron(polyhedron, vars_, dim):
        from lpi import ExprTerm
        from lpi import C_Polyhedron
        d = len(vars_)
        vs = vars_[:]
        if d < dim:
            base = "x"
            num = d
            for i in range(d, dim):
                v = base + str(num)
                while v in vs:
                    num += 1
                    v = base + str(num)
                num += 1
                vs.append(v)

        def parse_cons(c):
            equation = ExprTerm(c.inhomogeneous_term())
            for i in range(dim):
                cf = c.coefficient(Variable(i))
                if cf != 0:
                    equation += cf * ExprTerm(vars_[i])
            if c.is_equality():
                return equation == 0
            else:
                return equation >= 0
        cons = [parse_cons(c) for c in polyhedron.get_constraints()]
        return C_Polyhedron(constraints=cons, variables=vars_)

    @staticmethod
    def get_point(polyhedron):
        """
        """
        # TODO: DOC get_point ppllib
        poly, __, __ = ppllib._transform_polyhedron(polyhedron)
        if poly.is_empty():
            return None
        q = PPL_C_Polyhedron(poly)
        x = Variable(0)
        e = Linear_Expression(x)
        q.add_constraint(x >= 0)
        r = q.minimize(e)

        if r['bounded']:
            return r['generator']

        q = PPL_C_Polyhedron(poly)
        q.add_constraint(x <= 0)
        r = q.maximize(e)
        # TODO: Transform results
        return r['generator']

    @staticmethod
    def get_generators(polyhedron):
        poly, __, __ = ppllib._transform_polyhedron(polyhedron)
        # TODO: transform results
        return poly.generators()

    @staticmethod
    def contains(polyhedron1, polyhedron2):
        poly1, __, __ = ppllib._transform_polyhedron(polyhedron1)
        poly2, __, __ = ppllib._transform_polyhedron(polyhedron2)
        return poly1.contains(poly2)

    @staticmethod
    def contains_integer_point(polyhedron):
        poly, __, __ = ppllib._transform_polyhedron(polyhedron)
        return poly.contains_integer_point()

    @staticmethod
    def get_relative_interior_point(polyhedron, variables=None):
        poly, vars_, dimension = ppllib._transform_polyhedron(polyhedron)
        if poly.is_empty():
            return None, 1
        if variables is None:
            vs = [i for i in range(dimension)]
        else:
            vs = []
            for v in variables:
                try:
                    vs.append(vars_.index(v))
                except ValueError:
                    raise ValueError("Variable ({}) is not on this polyhedron.".format(v))
        q = PPL_C_Polyhedron(poly)

        from fractions import Fraction
        from fractions import gcd
        from math import ceil
        from math import floor
        from functools import reduce

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
        point = []
        for v in range(dimension):
            ci = coeffs[v].numerator * (divisor / coeffs[v].denominator)
            point.append(ci)

        return (point, divisor)

    @staticmethod
    def minimize(polyhedron, expression):
        poly, __, __ = ppllib._transform_polyhedron(polyhedron)
        exp = ppllib._transform_expression(expression)
        # TODO: transform result
        return poly.minimize(exp)

    @staticmethod
    def maximize(polyhedron, expression):
        poly, __, __ = ppllib._transform_polyhedron(polyhedron)
        exp = ppllib._transform_expression(expression)
        # TODO: transform result
        return poly.maximize(exp)

    @staticmethod
    def is_empty(polyhedron):
        poly, __, __ = ppllib._transform_polyhedron(polyhedron)
        return poly.is_empty()

    @staticmethod
    def is_disjoint_from(polyhedron1, polyhedron2):
        poly1, __, __ = ppllib._transform_polyhedron(polyhedron1)
        poly2, __, __ = ppllib._transform_polyhedron(polyhedron2)
        return poly1.is_disjoint_from(poly2)

    @staticmethod
    def minimized_constraints(polyhedron):
        poly, vars_, dimension = ppllib._transform_polyhedron(polyhedron)
        poly.minimized_constraints()
        return ppllib._convert_into_polyhedron(poly, vars_, dimension)

    @staticmethod
    def upper_bound_assign(polyhedron1, polyhedron2):
        poly1, vars_, dimension = ppllib._transform_polyhedron(polyhedron1)
        poly2, __, __ = ppllib._transform_polyhedron(polyhedron2)
        poly1.upper_bound_assign(poly2)
        return ppllib._convert_into_polyhedron(poly1, vars_, dimension)

    @staticmethod
    def poly_hull_assign(polyhedron1, polyhedron2):
        poly1, vars_, dimension = ppllib._transform_polyhedron(polyhedron1)
        poly2, __, __ = ppllib._transform_polyhedron(polyhedron2)
        poly1.poly_hull_assign(poly2)
        return ppllib._convert_into_polyhedron(poly1, vars_, dimension)

    @staticmethod
    def widening_assign(polyhedron1, polyhedron2, tp=0):
        poly1, vars_, dimension = ppllib._transform_polyhedron(polyhedron1)
        poly2, __, __ = ppllib._transform_polyhedron(polyhedron2)
        poly1.widening_assign(poly2, tp)
        return ppllib._convert_into_polyhedron(poly1, vars_, dimension)

    @staticmethod
    def extrapolation_assign(polyhedron1, polyhedron2, cs, tp=0, limited=False):
        poly1, vars_, dimension = ppllib._transform_polyhedron(polyhedron1)
        poly2, __, __ = ppllib._transform_polyhedron(polyhedron2)
        cs_ = Constraint_System([ppllib._transform_expression(c) for c in cs])
        # TODO: transform result
        poly1.extrapolation_assign(poly2, tp)
        if limited:
            poly1.limited_H79_extrapolation_assign(poly2, cs_, tp)
        else:
            poly1.bounded_H79_extrapolation_assign(poly2, cs_, tp)
        return ppllib._convert_into_polyhedron(poly1, vars_, dimension)

    @staticmethod
    def add_dimensions(polyhedron, dim):
        poly, vars_, __ = ppllib._transform_polyhedron(polyhedron)
        poly.add_space_dimensions_and_embed(dim)
        return ppllib._convert_into_polyhedron(poly, vars_, poly.space_dimension())

    @staticmethod
    def remove_dimensions(polyhedron, var_set):
        from ppl import Variables_Set
        poly, vars_, dimension = ppllib._transform_polyhedron(polyhedron)
        vs = Variables_Set()
        final_vs = []
        if isinstance(vs, str):
            var_set = [var_set]
        for i in range(dimension):
            if vars_[i] in var_set:
                vs.insert(Variable(i))
            else:
                final_vs.append(vars_[i])
        poly.remove_space_dimensions(vs)
        return ppllib._convert_into_polyhedron(poly, final_vs, poly.space_dimension())

    @staticmethod
    def expand_space_dimension(polyhedron, var, m):
        poly, vars_, dimension = ppllib._transform_polyhedron(polyhedron)
        if var not in vars_:
            raise ValueError("Variable ({}) not in polyhedron".format(var))
        poly.expand_space_dimension(Variable(vars_.index(var)), m)
        dim = poly.space_dimension()
        final_vs = vars_[:]
        base = "x"
        num = dimension
        for __ in range(dimension, dim):
            v = base + str(num)
            while v in final_vs:
                num += 1
                v = base + str(num)
            num += 1
            final_vs.append(v)
        return ppllib._convert_into_polyhedron(poly, final_vs, dim)

    @staticmethod
    def intersection_assign(polyhedron1, polyhedron2):
        poly1, vars_, dimension = ppllib._transform_polyhedron(polyhedron1)
        poly2, __, __ = ppllib._transform_polyhedron(polyhedron2)
        poly1.intersection_assign(poly2)
        return ppllib._convert_into_polyhedron(poly1, vars_, dimension)

    @staticmethod
    def unconstraint(polyhedron, var):
        poly, vars_, dimension = ppllib._transform_polyhedron(polyhedron)
        if var not in vars_:
            raise ValueError("Variable ({}) not in polyhedron".format(var))
        poly.unconstrain(Variable(vars_.index(var)))
        return ppllib._convert_into_polyhedron(poly, vars_, dimension)

    @staticmethod
    def project(polyhedron, var_set):
        from ppl import Variables_Set
        poly, vars_, dimension = ppllib._transform_polyhedron(polyhedron)
        vs = Variables_Set()
        final_vs = []
        if isinstance(vs, str):
            var_set = [var_set]
        do_it = False
        for i in range(dimension):
            if vars_[i] in var_set:
                final_vs.append(vars_[i])
            else:
                do_it = True
                vs.insert(Variable(i))
        if len(var_set) > len(final_vs):
            raise ValueError("Polyhedron can NOT be projected to the vars: {},\n because some variables are not in the polyhedron.".format(var_set))

        if do_it:
            poly.remove_dimensions(vs)
        return ppllib._convert_into_polyhedron(poly, final_vs, poly.space_dimension())
