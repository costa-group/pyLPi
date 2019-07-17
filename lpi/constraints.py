from enum import Enum
from lpi.expressions import Expression
from lpi.expressions import opExp


class BoolExpression(object):

    def __init__(self, params): raise NotImplementedError()

    def to_DNF(self): raise NotImplementedError()

    def negate(self): raise NotImplementedError()

    def normalized(self, mode="int"): raise NotImplementedError()

    def renamed(self, old_names, new_names): raise NotImplementedError()

    def get(self, toVar, toNum, toExp=lambda x: x, ignore_zero=False, toAnd=None, toOr=None): raise NotImplementedError()

    def degree(self): raise NotImplementedError()

    def get_variables(self): raise NotImplementedError()

    def is_true(self): raise NotImplementedError()

    def is_false(self): raise NotImplementedError()

    def is_linear(self):
        return self.degree() < 2

    def is_equality(self):
        return False

    def toString(self, toVar, toNum, eq_symb="==", leq_symb="<=", geq_symb=">=", lt_symb="<", gt_symb=">",
                 neq_symb="!=", or_symb="OR", and_symb="AND", imp_symb="->"): raise NotImplementedError()

    def __repr__(self):
        return self.toString(str, int)


class opCMP(Enum):
    LT = "<"
    LEQ = "<="
    GT = ">"
    GEQ = ">="
    EQ = "=="
    NEQ = "!="

    def oposite(self):
        if self == opCMP.LT:
            return opCMP.GT
        if self == opCMP.GT:
            return opCMP.LT
        if self == opCMP.LEQ:
            return opCMP.GEQ
        if self == opCMP.GEQ:
            return opCMP.LEQ
        return self

    def complement(self):
        if self == opCMP.LT:
            return opCMP.GEQ
        if self == opCMP.GT:
            return opCMP.LEQ
        if self == opCMP.LEQ:
            return opCMP.GT
        if self == opCMP.GEQ:
            return opCMP.LT
        if self == opCMP.EQ:
            return opCMP.NEQ
        if self == opCMP.NEQ:
            return opCMP.EQ

    def toString(self, eq_symb="==", leq_symb="<=", geq_symb=">=", lt_symb="<", gt_symb=">", neq_symb="!="):
        if self == opCMP.LT:
            return lt_symb
        if self == opCMP.GT:
            return gt_symb
        if self == opCMP.LEQ:
            return leq_symb
        if self == opCMP.GEQ:
            return geq_symb
        if self == opCMP.EQ:
            return eq_symb
        if self == opCMP.NEQ:
            return neq_symb

    def check(self, a, b):
        if self == opCMP.LT:
            return a < b
        if self == opCMP.GT:
            return a > b
        if self == opCMP.LEQ:
            return a <= b
        if self == opCMP.GEQ:
            return a >= b
        if self == opCMP.EQ:
            return a == b
        if self == opCMP.NEQ:
            return a != b
        return False

    def __repr__(self):
        return self.toString()


