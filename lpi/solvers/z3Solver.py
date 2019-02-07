from lpi.solvers import SolverInterface
from z3 import Solver
from z3 import Real, Int
from z3 import sat
from z3 import simplify
from z3 import And
from z3 import Or
from lpi.utils import lcm
from lpi.constraints import And as ExpAnd, Or as ExpOr
from lpi.polyhedron import C_Polyhedron


class z3Solver(SolverInterface):
    """
    Implementation of the `SolverInterface` using z3.
    this class can NOT be instantiate, all their methods are static.
    """
    _ID = "z3"

    def __init__(self, variable_type="real", coefficient_type="real"):
        self.solver = Solver()
        self.set_variable_type(variable_type)
        self.set_coefficient_type(coefficient_type)

    def set_variable_type(self, v_type):
        if v_type == "real":
            self.V = Real
        elif v_type == "int":
            self.V = Int
        else:
            raise ValueError("Unknown Variable type: {}".format(v_type))

    def set_coefficient_type(self, c_type):
        if c_type == "real":
            self.C = float
        elif c_type == "int":
            self.C = int
        else:
            raise ValueError("Unknown Coefficient type: {}".format(c_type))

    def transform(self, constraints):
        if isinstance(constraints, list):
            is_or = len(constraints) > 0 and isinstance(constraints[0], list)
            items = [self.transform(a) for a in constraints]
            if len(items) == 1:
                return items[0]
            elif is_or:
                return Or(items)
            else:
                return And(items)
        elif isinstance(constraints, C_Polyhedron):
            return self.transform(constraints.get_constraints())
        else:
            return constraints.get(self.V, self.C, ignore_zero=True, toOr=Or, toAnd=And)

    def get_constraints(self):
        from lpi import Expression

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
                elif op == "=":
                    return parse_cons_tree(tree.children()[0]) == parse_cons_tree(tree.children()[1])
                elif op == "and":
                    return ExpAnd([parse_cons_tree(simplify(c)) for c in tree.children()])
                elif op == "or":
                    return ExpOr([parse_cons_tree(simplify(c)) for c in tree.children()])
                else:
                    raise ValueError("Not a valid operator ({})".format(op))

        return [parse_cons_tree(simplify(c)) for c in self.solver.assertions()]

    def add(self, constraints):
        self.solver.add(self.transform(constraints))

    def push(self):
        self.solver.push()

    def pop(self):
        self.solver.pop()

    def get_point(self, variables):
        """
        >>> from lpi import Expression
        >>> from lpi.solvers.z3Solver import z3Solver
        >>> exp, y = 5 * Expression('x'), Expression('y')
        >>> s = z3Solver("real", "real")
        >>> s.add([exp < y, exp <= y, exp + y > 3, y > 2])
        >>> p, d = s.get_point(['x', 'y'])
        >>> int(p['x']), int(p['y']), d
        (0, 4, 1)
        >>> s = z3Solver("int", "int")
        >>> s.add([exp < y, exp <= y, exp + y > 3, y > 2])
        >>> p, d = s.get_point(['x', 'y'])
        >>> int(p['x']), int(p['y']), d
        (0, 5, 1)

        """
        if self.solver.check() == sat:
            # build POINTdsadsadiojsadsa
            vs = [self.V(v) for v in variables]
            m = self.solver.model()
            coeffs = {}
            for v in vs:
                if m[v] is None:
                    coeffs[v] = (0, 1)
                elif self.V == Real:
                    coeffs[v] = (int(str(m[v].numerator())), int(str(m[v].denominator())))
                else:
                    coeffs[v] = (int(str(m[v])), 1)
            point = {}
            if self.V == Real:
                divisor = lcm([coeffs[v][1] for v in vs])
            else:
                divisor = 1
            for v in vs:
                if self.V == Real:
                    ci = coeffs[v][0] * (divisor / coeffs[v][1])
                else:
                    ci = coeffs[v][0]
                point[str(v)] = ci
            return (point, divisor)
        else:
            return None, 1

    def is_sat(self):
        """
        >>> from lpi import Expression
        >>> from lpi.solvers.z3Solver import z3Solver
        >>> exp, y = 5 * Expression('x'), Expression('y')
        >>> s = z3Solver()
        >>> s.add([exp < y, exp <= y, exp + y > 3, y > 2])
        >>> s.is_sat()
        True
        """
        return self.solver.check() == sat


if __name__ == "__main__":
    import doctest
    doctest.testmod(verbose=True)
