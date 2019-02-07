"""
SMT solvers manager

Created on January 2019

@author: Jesús J. Doménech
Contents
--------

.. autosummary::
    :toctree: _autosummary

    z3Solver
"""


class SolverInterface:
    """
    Solver Interface each implementation must implement
    the following methods.
    """
    _ID = ".."

    def __init__(self, *args, **kwargs): raise NotImplementedError()

    def transform(self, constraints): raise NotImplementedError()

    def _convert_into_polyhedron(self, *args): raise NotImplementedError()

    def get_point(self, constraints, variables): raise NotImplementedError()

    def is_sat(self, constraints): raise NotImplementedError()

    def get_constraints(self): raise NotImplementedError()


class SolverType:
    def __init__(self):
        from .z3Solver import z3Solver
        self.solver_type = z3Solver

    def set(self, name):
        from .z3Solver import z3Solver
        ops = [z3Solver, SolverInterface]
        for o in ops:
            if o._ID == name:
                self.solver_type = o
                return None
        raise ValueError("Solver {} is not implemented.".format(name))

    def create(self, *args, **kwargs):
        return self.solver_type(*args, **kwargs)


Solver_conf = SolverType()


class Solver:
    def __new__(cls, *args, **kwargs):
        return Solver_conf.create(*args, **kwargs)
