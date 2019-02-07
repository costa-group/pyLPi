from enum import Enum


class opExp(Enum):
    ADD = "+"
    SUB = "-"
    MUL = "*"
    DIV = "/"

    def __repr__(self):
        return self.value()


class Expression(object):

    def __init__(self, left=None, op=None, right=None):
        from collections import Counter
        summands = []
        max_degree = 0
        n_vs = []
        if left is not None and not isinstance(left, Expression):
            try:
                left = self._term_exp(left)
            except ValueError:
                raise ValueError("Left argument is not a valid Expression.")
        elif left is not None:
            left = left.copy()
        if op is None:
            if left is None:
                summands = []
                max_degree = 0
                n_vs = []
            else:
                summands = left._summands[:]
                max_degree = left.degree()
                n_vs = list(left.get_variables())
        else:
            if right is None or left is None:
                raise ValueError("Wrong parameters.")
            if not isinstance(right, Expression):
                try:
                    right = self._term_exp(right)
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
                    if r_coeff == 0:
                        raise ValueError("Division by zero.")
                    for s in left._summands:
                        coeff = s[0] / r_coeff
                        if coeff != 0:
                            summands.append((coeff, s[1]))
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
                symb = 1
                if op == opExp.SUB:
                    symb = -1
                pending_summands = right._summands
                var_set = []
                for s in left._summands:
                    coeff, vs = s
                    for sr in pending_summands:
                        if Counter(vs) == Counter(sr[1]):
                            coeff += symb * sr[0]
                            pending_summands.remove(sr)
                    if coeff != 0:
                        if len(vs) > max_degree:
                            max_degree = len(vs)
                        var_set += [_v for _v in vs if _v not in var_set]
                        summands.append((coeff, vs))
                for coeff, vs in pending_summands:
                    if coeff != 0:
                        if len(vs) > max_degree:
                            max_degree = len(vs)
                        var_set += [_v for _v in vs if _v not in var_set]
                        summands.append((symb * coeff, vs))
                n_vs = var_set
        self._summands = summands
        self._degree = max_degree
        self._vars = n_vs

    def copy(self):
        E = Expression()
        E._summands = self._summands[:]
        E._degree = self.degree()
        E._vars = list(self.get_variables())
        return E

    def _term_exp(self, value):
        ss, d, vs = self._term(value)
        ex = Expression()
        ex._summands = ss
        ex._degree = d
        ex._vars = vs
        return ex

    def _term_var(self, value):
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

    def _term(self, value):
        vs = []
        coeff = 1
        try:
            coeff = float(value)
        except ValueError:
            if "/" in value:
                divs = value.split("/")
                try:
                    if len(divs) == 2:
                        coeff = float(divs[0]) / float(divs[1])
                    else:
                        raise ValueError()
                except ValueError:
                    vs = self._term_var(value)
            else:
                vs = self._term_var(value)
        return [(coeff, vs)], len(vs), list(vs)

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

    def toString(self, toVar, toNum):
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
                    txt_s += "- "
                txt_s += " * ".join([toVar(v) for v in s[1]])
            elif s0_num != _zero:
                txt_s = str(s0_num)
            txt += txt_s
        if txt == "":
            txt = "0"
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
            right = self._term_exp(other)
        elif not isinstance(other, Expression):
            raise NotImplementedError("Expression can't add type: {}".format(type(other)))
        return Expression(self, opExp.ADD, right)

    def __sub__(self, other):
        right = other
        if isinstance(other, (float, int)):
            right = self._term_exp(other)
        elif not isinstance(other, Expression):
            raise NotImplementedError("Expression can't substract type: {}".format(type(other)))
        return Expression(self, opExp.SUB, right)

    def __mul__(self, other):
        right = other
        if isinstance(other, (float, int)):
            right = self._term_exp(other)
        elif not isinstance(other, Expression):
            raise NotImplementedError("Expression can't multiply type: {}".format(type(other)))
        return Expression(self, opExp.MUL, right)

    def __truediv__(self, other):
        right = other
        if isinstance(other, (float, int)):
            right = self._term_exp(other)
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
            left = self._term_exp(other)
        elif not isinstance(other, Expression):
            raise NotImplementedError(type(other))
        return Expression(left, opExp.ADD, self)

    def __rsub__(self, other):
        left = other
        if isinstance(other, (float, int)):
            left = self._term_exp(other)
        elif not isinstance(other, Expression):
            raise NotImplementedError(type(other))
        return Expression(left, opExp.SUB, self)

    def __rmul__(self, other):
        left = other
        if isinstance(other, (float, int)):
            left = self._term_exp(other)
        elif not isinstance(other, Expression):
            raise NotImplementedError(type(other))
        return Expression(left, opExp.MUL, self)

    def __rtruediv__(self, other):
        left = other
        if isinstance(other, (float, int)):
            left = self._term_exp(other)
        elif not isinstance(other, Expression):
            raise NotImplementedError(type(other))
        return Expression(left, opExp.DIV, self)

    def __lt__(self, other):
        right = other
        if isinstance(other, (float, int)):
            right = self._term_exp(other)
        elif not isinstance(other, Expression):
            raise NotImplementedError()
        from lpi.constraints import opCMP
        from lpi.constraints import Constraint
        return Constraint(self, opCMP.LT, right)

    def __le__(self, other):
        right = other
        if isinstance(other, (float, int)):
            right = self._term_exp(other)
        elif not isinstance(other, Expression):
            raise NotImplementedError()
        from lpi.constraints import opCMP
        from lpi.constraints import Constraint
        return Constraint(self, opCMP.LEQ, right)

    def __eq__(self, other):
        right = other
        if isinstance(other, (float, int)):
            right = self._term_exp(other)
        elif not isinstance(other, Expression):
            raise NotImplementedError(type(other))
        from lpi.constraints import opCMP
        from lpi.constraints import Constraint
        return Constraint(self, opCMP.EQ, right)

    def __neq__(self, other):
        right = other
        if isinstance(other, (float, int)):
            right = self._term_exp(other)
        elif not isinstance(other, Expression):
            raise NotImplementedError(type(other))
        from lpi.constraints import opCMP
        from lpi.constraints import Constraint
        return Constraint(self, opCMP.NEQ, right)

    def __gt__(self, other):
        right = other
        if isinstance(other, (float, int)):
            right = self._term_exp(other)
        elif not isinstance(other, Expression):
            raise NotImplementedError()
        from lpi.constraints import opCMP
        from lpi.constraints import Constraint
        return Constraint(self, opCMP.GT, right)

    def __ge__(self, other):
        right = other
        if isinstance(other, (float, int)):
            right = self._term_exp(other)
        elif not isinstance(other, Expression):
            raise NotImplementedError()
        from lpi.constraints import opCMP
        from lpi.constraints import Constraint
        return Constraint(self, opCMP.GEQ, right)
