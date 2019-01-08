from enum import Enum
from .Expressions import Expression
from .Expressions import ExprTerm
from .Expressions import opExp


class BoolExpression(object):

    def __init__(self, params): raise NotImplementedError()

    def to_DNF(self): raise NotImplementedError()

    def negate(self): raise NotImplementedError()

    def is_true(self): raise NotImplementedError()

    def is_false(self): raise NotImplementedError()

    def toString(self, toVar, toNum, eq_symb="==", leq_symb="<=", geq_symb=">=", lt_symb="<", gt_symb=">", neq_symb="!="): raise NotImplementedError()

    def degree(self): raise NotImplementedError()

    def get_variables(self): raise NotImplementedError()

    def is_linear(self):
        return self.degree() < 2

    def is_equality(self):
        return False

    def __repr__(self):
        return self.toString(str, int, eq_symb="==", leq_symb="<=", geq_symb=">=", lt_symb="<", gt_symb=">", neq_symb="!=")


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

    def __repr__(self):
        return self.toString()


class Constraint(BoolExpression):

    def __init__(self, left: Expression, op: opCMP, right: Expression = None):
        if(not isinstance(left, Expression) or
           (right is not None and not isinstance(right, Expression)) or
           (not isinstance(op, opCMP))):
            raise ValueError()
        exp = left
        a_op = op
        if right is not None:
            exp = exp - right
        neg = True
        for c, __ in exp._summands:
            if c > 0:
                neg = False
                break
        if neg:
            exp = 0 - exp
            a_op = a_op.oposite()
        self._exp = exp
        self._op = a_op
        self._vars = self._exp.get_variables()
        self._degree = self._exp.degree()

    def to_DNF(self): return Or(And(self))

    def negate(self):
        zero = ExprTerm(0)
        if self._op == opCMP.EQ:
            return Or(Constraint(self._exp, opCMP.GT, zero),
                      Constraint(self._exp, opCMP.LT, zero))
        return Constraint(self._exp, self._op.complement(), zero)

    def is_true(self): return False

    def is_false(self): return False

    def is_equality(self): return self._op == opCMP.EQ

    def degree(self): return self._degree

    def get_variables(self): return self._vars

    def get_independent_term(self): return self._exp.get_coeff()

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

    def get(self, toVar, toNum, toExp):
        left = self._exp.get(toVar, toNum, toExp)
        if isinstance(left, toNum):
            left = toExp(left)
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

    def transform(self, variables, lib):
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
            from z3 import Real

            def toVar(v):
                if v in variables:
                    return Real(v)
                else:
                    raise ValueError("{} is not a variable.".format(v))
            return self.get(toVar, int)
        else:
            raise ValueError("lib ({}) not supported".format(lib))

    def toString(self, toVar, toNum, eq_symb="==", leq_symb="<=", geq_symb=">=", lt_symb="<", gt_symb=">", neq_symb="!="):
        op = self._op.toString(eq_symb=eq_symb, leq_symb=leq_symb, geq_symb=geq_symb, lt_symb=lt_symb, gt_symb=gt_symb, neq_symb=neq_symb)
        return "{} {} 0".format(self._exp.toString(toVar, toNum), op)


class Implies(BoolExpression):

    def __init__(self, left, right):
        if(not isinstance(left, BoolExpression) or
           not isinstance(right, BoolExpression)):
            raise ValueError()
        self._left = left
        self._right = right

    def negate(self):
        return And(self._left, self._right.negate())

    def toDNF(self):
        dnf_left = self._left.negate().toDNF()
        dnf_right = self._right.toDNF()
        return dnf_left + dnf_right

    def __repr__(self):
        return str(self._left) + "->" + str(self._right)

    def isTrue(self):
        return (self._left.isFalse() or self._right.isTrue())

    def isFalse(self):
        return (self._left.isTrue() and self._right.isFalse())


class And(BoolExpression):

    def __init__(self, *params):
        for e in params:
            if not isinstance(e, BoolExpression):
                raise ValueError()
        self._boolexps = params

    def negate(self):
        exps = []
        for e in self._boolexps:
            exps.append(e.negate())
        return Or(*exps)

    def toDNF(self):
        dnfs = [e.toDNF() for e in self._boolexps]
        head = [[]]
        for dnf in dnfs:
            new_head = []
            for exp in dnf:
                new_head += [c + exp for c in head]
            head = new_head
        return head

    def __repr__(self):
        s = [str(e) for e in self._boolexps]
        return "(" + " /\ ".join(s) + ")"

    def isTrue(self):
        for e in self._boolexps:
            if not e.isTrue():
                return False
        return True

    def isFalse(self):
        for e in self._boolexps:
            if e.isFalse():
                return True
        return False


class Or(BoolExpression):

    def __init__(self, *params):
        for e in params:
            if not isinstance(e, BoolExpression):
                raise ValueError()
        self._boolexps = params

    def negate(self):
        exps = []
        for e in self._boolexps:
            exps.append(e.negate())
        return And(*exps)

    def toDNF(self):
        dnfs = [e.toDNF() for e in self._boolexps]
        head = []
        for dnf in dnfs:
            head += dnf
        return head

    def isTrue(self):
        for e in self._boolexps:
            if e.isTrue():
                return True
        return False

    def isFalse(self):
        isfalse = True
        for e in self._boolexps:
            if not e.isFalse():
                isfalse = False
        return isfalse

    def __repr__(self):
        s = [str(e) for e in self._boolexps]
        return "(" + " \/ ".join(s) + ")"


class Not(BoolExpression):

    def __init__(self, exp):
        if isinstance(exp, BoolExpression):
            self._exp = exp
        else:
            raise ValueError()

    def negate(self): return self._exp

    def toDNF(self):
        neg_exp = self._exp.negate()
        return neg_exp.toDNF()

    def __repr__(self):
        return "not(" + str(self._exp) + ")"

    def isTrue(self):
        return self._exp.isFalse()

    def isFalse(self):
        return self._exp.isTrue()
