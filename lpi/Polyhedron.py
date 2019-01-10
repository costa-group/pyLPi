class Polyhedron:

    _constraints = []
    _dimension = 0
    _vars = []

    def __init__(self, constraints=[], variables=[]):
        self._dimension = len(variables)
        self._vars = variables
        self._constraints = constraints

    def add_constraint(self, constraint):
        self._constraints.append(constraint)

    def add_constraints(self, constraints):
        for c in constraints:
            self._constraints.append(c)

    def get_dimension(self):
        return self._dimension

    def get_variables(self):
        return self._vars

    def toString(self, vars_name=None, eq_symb="==", geq_symb=">="):
        cs = self._constraints
        if vars_name is not None:
            raise DeprecationWarning("vars name used at toString")
        vars_name = self._vars
        toVar = lambda v: v
        toNum = lambda v: str(int(v))
        return [c.toString(toVar, toNum, eq_symb=eq_symb, geq_symb=geq_symb)
                for c in cs]

    def get_constraints(self, use_z3=None):
        if use_z3 is not None:
            raise DeprecationWarning()
        return self._constraints