class Constraint(BoolExpression):

    def __init__(self, left: Expression, op: opCMP, right: Expression = None):
        if(not isinstance(left, Expression) or
           (right is not None and not isinstance(right, Expression)) or
           (not isinstance(op, opCMP))):
            raise ValueError()
        a_op = op
        if op in [opCMP.LEQ, opCMP.LT]:
            a_op = op.oposite()
            if right is not None:
                exp = right - left
            else:
                exp = - left
        else:
            exp = left
            if right is not None:
                exp = exp - right

        self._exp = exp
        self._exp._denominator = 1
        self._op = a_op
        self._vars = self._exp.get_variables()
        self._degree = self._exp.degree()

    def aproximate_coeffs(self, max_coeff=1e12, max_dec=10):
        self._exp.aproximate_coeffs(max_coeff=max_coeff, max_dec=max_dec)
        self._exp._denominator = 1

    def to_DNF(self): return [[self]]

    def negate(self):
        if self._op == opCMP.EQ:
            return Or(Constraint(self._exp, opCMP.GT),
                      Constraint(self._exp, opCMP.LT))
        return Constraint(self._exp, self._op.complement())

    def normalized(self, mode="int"):
        if self._op in [opCMP.EQ, opCMP.GEQ]:
            return Constraint(self._exp, self._op)
        elif mode == "int":
            return Constraint(self._exp - 1, opCMP.GEQ)
        elif mode == "rat":
            return Constraint(self._exp, opCMP.GEQ)
        else:
            raise ValueError("Unknown transformation mode: {}".format(mode))

    def renamed(self, old_names, new_names):
        return Constraint(self._exp.renamed(old_names, new_names), self._op)

    def get(self, toVar, toNum, toExp=lambda x: x, ignore_zero=False, toAnd=None, toOr=None):
        left = self._exp.get(toVar, toNum, toExp, ignore_zero=ignore_zero)
        # left = toExp(left)
        zero = toExp(toNum(0))
        if self._op == opCMP.EQ:
            return (left == zero)
        elif self._op == opCMP.GT:
            return (left >= toExp(toNum(1)))
        elif self._op == opCMP.GEQ:
            return (left >= zero)
        elif self._op == opCMP.LT:
            return (left <= toExp(toNum(-1)))
        elif self._op == opCMP.LEQ:
            return (left <= zero)

    def degree(self): return self._degree

    def get_variables(self):
        return self._vars[:]

    def is_true(self):
        if self._exp.is_constant():
            const = self._exp.get_coeff()
            return self._op.check(const, 0)
        return False

    def is_false(self):
        if self._exp.is_constant():
            const = self._exp.get_coeff()
            return not self._op.check(const, 0)
        return False

    def is_equality(self): return self._op == opCMP.EQ

    def get_independent_term(self): return self._exp.get_coeff()

    def get_coefficient(self, variable):
        return self._exp.get_coeff(variable)

    def isolate(self, variable):
        """
        returns the expression that corresponds to:
        variable = expression without variable
        if it is not equality raises a ValueError
        if the term with the variable has degree > 1 raises a ValueError
        """
        if self._op != opCMP.EQ:
            raise ValueError("isolate is only for equalities")
        var_coeff = self._exp.get_coeff(variable)
        if var_coeff == 0:
            return None
        if var_coeff != 1 and var_coeff != -1:
            raise ValueError("isolate can not divide by var coeffs")
        var_exp = Expression(var_coeff, opExp.MUL, variable)
        exp = (self._exp - var_exp) / (-var_coeff)
        if variable in exp.get_variables():
            raise ValueError("degree > 1")
        return exp

    def __eq__(self, other):
        if not isinstance(other, Constraint):
            raise ValueError("...")
        if self._op != other._op:
            return False
        e = self._exp - other._exp
        return e.is_constant() and e.get_coeff() == 0

    def toString(self, toVar, toNum, eq_symb="==", leq_symb="<=", geq_symb=">=", lt_symb="<", gt_symb=">",
                 neq_symb="!=", or_symb="OR", and_symb="AND", imp_symb="->", opformat="infix"):
        op = self._op.toString(eq_symb=eq_symb, leq_symb=leq_symb, geq_symb=geq_symb, lt_symb=lt_symb, gt_symb=gt_symb, neq_symb=neq_symb)
        if opformat == "prefix":
            return "({} {} 0)".format(op, self._exp.toString(toVar, toNum, opformat=opformat))
        else:
            return "{} {} 0".format(self._exp.toString(toVar, toNum), op)


class Implies(BoolExpression):

    def __init__(self, left, right):
        if(not isinstance(left, BoolExpression) or
           not isinstance(right, BoolExpression)):
            raise ValueError()
        self._left = left
        self._right = right

    def to_DNF(self):
        dnf_left = self._left.negate().to_DNF()
        dnf_right = self._right.to_DNF()
        return dnf_left + dnf_right

    def negate(self):
        return And(self._left, self._right.negate())

    def normalized(self, mode="int"):
        return Implies(self._left.normalized(mode=mode),
                       self._right.normalized(mode=mode))

    def renamed(self, old_names, new_names):
        return Implies(self._left.renamed(old_names, new_names),
                       self._right.renamed(old_names, new_names))

    def get(self, toVar, toNum, toExp=lambda x: x, ignore_zero=False, toAnd=None, toOr=None): raise NotImplementedError()

    def degree(self):
        return max(self._left.degree(), self._right.degree())

    def get_variables(self):
        return list(set(self._left.get_variables() + self._right.get_variables()))

    def is_true(self):
        return (self._left.is_false() or self._right.is_true())

    def is_false(self):
        return (self._left.is_true() and self._right.is_false())

    def toString(self, toVar, toNum, eq_symb="==", leq_symb="<=", geq_symb=">=", lt_symb="<", gt_symb=">",
                 neq_symb="!=", or_symb="OR", and_symb="AND", imp_symb="->"):
        txt_l = self._left.toString(toVar, toNum, eq_symb=eq_symb, leq_symb=leq_symb, geq_symb=geq_symb, lt_symb=lt_symb,
                                    gt_symb=gt_symb, neq_symb=neq_symb, or_symb=or_symb, and_symb=and_symb, imp_symb=imp_symb)
        txt_r = self._right.toString(toVar, toNum, eq_symb=eq_symb, leq_symb=leq_symb, geq_symb=geq_symb, lt_symb=lt_symb,
                                     gt_symb=gt_symb, neq_symb=neq_symb, or_symb=or_symb, and_symb=and_symb, imp_symb=imp_symb)
        return "{} {} {}".format(txt_l, imp_symb, txt_r)


