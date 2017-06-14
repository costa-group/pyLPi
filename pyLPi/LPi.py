# from RankConfig import getLPMod
import LPppl
import LPz3


class C_Polyhedron:
    """A closed convex polyhedron.
    """

    _poly = None

    def __init__(self, cons=None, dim=-1, lplib=None):
        """Builds a C polyhedron from a system of constraints.

        :param cons: Constraint system
        :type cons: ppl.Constraint_System :param dim: dimension
            of the `universe`, optional. Defaults Constraint System dimension.
        :type dim: int
        """
        if lplib is None:
            lplib = "ppl"  # get_LP_lib_name()
        if lplib == "ppl":
            self._poly = LPppl.LPPolyhedron(cons, dim)
        elif lplib == "z3":
            self._poly = LPz3.LPPolyhedron(cons, dim)

    def add_constraint(self, constraint):
        """Adds a copy of constraint to the system of constraints
        of this (without minimizing the result).

        :param constraint: Constraint to be added.
        :type constraint: `ppl.Constraint`
        """
        self._poly.add_constraint(constraint)

    def add_constraints(self, constraints):
        """Adds a copy of each constraint to the system of constraints of this
        (without minimizing the result).

        :param constraints: List to be added.
        :type constraints: `list` of `ppl.Constraint`
        """
        self._poly.add_constraints(constraints)

    def add_constraint_system(self, constraint_system):
        """Adds a copy of the constraints in constraint_system to the system
        of constraints of this (without minimizing the result).

        :param constraint_system: Constraint system to be added
        :type constraint_system: `ppl.Constraint_System`
        """
        self._poly.add_constraint_system(constraint_system)

    def get_dimension(self):
        """Returns the dimension of the vector space enclosing
        """
        return self._poly.get_dimension()

    def get_constraints(self):
        """Returns the system of constraints.
        """
        return self._poly.get_constraints()

    def get_point(self):
        """Returns a random interior point.
        """
        return self._poly.get_point()

    def get_generators(self):
        """Returns the system of generators.
        """
        return self._poly.get_generators()

    def contains_integer_point(self):
        """Returns true if and only if *this contains at least one
        integer point.
        """
        return self._poly.contains_integer_point()

    def get_integer_point(self):
        """Returns a random interior integer point.
        """
        return self._poly.get_integer_point()

    def get_relative_interior_point():
        """Returns a random interior point.
        """
        return self._poly.get_relative_interior_point()

    def minimize(self, expression):
        return self._poly.minimize(expression)

    def maximize(self, expression):
        return self._poly.maximize(expression)

    def is_empty(self):
        """Returns true if and only if it is an empty polyhedron.
        """
        return self._poly.is_empty()

    def is_implied(self, constraint):
        return self._poly.is_implied(constraint)

    def is_disjoint_from(self, polyhedron):
        """Returns true if and only if this and `polyhedron` are disjoint.

        :param polyhedron: Polyhedron to compare
        :type polyhedron: :obj:C_Polyhedron
        """
        return self._poly.is_disjoint_from(polyhedron)

    def __repr__(self):
        return self._poly.__repr__()

    def int_minimize(self, something):
        return self._poly.int_minimize(something)

    def int_maximize(self, something):
        return self._poly.int_maximize(something)

    def is_bounded(self):
        """Returns true if and only if this is a bounded polyhedron.
        """
        return self._poly.is_bounded()

    def minimize_constraint_system():
        """Returns the system of constraints, with no redundant constraint.
        """
        return self._poly.minimize_constraint_system()
