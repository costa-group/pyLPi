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
    _ID = ""

    def __init__(self, *args, **kwargs):
        raise Exception("Can NOT be instantiate.")

    @staticmethod
    def _transform_polyhedron(polyhedron): raise NotImplementedError()

    @staticmethod
    def _convert_into_polyhedron(*args): raise NotImplementedError()

    @staticmethod
    def get_point(polyhedron): raise NotImplementedError()

    @staticmethod
    def is_sat(polyhedron): raise NotImplementedError()


def solver_factory(name):
    from .z3Solver import z3Solver
    solvers = [z3Solver]
    for s in solvers:
        if s._ID.lower() == name.lower():
            return s
    raise ValueError("Solver ({}) not found.".format(name))