class And(BoolExpression):

    def __init__(self, *params):
        exps = []
        for p in params:
            a = p
            if not isinstance(a, list):
                a = [p]
            for e in a:
                if not isinstance(e, BoolExpression):
                    print("why ", e, type(e))
                    raise ValueError("And only accepts boolean expressions")
                if isinstance(e, And):
                    for c in e._boolexps:
                        if c.is_true():
                            continue
                        exps.append(c)
                else:
                    if e.is_true():
                        continue
                    exps.append(e)

        self._boolexps = exps

    def len(self):
        return len(self._boolexps)

    def to_DNF(self):
        dnfs = [e.to_DNF() for e in self._boolexps]
        head = [[]]
        for dnf in dnfs:
            new_head = []
            for exp in dnf:
                new_head += [c + exp for c in head]
            head = new_head
        return head

    def negate(self):
        exps = []
        for e in self._boolexps:
            exps.append(e.negate())
        return Or(*exps)

    def normalized(self, mode="int"):
        return And([e.normalized(mode=mode) for e in self._boolexps])

    def renamed(self, old_names, new_names):
        return And([e.renamed(old_names, new_names) for e in self._boolexps])

    def get(self, toVar, toNum, toExp=lambda x: x, ignore_zero=False, toAnd=None, toOr=None):
        if len(self._boolexps) == 1:
            return self._boolexps[0].get(toVar, toNum, toExp=toExp, ignore_zero=ignore_zero, toAnd=toAnd, toOr=toOr)
        if toAnd is None:
            raise ValueError("undef action for And")
        return toAnd([e.get(toVar, toNum, toExp=toExp, ignore_zero=ignore_zero, toAnd=toAnd, toOr=toOr)
                      for e in self._boolexps])

    def degree(self):
        return max([e.degree() for e in self._boolexps])

    def get_variables(self):
        vars_ = []
        for e in self._boolexps:
            vars_ += e.get_variables()
        return list(set(vars_))

    def is_true(self):
        for e in self._boolexps:
            if not e.is_true():
                return False
        return True

    def is_false(self):
        for e in self._boolexps:
            if e.is_false():
                return True
        return False

    def toString(self, toVar, toNum, eq_symb="==", leq_symb="<=", geq_symb=">=", lt_symb="<", gt_symb=">",
                 neq_symb="!=", or_symb="OR", and_symb="AND", imp_symb="->"):
        token = " {} ".format(and_symb)
        return "({})".format(token.join([e.toString(toVar, toNum, eq_symb=eq_symb, leq_symb=leq_symb, geq_symb=geq_symb,
                                                    lt_symb=lt_symb, gt_symb=gt_symb, neq_symb=neq_symb, or_symb=or_symb,
                                                    and_symb=and_symb, imp_symb=imp_symb) for e in self._boolexps]))


class Or(BoolExpression):

    def __init__(self, *params):
        exps = []
        for p in params:
            a = p
            if not isinstance(a, list):
                a = [p]
            for e in a:
                if not isinstance(e, BoolExpression):
                    raise ValueError("Or only accepts boolean expressions")
                if isinstance(e, Or):
                    for c in e._boolexps:
                        exps.append(c)
                else:
                    exps.append(e)

        self._boolexps = exps

    def len(self):
        return len(self._boolexps)

    def to_DNF(self):
        dnfs = [e.to_DNF() for e in self._boolexps]
        head = []
        for dnf in dnfs:
            head += dnf
        return head

    def negate(self):
        exps = []
        for e in self._boolexps:
            exps.append(e.negate())
        return And(*exps)

    def normalized(self, mode="int"):
        return Or([e.normalized(mode=mode) for e in self._boolexps])

    def renamed(self, old_names, new_names):
        return Or([e.renamed(old_names, new_names) for e in self._boolexps])

    def get(self, toVar, toNum, toExp=lambda x: x, ignore_zero=False, toAnd=None, toOr=None):
        if len(self._boolexps) == 1:
            return self._boolexps[0].get(toVar, toNum, toExp=toExp, ignore_zero=ignore_zero, toAnd=toAnd, toOr=toOr)
        if toOr is None:
            raise ValueError("undef action for Or")
        return toOr([e.get(toVar, toNum, toExp=toExp, ignore_zero=ignore_zero, toAnd=toAnd, toOr=toOr)
                    for e in self._boolexps])

    def is_true(self):
        for e in self._boolexps:
            if e.is_true():
                return True
        return False

    def is_false(self):
        isFalse = True
        for e in self._boolexps:
            if not e.is_false():
                isFalse = False
        return isFalse

    def toString(self, toVar, toNum, eq_symb="==", leq_symb="<=", geq_symb=">=", lt_symb="<", gt_symb=">",
                 neq_symb="!=", or_symb="OR", and_symb="AND", imp_symb="->"):
        token = " {} ".format(or_symb)
        return "({})".format(token.join([e.toString(toVar, toNum, eq_symb=eq_symb, leq_symb=leq_symb, geq_symb=geq_symb,
                                                    lt_symb=lt_symb, gt_symb=gt_symb, neq_symb=neq_symb, or_symb=or_symb,
                                                    and_symb=and_symb, imp_symb=imp_symb) for e in self._boolexps]))
