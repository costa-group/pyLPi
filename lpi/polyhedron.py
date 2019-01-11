"""
Created on January 2019

@author: Jesús J. Doménech
"""


class C_Polyhedron:

    _constraints = []
    _dimension = 0
    _vars = []

    def __init__(self, constraints=[], variables=[]):
        """Closed Polyhedron.

        :param constraints: list of constraints
        :type constraints: `list` of `lpi.Constraint`
        :param variables: list of variables names.
        :type variables: `list` of `string`
        """
        self._dimension = len(variables)
        self._vars = variables
        self._constraints = constraints

    def add_constraint(self, constraint):
        """Adds a constraint.

        :param constraint: Constraint to be added.
        :type constraint: `lpi.Constraint`
        """
        self._constraints.append(constraint)

    def add_constraints(self, constraints):
        """Adds a list of constraints.

        :param constraints: List to be added.
        :type constraints: `list` of `lpi.Constraint`
        """
        for c in constraints:
            self._constraints.append(c)

    def get_dimension(self):
        """Returns the dimension of the vector space enclosing
        """
        return self._dimension

    def get_variables(self):
        """Returns the list of variables of the polyhedron.
        """
        return self._vars

    def toString(self, vars_name=None, eq_symb="==", geq_symb=">="):
        """Returns an string representing the polyhedron

        :param eq_symb: symbol for equalities
        :type eq_symb: `string`
        :param geq_symb: symbol for inequalities of type greater than or equal to.
        :type geq_symb: `string`
        """
        cs = self._constraints
        if vars_name is not None:
            raise DeprecationWarning("vars name used at toString")
        vars_name = self._vars
        toVar = lambda v: v
        toNum = lambda v: str(int(v))
        return [c.toString(toVar, toNum, eq_symb=eq_symb, geq_symb=geq_symb)
                for c in cs]

    def get_constraints(self, use_z3=None):
        """Returns the list of constraints.
        """
        if use_z3 is not None:
            raise DeprecationWarning()
        return self._constraints
