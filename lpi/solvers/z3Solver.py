from lpi.solvers import SolverInterface
from z3 import Solver
from z3 import Real
from z3 import sat
from z3 import simplify
from lpi.utils import lcm


class z3Solver(SolverInterface):
    """
    Implementation of the `SolverInterface` using z3.
    this class can NOT be instantiate, all their methods are static.
    >>> z3Solver()
    Traceback (most recent call last):
    ...
    Exception: Can NOT be instantiate.
    """
    _ID = "z3"

    @staticmethod
    def transform(polyhedron):
        return z3Solver._transform(polyhedron.get_constraints(), polyhedron.get_variables())

    @staticmethod
    def _transform(expression, vars_=None):
        if isinstance(expression, list):
            return [z3Solver._transform(e, vars_=vars_) for e in expression]

        def toVar(v):
            if v in vars_:
                return Real(v)
            else:
                raise ValueError("{} is not a variable.".format(v))

        return expression.get(toVar, int, ignore_zero=True)

    @staticmethod
    def _convert_into_polyhedron(solver, vars_):
        from lpi import Expression
        from lpi import C_Polyhedron

        def parse_cons_tree(tree):
            if tree.num_args() == 0:
                return Expression(str(tree))
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
        >>> from lpi import Expression
        >>> from lpi.solvers import solver_factory
        >>> exp = 5 * Expression('x')
        >>> y = Expression('y')
        >>> p = C_Polyhedron([exp < y, exp <= y, exp + y > 3, y > 2], ['x', 'y'])
        >>> solver_factory('z3').get_point(p)
        (2 * y, 1)
        """
        from lpi import Expression
        vars_ = polyhedron.get_variables()
        cons = z3Solver._transform(polyhedron.get_constraints(), vars_)
        s = Solver()
        s.add(cons)
        if s.check() == sat:
            # build POINT
            coeffs = s.model()
            divisor = lcm([int(str(coeffs[f].denominator()))
                           for f in coeffs])
            exp = Expression(0)
            for v in vars_:
                if coeffs[Real(v)] is not None:
                    ci = int(str(coeffs[Real(v)].numerator()))
                    ci *= (divisor / int(str(coeffs[Real(v)].denominator())))
                else:
                    ci = 0
                exp += ci * Expression(v)

            return (exp, divisor)
        else:
            return None, 1

    @staticmethod
    def is_sat(polyhedron):
        """
        >>> from lpi import C_Polyhedron
        >>> from lpi import Expression
        >>> from lpi.solvers import solver_factory
        >>> exp = 5 * Expression('x')
        >>> y = Expression('y')
        >>> p = C_Polyhedron([exp < y, exp <= y, exp + y > 3, y > 2], ['x', 'y'])
        >>> solver_factory('z3').is_sat(p)
        True
        """
        cons = z3Solver._transform(polyhedron.get_constraints(), polyhedron.get_variables())
        s = Solver()
        s.add(cons)
        return s.check() == sat


if __name__ == "__main__":
    import doctest
    doctest.testmod(verbose=True)
