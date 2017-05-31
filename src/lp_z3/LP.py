import ppl
import z3

class Variable(ppl.Variable):
    def imhere(self):
        pass
class Linear_Expression(ppl.Linear_Expression):
    def imhere(self):
        pass
class Constraint(ppl.Constraint):
    def imhere(self):
        pass
class Constraint_System:
    def __init__(self,c=[]):
        if(isinstance(c,ppl.Constraint)):
            self.cons = [c]
        elif(isinstance(c,list)):
            self.cons = c
        else:
            raise ValueError("Constraint or list of Constraints")
    def insert(self, c):
        self.cons.append(c)

    def has_strict_inequalities(self):
        for c in self.cons:
            if(c.is_strict_inequality()):
                return True
        return False
    def has_equalities(self):
        for c in self.cons:
            if(c.is_equality()):
                return True
        return False

    def empty(self):
        return len(self.cons)==0

    def clear(self):
        self.cons = []


class Polyhedron:
    def add_constrain():
        pass
