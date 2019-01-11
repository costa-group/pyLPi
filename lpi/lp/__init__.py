"""
Linear Programming manager

Created on January 2019

@author: Jesús J. Doménech

Contents
--------

.. autosummary::
    :toctree: _autosummary

    ppllib
"""


class lpInterface:
    _ID = ""

    def __init__(self, *args, **kwargs):
        raise Exception("Can NOT be instantiate.")

    @staticmethod
    def _transform_polyhedron(polyhedron, poly): raise NotImplementedError()

    @staticmethod
    def _convert_into_polyhedron(*args): raise NotImplementedError()

    @staticmethod
    def get_point(polyhedron): raise NotImplementedError()

    @staticmethod
    def get_generators(polyhedron): raise NotImplementedError()

    @staticmethod
    def contains(polyhedron1, polyhedron2): raise NotImplementedError()

    @staticmethod
    def contains_integer_point(polyhedron): raise NotImplementedError()

    @staticmethod
    def get_relative_interior_point(polyhedron, variables=None): raise NotImplementedError()

    @staticmethod
    def minimize(polyhedron, expression): raise NotImplementedError()

    @staticmethod
    def maximize(polyhedron, expression): raise NotImplementedError()

    @staticmethod
    def is_empty(polyhedron): raise NotImplementedError()

    @staticmethod
    def is_disjoint_from(polyhedron1, polyhedron2): raise NotImplementedError()

    @staticmethod
    def minimized_constraints(polyhedron): raise NotImplementedError()

    @staticmethod
    def upper_bound_assign(polyhedron1, polyhedron2): raise NotImplementedError()

    @staticmethod
    def poly_hull_assign(polyhedron1, polyhedron2): raise NotImplementedError()

    @staticmethod
    def widening_assign(polyhedron1, polyhedron2, tp=0): raise NotImplementedError()

    @staticmethod
    def extrapolation_assign(polyhedron1, polyhedron2, cs, tp=0, limited=False): raise NotImplementedError()

    @staticmethod
    def add_dimensions(polyhedron, dim): raise NotImplementedError()

    @staticmethod
    def remove_dimensions(polyhedron, var_set): raise NotImplementedError()

    @staticmethod
    def project(polyhedron, var_set): raise NotImplementedError()


def lp_factory(name):
    from .ppllib import ppllib
    lps = [ppllib]
    for s in lps:
        if s._ID == name:
            return s
    raise ValueError("LP ({}) not found.".format(name))
