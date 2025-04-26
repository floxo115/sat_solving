from typing import Iterable, Dict
from enum import Enum

class Status(Enum):
    SATISFIED = 1
    CONTRADICTION = 2
    UNSATURATED = 3



class Clause:
    def __init__(self, literals: Iterable[int]):
        if len(literals) == 0:
            raise ValueError("literals can not be empty")
        self.literals = list(literals)

        self.watch_pointer1 = 0
        self.watch_pointer2 = 1 if len(self.literals) > 1 else 0

    def is_sat(self, assignment: Dict[int, bool]) -> Status:
        checked_literal_counter = 0 
        for literal in self.literals:
            if abs(literal) in assignment.keys():
                checked_literal_counter += 1
                val = assignment[abs(literal)]
                if literal > 0 and val or literal < 0 and not val:
                    return Status.SATISFIED

        if checked_literal_counter == len(self.literals):
            return Status.CONTRADICTION
        elif checked_literal_counter < len(self.literals):
            return Status.UNSATURATED

    def set_watchers(self, assignment: Dict[int, bool], new_variable: int):
        if new_variable <= 0:
            raise ValueError("new variable can not be smaller than 1")
        if new_variable not in assignment.keys():
            raise ValueError("new variable has to be in assignment")

        # if the literal is already unit, we have do nothing
        if self.watch_pointer1 == self.watch_pointer2:
            return

        # if the new variable is watched by watch pointer 2 we swap the pointers
        # so that always watch pointer 1 points to the new variable if any watch pointer
        # points to it at all
        if new_variable == abs(self.literals[self.watch_pointer2]):
            self.watch_pointer1, self.watch_pointer2 = (
                self.watch_pointer2,
                self.watch_pointer1,
            )

        # if no watch pointer points to the new variable do nothing and return
        if new_variable != abs(self.literals[self.watch_pointer1]):
            return

        # lit_val gives us the value of the literal watched by watch pointer 1 under the current assignment
        lit_polarity = -1 if self.literals[self.watch_pointer1] < 0 else 1
        lit_val = lit_polarity * assignment[abs(self.literals[self.watch_pointer1])]

        # if the literal value pointed by watch pointer 1 is becoming True: do nothing
        if lit_val:
            return

        # from here on we assume that the new variable assignment makes the literal
        # watched by watch pointer 1 False

        # and because of that we need to find a new non assigned and non non watched literal
        for i, literal in enumerate(self.literals):
            if abs(literal) not in assignment.keys() and self.watch_pointer2 != i:
                self.watch_pointer1 = i
                break

    def bcp(self, assignment: Dict[int, bool]):
        # if the clause is a unit clause we just return the variable and an assignment
        # that makes the literal True
        if self.watch_pointer1 == self.watch_pointer2:
            lit_polarity = -1 if self.literals[self.watch_pointer1] < 0 else 1
            return abs(self.literals[self.watch_pointer1]), lit_polarity > 0

        # it is assumed that the watch pointers were set with set_watch pointers before
        # if the second watch pointer's literal is True or unassigned we can not infer anything
        if (
            abs(self.literals[self.watch_pointer2]) not in assignment.keys()
            or assignment[abs(self.literals[self.watch_pointer2])]
        ):
            return None

        # if the first watch pointer points to a literal that is assigned also do nothing
        if abs(self.literals[self.watch_pointer1]) in assignment.keys():
            return None

        # now we check if there are still unassigned and unwatched literals in the clause.
        # If not the literal watched by watch pointer 1 has to be True.
        for i, literal in enumerate(self.literals):
            if i in [self.watch_pointer1, self.watch_pointer2]:
                continue
            elif abs(literal) not in assignment.keys():
                return None

            # if the current literals is true under the assignment then we can infer nothing
            lit_polarity = -1 if literal < 0 else 1
            is_assignment_true = 1 if assignment[abs(literal)] > 0 else -1
            if lit_polarity * is_assignment_true > 0:
                return None

        # lit_val gives us the value of the literal watched by watch pointer 1 under the current assignment
        lit_polarity = -1 if self.literals[self.watch_pointer1] < 0 else 1
        return abs(self.literals[self.watch_pointer1]), lit_polarity > 0


class DLPPSolver:
    def __init__(self, clauses: list[int], timeout=float("inf")):
        if len(clauses) == 0:
            raise ValueError("literals can not be empty")
        
        self.clauses = [Clause(literals) for literals in clauses]
        self.assignment = {}
        self.decision_level = 0
        self.variable_stack = []
        self.backtracking_stack = []

    def is_sat(self, assignment: Dict[int, bool]) -> bool:
        for clause in self.clauses:
            if not clause.is_sat(assignment):
                return False
        
        return True


