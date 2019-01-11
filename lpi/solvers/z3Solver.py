from lpi.solvers import SolverInterface
from z3 import Solver
from z3 import Real
from z3 import sat
from z3 import simplify
from lpi.utils import lcm


class z3Solver(SolverInterface):
    # TODO: Define lib
    """
    >>> z3Solver()
    Traceback (most recent call last):
    ...
    Exception: Can NOT be instantiate.
    """
    _ID = "z3"

    @staticmethod
    def _transform_polyhedron(polyhedron):
        vs = polyhedron.get_variables()
        dim = polyhedron.get_dimension()

        def toVar(v):
            if v in vs:
                return Real(v)
            else:
                raise ValueError("{} is not a variable.".format(v))
        cs = [c.get(toVar, int, ignore_zero=True)
              for c in polyhedron.get_constraints()]
        return (cs, vs, dim)

    @staticmethod
    def _convert_into_polyhedron(solver, vars_):
        from lpi import ExprTerm
        from lpi import C_Polyhedron

        def parse_cons_tree(tree):
            if tree.num_args() == 0:
                return ExprTerm(str(tree))
            else:
                op = tree.decl().name()
                if op == "*":
                    return parse_cons_tree(tree.children()[0]) * parse_cons_tree(tree.children()[1])
                elif op == "+":
                    return parse_cons_tree(tree.children()[0]) + parse_cons_tree(tree.children()[1])
                elif op == "/":
                    return parse_cons_tree(tree.children()[0]) / parse_cons_tree(tree.children()[1])
                elif op == "-":
                    return parse_cons_tree(tree.children()[0]) - parse_cons_tree(tree.children()[1])
                elif op == ">=":
                    return parse_cons_tree(tree.children()[0]) >= parse_cons_tree(tree.children()[1])
                elif op == "<=":
                    return parse_cons_tree(tree.children()[0]) <= parse_cons_tree(tree.children()[1])
                elif op == ">":
                    return parse_cons_tree(tree.children()[0]) > parse_cons_tree(tree.children()[1])
                elif op == "<":
                    return parse_cons_tree(tree.children()[0]) < parse_cons_tree(tree.children()[1])
                else:
                    raise ValueError("Not a valid operator ({})".format(op))

        cons = [parse_cons_tree(simplify(c)) for c in solver.assertions()]
        return C_Polyhedron(constraints=cons, variables=vars_)

    @staticmethod
    def get_point(polyhedron):
        """
        >>> from lpi import C_Polyhedron
        >>> from lpi import ExprTerm
        >>> from lpi.solvers import solver_factory
        >>> exp = 5 * ExprTerm('x')
        >>> y = ExprTerm('y')
        >>> p = C_Polyhedron([exp < y, exp <= y, exp + y > 3, y > 2], ['x', 'y'])
        >>> solver_factory('z3').get_point(p)
        ([0.0, 4.0], 1)
        """
        cons, vars_, __ = z3Solver._transform_polyhedron(polyhedron)
        s = Solver()
        s.add(cons)
        if s.check() == sat:
            # build POINT
            coeffs = s.model()
            point = []
            divisor = lcm([int(str(coeffs[f].denominator()))
                           for f in coeffs])

            for v in vars_:
                if coeffs[Real(v)] is not None:
                    ci = int(str(coeffs[Real(v)].numerator()))
                    ci *= (divisor / int(str(coeffs[Real(v)].denominator())))
                else:
                    ci = 0
                point.append(ci)

            return (point, divisor)
        else:
            return None, 1

    @staticmethod
    def is_sat(polyhedron):
        """
        >>> from lpi import C_Polyhedron
        >>> from lpi import ExprTerm
        >>> from lpi.solvers import solver_factory
        >>> exp = 5 * ExprTerm('x')
        >>> y = ExprTerm('y')
        >>> p = C_Polyhedron([exp < y, exp <= y, exp + y > 3, y > 2], ['x', 'y'])
        >>> solver_factory('z3').is_sat(p)
        True
        """
        cons, __, __ = z3Solver._transform_polyhedron(polyhedron)
        s = Solver()
        s.add(cons)
        return s.check() == sat


if __name__ == "__main__":
    import doctest
    doctest.testmod(verbose=True)
