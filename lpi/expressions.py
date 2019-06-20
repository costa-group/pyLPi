from enum import Enum
from decimal import Decimal
from fractions import Fraction, gcd


class opExp(Enum):
    ADD = "+"
    SUB = "-"
    MUL = "*"
    DIV = "/"

    def __repr__(self):
        return self.value()


class Term(object):

    def __new__(cls, value, denominator=1):
        vs = []
        coeff = 1
        den = denominator
        try:
            coeff, den = cls._coefficient(value, den)
        except ValueError:
            vs = cls._variable(value)
        ex = Expression()
        ex._summands = [(coeff, vs)]
        ex._degree = len(vs)
        ex._vars = list(vs)
        ex._denominator = den
        return ex

    @classmethod
    def _coefficient(cls, value, den=1):
        from decimal import InvalidOperation
        try:
            v = str(value)
            vs = v.split("/")
            if len(vs) == 1:
                dec = Decimal(v)
                frac = Fraction(dec)
            elif len(vs) == 2:
                frac = Fraction(int(vs[0]), int(vs[1]))
            else:
                raise InvalidOperation()
        except InvalidOperation:
            raise ValueError("{} is not a valid coefficient".format(value))
        if den != 1:
            frac = Fraction(frac.numerator, frac.denominator * den)
        return frac.numerator, frac.denominator

    @classmethod
    def _variable(cls, value):
        import re
        vlist = value
        if not isinstance(value, list):
            vlist = [value]
        vs = []
        for v in vlist:
            if re.match("(^([\w_][\w0-9\'\^_\!\.]*)$)", v):
                vs.append(v)
            else:
                raise ValueError("{} is not a valid Term.".format(v))
        return vs


