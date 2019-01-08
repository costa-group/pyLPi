from enum import Enum


class opExp(Enum):
    ADD = "+"
    SUB = "-"
    MUL = "*"
    DIV = "/"

    def __repr__(self):
        return self.value()


class Expression(object):

    def __init__(self, left, op: opExp, right):
        if not isinstance(left, Expression):
            try:
                left = ExprTerm(left)
            except ValueError:
                raise ValueError("left argument is not a valid Expression.")
        if not isinstance(right, Expression):
            try:
                right = ExprTerm(right)
            except ValueError:
                raise ValueError("right argument is not a valid Expression.")
        if not isinstance(op, opExp):
            raise ValueError("{} is not a valid Operation.".format(op))
        from collections import Counter
        summands = []
        max_degree = 0
        n_vs = []
        if op == opExp.DIV:
            if(len(right._summands) > 1 or
               len(right._summands[0][1]) > 0):
                raise TypeError("Unsupported division by polynom.")
            else:
                r_coeff = right._summands[0][0]
                if r_coeff == 0:
                    raise TypeError("Division by zero.")
                for s in left._summands:
                    coeff = s[0] / r_coeff
                    if coeff != 0:
                        summands.append((coeff, s[1]))
                max_degree = left.degree()
                n_vs = left.get_variables()
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
            var_set = set()
            while len(tmp_summands) > 0:
                coeff, vs = tmp_summands.pop(0)
                for sr in tmp_summands:
                    if Counter(vs) == Counter(sr[1]):
                        coeff += sr[0]
                        tmp_summands.remove(sr)
                if coeff != 0:
                    if len(vs) > max_degree:
                        max_degree = len(vs)
                    var_set.union(vs)
                    summands.append((coeff, vs))
            n_vs = list(var_set)
            del var_set
        elif op in [opExp.ADD, opExp.SUB]:
            symb = 1
            if op == opExp.SUB:
                symb = -1
            pending_summands = right._summands
            var_set = set()
            for s in left._summands:
                coeff, vs = s
                for sr in pending_summands:
                    if Counter(vs) == Counter(sr[1]):
                        coeff += symb * sr[0]
                        pending_summands.remove(sr)
                if coeff != 0:
                    if len(vs) > max_degree:
                        max_degree = len(vs)
                    var_set.union(vs)
                    summands.append((coeff, vs))
            for coeff, vs in pending_summands:
                if coeff != 0:
                    if len(vs) > max_degree:
                        max_degree = len(vs)
                    var_set.union(vs)
                    summands.append((symb * coeff, vs))
            n_vs = list(var_set)
            del var_set
        self._summands = summands
        self._degree = max_degree
        self._vars = n_vs

    def degree(self): return self._degree

    def is_linear(self): return self.degree() < 2

    def get_variables(self): return self._vars

    def get_coeff(self, variables=[]):
        if isinstance(variables, str):
            variables = [variables]
        from collections import Counter
        for sr in self._summands:
            if Counter(variables) == Counter(sr[1]):
                return sr[0]
        return 0

    def toString(self, toVar, toNum):
        txt = ""
        _one = toNum(1)
        _minusone = toNum(-1)
        _zero = toNum(0.0)
        for s in self._summands:
            txt_s = ""
            s0_num = toNum(s[0])
            if len(s[1]) > 0:
                if s0_num != _one and s0_num != _minusone:
                    txt_s += str(s0_num) + " * "
                elif s0_num == _minusone:
                    txt_s += "- "
                txt_s += " * ".join([toVar(v) for v in s[1]])
            elif s0_num != _zero:
                txt_s = str(s0_num)

            if s0_num > _zero and txt != "":
                txt += " + "
            elif txt != "":
                txt += " "
            txt += txt_s
        if txt == "":
            txt = "0"
        return txt

    def __repr__(self): return self.toString(str, int)

    def get(self, toVar, toNum, toExp=lambda x: x, ignore_zero=False):
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
            right = ExprTerm(other)
        elif not isinstance(other, (ExprTerm, Expression)):
            raise NotImplementedError()
        return Expression(self, opExp.ADD, right)

    def __sub__(self, other):
        right = other
        if isinstance(other, (float, int)):
            right = ExprTerm(other)
        elif not isinstance(other, (ExprTerm, Expression)):
            raise NotImplementedError()
        return Expression(self, opExp.SUB, right)

    def __mul__(self, other):
        right = other
        if isinstance(other, (float, int)):
            right = ExprTerm(other)
        elif not isinstance(other, (ExprTerm, Expression)):
            raise NotImplementedError()
        return Expression(self, opExp.MUL, right)

    def __truediv__(self, other):
        right = other
        if isinstance(other, (float, int)):
            right = ExprTerm(other)
        elif not isinstance(other, (ExprTerm, Expression)):
            raise NotImplementedError()
        return Expression(self, opExp.DIV, right)

    def __neg__(self):
        return self * (-1)

    def __pos__(self):
        return self

    def __radd__(self, other):
        left = other
        if isinstance(other, (float, int)):
            left = ExprTerm(other)
        elif not isinstance(other, (ExprTerm, Expression)):
            raise NotImplementedError()
        return Expression(left, opExp.ADD, self)

    def __rsub__(self, other):
        left = other
        if isinstance(other, (float, int)):
            left = ExprTerm(other)
        elif not isinstance(other, (ExprTerm, Expression)):
            raise NotImplementedError()
        return Expression(left, opExp.SUB, self)

    def __rmul__(self, other):
        left = other
        if isinstance(other, (float, int)):
            left = ExprTerm(other)
        elif not isinstance(other, (ExprTerm, Expression)):
            raise NotImplementedError()
        return Expression(left, opExp.MUL, self)

    def __rtruediv__(self, other):
        left = other
        if isinstance(other, (float, int)):
            left = ExprTerm(other)
        elif not isinstance(other, (ExprTerm, Expression)):
            raise NotImplementedError()
        return Expression(left, opExp.DIV, self)

    def __lt__(self, other):
        right = other
        if isinstance(other, (float, int)):
            right = ExprTerm(other)
        elif not isinstance(other, (ExprTerm, Expression)):
            raise NotImplementedError()
        from .Constraints import opCMP
        from .Constraints import Constraint
        return Constraint(self, opCMP.LT, right)

    def __le__(self, other):
        right = other
        if isinstance(other, (float, int)):
            right = ExprTerm(other)
        elif not isinstance(other, (ExprTerm, Expression)):
            raise NotImplementedError()
        from .Constraints import opCMP
        from .Constraints import Constraint
        return Constraint(self, opCMP.LEQ, right)

    def __eq__(self, other):
        right = other
        if isinstance(other, (float, int)):
            right = ExprTerm(other)
        elif not isinstance(other, (ExprTerm, Expression)):
            raise NotImplementedError()
        from .Constraints import opCMP
        from .Constraints import Constraint
        return Constraint(self, opCMP.EQ, right)

    def __gt__(self, other):
        right = other
        if isinstance(other, (float, int)):
            right = ExprTerm(other)
        elif not isinstance(other, (ExprTerm, Expression)):
            raise NotImplementedError()
        from .Constraints import opCMP
        from .Constraints import Constraint
        return Constraint(self, opCMP.GT, right)

    def __ge__(self, other):
        right = other
        if isinstance(other, (float, int)):
            right = ExprTerm(other)
        elif not isinstance(other, (ExprTerm, Expression)):
            raise NotImplementedError()
        from .Constraints import opCMP
        from .Constraints import Constraint
        return Constraint(self, opCMP.GEQ, right)


class ExprTerm(Expression):

    def __init__(self, value):
        vs = []
        coeff = 1
        if isinstance(value, (float, int)):
            coeff = value
        else:
            try:
                coeff = float(value)
            except ValueError:
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
        self._summands = [(coeff, vs)]
        self._degree = len(vs)
        self._vars = list(vs)

    def __neg__(self):
        return self * (-1)
