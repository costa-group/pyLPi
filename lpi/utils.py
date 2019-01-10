def lcm(numbers):
    """Return lowest common multiple."""
    from fractions import gcd
    from functools import reduce

    def lcm2(a, b):
        return (a * b) // gcd(a, b)
    return reduce(lcm2, numbers, 1)
