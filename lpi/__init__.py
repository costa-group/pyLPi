"""
Constraints, Expressions and methods to use them with LP libs and SMT-solvers

Submodules
----------

.. autosummary::
    :toctree: _autosummary

    solvers

Contents
--------

.. autosummary::
    :toctree: _autosummary

    polyhedron.C_Polyhedron
    constraints.Constraint
    expressions.Expression
    utils

"""
from lpi.constraints import Constraint
from lpi.polyhedron import C_Polyhedron
from lpi.expressions import Expression
from lpi.solvers import solver_factory


__all__ = ["C_Polyhedron", "Constraint", "Expression",
           "solver_factory", "smtlib"]


def tests():
    import doctest
    import lpi
    import lpi.solvers.z3Solver
    import lpi.polyhedron
    import lpi.utils
    mods = [lpi, lpi.solvers, lpi.solvers.z3Solver,
            lpi.polyhedron, lpi.expressions, lpi.constraints, lpi.utils]
    F, T = 0, 0
    for m in mods:
        f, t = doctest.testmod(m)
        F += f
        T += t
        if f == 0:
            print("Test passed: `{}`".format(m.__name__))
    return F, T


smtlib = solver_factory("z3")