class Expression(object):

    def __init__(self, left=None, op=None, right=None):
        from collections import Counter
        summands = []
        max_degree = 0
        n_vs = []
        den = 1
        if left is not None and not isinstance(left, Expression):
            try:
                left = Term(left)
            except ValueError:
                raise ValueError("Left argument is not a valid Expression.")
        elif left is not None:
            left = left.copy()
        if op is None:
            if left is None:
                summands = []
                max_degree = 0
                n_vs = []
                den = 1
            else:
                summands = left._summands[:]
                max_degree = left.degree()
                n_vs = list(left.get_variables())
                den = left._denominator
        else:
            if right is None or left is None:
                raise ValueError("Wrong parameters.")
            if not isinstance(right, Expression):
                try:
                    right = Term(right)
                except ValueError:
                    raise ValueError("Right argument is not a valid Expression.")
            else:
                right = right.copy()
            if not isinstance(op, opExp):
                raise ValueError("{} is not a valid Operation.".format(op))
            if op == opExp.DIV:
                if(len(right._summands) > 1 or
                   len(right._summands[0][1]) > 0):
                    raise ValueError("Unsupported division by polynom.")
                else:
                    r_coeff = right._summands[0][0]
                    r_den = right._denominator
                    if r_coeff == 0:
                        raise ValueError("Division by zero.")
                    symb = 1
                    if r_coeff < 0:
                        symb = -1
                    for s in left._summands:
                        coeff = s[0] * r_den * symb
                        if coeff != 0:
                            summands.append((coeff, s[1]))
                    den = left._denominator * r_coeff * symb
                    max_degree = left.degree()
                    n_vs = list(left.get_variables())
            elif op == opExp.MUL:
                tmp_summands = []
                for l_s in left._summands:
                    l_coeff, l_vars = l_s
                    for l_r in right._summands:
                        coeff = l_coeff * l_r[0]
                        var = l_vars + l_r[1]
                        var.sort()
                        if coeff != 0:
                            tmp_summands.append((coeff, var))
                den = left._denominator * right._denominator
                var_set = []
                while len(tmp_summands) > 0:
                    coeff, vs = tmp_summands.pop(0)
                    for sr in tmp_summands:
                        if Counter(vs) == Counter(sr[1]):
                            coeff += sr[0]
                            tmp_summands.remove(sr)
                    if coeff != 0:
                        if len(vs) > max_degree:
                            max_degree = len(vs)
                        var_set += [_v for _v in vs if _v not in var_set]
                        summands.append((coeff, vs))
                n_vs = var_set
            elif op in [opExp.ADD, opExp.SUB]:
                lcm = lambda a, b: (a * b / gcd(a, b))
                symb = 1
                if op == opExp.SUB:
                    symb = -1
                den = lcm(left._denominator, right._denominator)
                l_dif = den / left._denominator
                r_dif = den / right._denominator
                pending_summands = right._summands
                var_set = []
                for s in left._summands:
                    coeff, vs = s
                    coeff = coeff * l_dif
                    for sr in pending_summands:
                        if Counter(vs) == Counter(sr[1]):
                            r_c = sr[0] * r_dif
                            coeff += symb * r_c
                            pending_summands.remove(sr)
                    if coeff != 0:
                        if len(vs) > max_degree:
                            max_degree = len(vs)
                        var_set += [_v for _v in vs if _v not in var_set]
                        summands.append((coeff, vs))
                for coeff, vs in pending_summands:
                    coeff = coeff * r_dif
                    if coeff != 0:
                        if len(vs) > max_degree:
                            max_degree = len(vs)
                        var_set += [_v for _v in vs if _v not in var_set]
                        summands.append((symb * coeff, vs))
                n_vs = var_set
        self._summands = summands
        self._degree = max_degree
        self._vars = n_vs
        self._denominator = den

    def copy(self):
        E = Expression()
        E._summands = self._summands[:]
        E._degree = self.degree()
        E._vars = list(self.get_variables())
        E._denominator = self._denominator
        return E

    def aproximate_coeffs(self, max_coeff=1e14, max_dec=10):
        divby = 1
        for s in self._summands:
            while abs(s[0]) / divby > max_coeff:
                divby *= 10
        new_summands = []
        n_vs = []
        max_degree = 0
        divby = divby * self._denominator
        for s in self._summands:
            c = round(s[0] / divby, max_dec)
            if c == 0:
                continue
            max_degree = len(s[1]) if len(s[1]) > max_degree else max_degree
            for v in s[1]:
                if v not in n_vs:
                    n_vs.append(v)
            new_summands.append((c, s[1]))
        self._denominator = divby
        self._summands = new_summands
        self._degree = max_degree
        self._vars = n_vs

    def denominator(self): return self._denominator

    def degree(self): return self._degree

    def is_linear(self): return self.degree() < 2

    def get_variables(self): return self._vars[:]

    def get_coeff(self, variables=[]):
        if isinstance(variables, str):
            variables = [variables]
        from collections import Counter
        for sr in self._summands:
            if Counter(variables) == Counter(sr[1]):
                return sr[0]
        return 0

    def is_constant(self):
        return len(self._vars) == 0

    def _prefixToString(self, toVar, toNum):
        _one = toNum(1.0)
        _minusone = toNum(-1.0)
        _zero = toNum(0.0)
        if len(self._summands) == 0:
            return "0"

        def s2prefix(s):
            s0_num = toNum(s[0])
            if len(s[1]) == 0:
                return str(s0_num)
            vs = toVar(s[1][0])
            if len(s[1]) > 1:
                vs = "(* {} {})".format(vs, toVar(s[1][1]))
                for v in s[1][2:]:
                    vs = "(* {} {})".format(vs, toVar(v))
            if s0_num != _one:
                return "(* {} {})".format(s0_num, vs)
            else:
                return vs
        txt = s2prefix(self._summands[0])
        for s in self._summands[1:]:
            txt = "(+ {} {})".format(txt, s2prefix(s))
        return txt

    def toString(self, toVar, toNum, opformat="infix"):
        if opformat == "prefix":
            return self._prefixToString(toVar, toNum)
        txt = ""
        _one = toNum(1.0)
        _minusone = toNum(-1.0)
        _zero = toNum(0.0)
        for s in self._summands:
            txt_s = ""
            s0_num = toNum(s[0])
            if s0_num > _zero and txt != "":
                txt += " + "
            elif s0_num < _zero and txt != "":
                txt += " "
            elif s0_num == _zero:
                continue
            if len(s[1]) > 0:
                if s0_num != _one and s0_num != _minusone:
                    txt_s += str(s0_num) + " * "
                elif s0_num == _minusone:
                    txt_s += "-"
                txt_s += " * ".join([toVar(v) for v in s[1]])
            elif s0_num != _zero:
                txt_s = str(s0_num)
            txt += txt_s
        if txt == "":
            txt = "0"
        elif self._denominator != 1:
            txt = "(" + txt + ") / " + str(toNum(self._denominator))
        return txt

    def __repr__(self): return self.toString(str, int)

    def renamed(self, old_names, new_names):
        from collections import Counter
        corresponding = {o: n for o, n in zip(old_names, new_names)}
        tmp_summands = [(c, [corresponding[v] for v in vs]) for c, vs in self._summands]
        var_set = []
        max_degree = 0
        summands = []
        while len(tmp_summands) > 0:
            coeff, vs = tmp_summands.pop(0)
            for sr in tmp_summands:
                if Counter(vs) == Counter(sr[1]):
                    coeff += sr[0]
                    tmp_summands.remove(sr)
            if coeff != 0:
                if len(vs) > max_degree:
                    max_degree = len(vs)
                var_set += [_v for _v in vs if _v not in var_set]
                summands.append((coeff, vs))
        exp = Expression()
        exp._summands = summands
        exp._degree = max_degree
        exp._vars = var_set
        exp._denominator = self._denominator
        return exp

    def get(self, toVar, toNum, toExp=lambda x: x, ignore_zero=False, toAnd=None, toOr=None):
        """
        toVar: function which keys are the variables name.
        toNum: class of numbers (e.g for ppl use Linear_Expression, for z3 use Real or Int)
        """
        exp = toExp(0)
        for s in self._summands:
            s_exp = toNum(s[0])
            if ignore_zero:
                if s_exp == toNum(0):
                    continue
            for v in s[1]:
                s_exp *= toVar(v)
            exp += s_exp
        if self._denominator != 1:
            print("IM USING THE DENOMINATORRRRR")
            print("#" * 80)
            exp = exp / toNum(self._denominator)
        return exp

    def transform(self, variables, lib="ppl"):
        """
        variables: list of variables (including prime and local variables)
        lib: "z3" or "ppl"
        """
        if lib == "ppl":
            from ppl import Linear_Expression
            from ppl import Variable

            def toVar(v):
                if v in variables:
                    return Variable(variables.index(v))
                else:
                    raise ValueError("{} is not a variable.".format(v))

            return self.get(toVar, int, Linear_Expression)
        elif lib == "z3":

            def nope(v):
                return v

            from z3 import Int

            def toNum(v):
                return Int(int(v))

            def toVar(v):
                if v in variables:
                    return Int(v)
                else:
                    raise ValueError("{} is not a variable.".format(v))

            return self.get(toVar, toNum, nope, ignore_zero=True)
        else:
            raise ValueError("lib ({}) not supported".format(lib))

    def __add__(self, other):
        right = other
        if isinstance(other, (float, int)):
            right = Term(other)
        elif not isinstance(other, Expression):
            raise NotImplementedError("Expression can't add type: {}".format(type(other)))
        return Expression(self, opExp.ADD, right)

    def __sub__(self, other):
        right = other
        if isinstance(other, (float, int)):
            right = Term(other)
        elif not isinstance(other, Expression):
            raise NotImplementedError("Expression can't substract type: {}".format(type(other)))
        return Expression(self, opExp.SUB, right)

    def __mul__(self, other):
        right = other
        if isinstance(other, (float, int)):
            right = Term(other)
        elif not isinstance(other, Expression):
            raise NotImplementedError("Expression can't multiply type: {}".format(type(other)))
        return Expression(self, opExp.MUL, right)

    def __truediv__(self, other):
        right = other
        if isinstance(other, (float, int)):
            right = Term(other)
        elif not isinstance(other, Expression):
            raise NotImplementedError("Expression can't be divided by type: {}".format(type(other)))
        return Expression(self, opExp.DIV, right)

    def __neg__(self):
        return self * (-1)

    def __pos__(self):
        return self

    def __radd__(self, other):
        left = other
        if isinstance(other, (float, int)):
            left = Term(other)
        elif not isinstance(other, Expression):
            raise NotImplementedError(type(other))
        return Expression(left, opExp.ADD, self)

    def __rsub__(self, other):
        left = other
        if isinstance(other, (float, int)):
            left = Term(other)
        elif not isinstance(other, Expression):
            raise NotImplementedError(type(other))
        return Expression(left, opExp.SUB, self)

    def __rmul__(self, other):
        left = other
        if isinstance(other, (float, int)):
            left = Term(other)
        elif not isinstance(other, Expression):
            raise NotImplementedError(type(other))
        return Expression(left, opExp.MUL, self)

    def __rtruediv__(self, other):
        left = other
        if isinstance(other, (float, int)):
            left = Term(other)
        elif not isinstance(other, Expression):
            raise NotImplementedError(type(other))
        return Expression(left, opExp.DIV, self)

    def __lt__(self, other):
        right = other
        if isinstance(other, (float, int)):
            right = Term(other)
        elif not isinstance(other, Expression):
            raise NotImplementedError()
        from lpi.constraints import opCMP
        from lpi.constraints import Constraint
        return Constraint(self, opCMP.LT, right)

    def __le__(self, other):
        right = other
        if isinstance(other, (float, int)):
            right = Term(other)
        elif not isinstance(other, Expression):
            raise NotImplementedError()
        from lpi.constraints import opCMP
        from lpi.constraints import Constraint
        return Constraint(self, opCMP.LEQ, right)

    def __eq__(self, other):
        right = other
        if isinstance(other, (float, int)):
            right = Term(other)
        elif not isinstance(other, Expression):
            raise NotImplementedError(type(other))
        from lpi.constraints import opCMP
        from lpi.constraints import Constraint
        return Constraint(self, opCMP.EQ, right)

    def __neq__(self, other):
        right = other
        if isinstance(other, (float, int)):
            right = Term(other)
        elif not isinstance(other, Expression):
            raise NotImplementedError(type(other))
        from lpi.constraints import opCMP
        from lpi.constraints import Constraint
        return Constraint(self, opCMP.NEQ, right)

    def __gt__(self, other):
        right = other
        if isinstance(other, (float, int)):
            right = Term(other)
        elif not isinstance(other, Expression):
            raise NotImplementedError()
        from lpi.constraints import opCMP
        from lpi.constraints import Constraint
        return Constraint(self, opCMP.GT, right)

    def __ge__(self, other):
        right = other
        if isinstance(other, (float, int)):
            right = Term(other)
        elif not isinstance(other, Expression):
            raise NotImplementedError()
        from lpi.constraints import opCMP
        from lpi.constraints import Constraint
        return Constraint(self, opCMP.GEQ, right)
