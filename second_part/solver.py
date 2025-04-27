import time
from typing import Iterable, Dict
from enum import Enum
from random import choice

class Status(Enum):
    SATISFIED = 1
    CONTRADICTION = 2
    UNSATURATED = 3

class ImpossibleAssignmentError(Exception):
    pass


class Clause:
    def __init__(self, literals: Iterable[int]):
        # if len(literals) == 0:
        #     raise ValueError("literals can not be empty")
        self.literals = list(literals)

        self.watch_pointer1 = 0
        self.watch_pointer2 = 1 if len(self.literals) > 1 else 0

    def is_sat(self, assignment: Dict[int, bool]) -> Status:
        if len(self.literals) == 0:
            return Status.CONTRADICTION

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
        if len(self.literals) == 0:
            return None

        # if the clause is a unit clause we just return the variable and an assignment
        # that makes the literal True
        if self.watch_pointer1 == self.watch_pointer2:
            lit_polarity = -1 if self.literals[self.watch_pointer1] < 0 else 1
            return abs(self.literals[self.watch_pointer1]), lit_polarity > 0

        if abs(self.literals[self.watch_pointer2]) not in assignment.keys():
            self.watch_pointer2, self.watch_pointer1 = self.watch_pointer1, self.watch_pointer2

        # it is assumed that the watch pointers were set with set_watch pointers before
        # if the second watch pointer's literal is True or unassigned we can not infer anything
        if (
            abs(self.literals[self.watch_pointer2]) not in assignment.keys()
            or assignment[abs(self.literals[self.watch_pointer2])] == self.literals[self.watch_pointer2] > 0
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
        # if len(clauses) == 0:
        #     raise ValueError("literals can not be empty")
        
        self.clauses = [Clause(literals) for literals in clauses]
        self.variables = set()
        for clause in self.clauses:
            self.variables.update([abs(lit) for lit in clause.literals])
        self.assignment = {}
        self.decision_level = 0
        self.variable_stack = []
        self.backtracking_stack = [0] # having the first element set to -1 makes indexing with the decision level easier

        self.timeout = timeout
    def is_sat(self, assignment: Dict[int, bool]) -> Status:
        is_at_least_one_clause_unsaturated = False
        
        for clause in self.clauses:
            clause_status = clause.is_sat(assignment)
            if clause_status == Status.CONTRADICTION:
                return Status.CONTRADICTION
            elif clause_status == Status.UNSATURATED:
                is_at_least_one_clause_unsaturated = True
            
        if not is_at_least_one_clause_unsaturated:
            return Status.SATISFIED

        return Status.UNSATURATED
    
    def add_decision(self, variable: int, value: bool):
        if variable <= 0:
            raise ValueError("variable has to be greater than 0")
        if variable not in self.variables:
            raise ValueError("assignment is not possible, since the variable is not contained in the formula")
        if variable in self.assignment.keys():
            raise ValueError("assigned variables can not be assigned again")
        
        self.decision_level += 1
        self.variable_stack.append(variable)
        self.backtracking_stack.append(len(self.variable_stack))
        
        self.assignment[variable] = value

        for clause in self.clauses:
            clause.set_watchers(self.assignment, variable)

    def backtrack(self):
        if self.decision_level == 0:
            return
        
        to_remove_variables = self.variable_stack[self.backtracking_stack[-2]:]
        for variable in to_remove_variables:
            del self.assignment[variable]
        
        self.variable_stack = self.variable_stack[:self.backtracking_stack[-2]]
        self.backtracking_stack = self.backtracking_stack[:-1]
        self.decision_level -= 1
        
    def bcp(self) -> Dict[int, bool]:
        forced_assignments = {}
        for clause in self.clauses:
            if clause.is_sat(self.assignment) == Status.SATISFIED:
                continue
            clause_forced_assignment = clause.bcp(self.assignment)
            if clause_forced_assignment is None:
                continue

            if clause_forced_assignment[0] in forced_assignments.keys()\
                and clause_forced_assignment[1] is not forced_assignments[clause_forced_assignment[0]]:
                raise ImpossibleAssignmentError("bcp forces different assignments of same variable")
            elif clause_forced_assignment[0] in self.assignment.keys()\
                and clause_forced_assignment[1] is not self.assignment[clause_forced_assignment[0]]:
                raise ImpossibleAssignmentError("bcp forces that violates previous assignments")
            
            else:
                forced_assignments[clause_forced_assignment[0]] = clause_forced_assignment[1]
        
        self.__add_forced_assignment(forced_assignments)
        return forced_assignments
    
    def __add_forced_assignment(self, assignment: Dict[int, bool]):
        # here I assume that everything is correct because it is only used in bcp and
        # there I already checked the validity of the forced assignment
        for variable, value in assignment.items():
            self.variable_stack.append(variable)
            
            self.assignment[variable] = value

            for clause in self.clauses:
                clause.set_watchers(self.assignment, variable)

    def solve(self):
        start_time = time.perf_counter()
        variables = self.variables.copy()
        variable_stack = []
        while True:
            if time.perf_counter() - start_time > self.timeout:
                raise TimeoutError("Timed out")
            while True:
                try:
                    forced_assignments = self.bcp()
                    #print(forced_assignments)
                except ImpossibleAssignmentError:
                    break
                if forced_assignments == {}:
                    break

            if self.is_sat(self.assignment) == Status.SATISFIED:
                return True

            elif self.is_sat(self.assignment) == Status.CONTRADICTION:
                if len(variable_stack) == 0:
                    return False

                variable, dl = variable_stack.pop()
                while self.decision_level != dl:
                    self.backtrack()

                try:
                    self.add_decision(variable, False)
                except ImpossibleAssignmentError:
                    pass
            elif self.is_sat(self.assignment) == Status.UNSATURATED:
                variable = None
                for var in sorted(variables):
                    if var not in self.assignment:
                        variable = var
                        break
                if variable is None:
                    # No variables left unassigned, should not happen normally here
                    raise ValueError("No unassigned variables found")
                variable_stack.append((variable, self.decision_level))
                #print(variable, self.decision_level)
                try:
                    self.add_decision(variable, True)
                except ImpossibleAssignmentError:
                    pass



    







            


