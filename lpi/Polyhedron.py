class Polyhedron:

    _existsPoly = False
    _poly = None
    _constraints = None
    _dimension = 0

    def __init__(self, constraints=[], dim=0):
        # TODO: Define new polyhedron