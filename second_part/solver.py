import time
from typing import Iterable, Dict, List, Tuple, Optional
from enum import Enum

class Status(Enum):
    """
    Enum for specifying the status of Clauses and CNFs.

    SATISFIED: The object is satisfied under the given assignment\n
    CONTRADICTION: The object is unsatisfiable under the given assignment\n
    UNSATURATED: The status of the object is not decided under the given assignment\n
    """
    SATISFIED = 1
    CONTRADICTION = 2
    UNSATURATED = 3

class ImpossibleAssignmentError(Exception):
    """
    Exception raised when an assignment is impossible. E.g. not A should be assigned while A is already assigned
    """
    def __init__(self, message):
        super().__init__()



class Clause:
    """
    A Clause to be used to compose CNFs e.g. (A OR B OR not C)
    """
    def __init__(self, literals: List[int]):
        """
        Initializes the Clause
        :param literals: The literals that compose the Clause. E.g.: [-1, -3, 2, 10,...]
        """
        self.literals = list(literals)

        # if the clause is not only one literal the watchpointers should point to the first and second locations
        if len(literals) > 1:
            self.watch_pointer1 = 0
            self.watch_pointer2 = 1
        # if the clause is a unit then the watch pointers should only point to the first element
        elif len(literals) == 1:
            self.watch_pointer1 = self.watch_pointer2 = 0

        # if the clause is empty it is always false and no watch pointers are needed

    def is_sat(self, assignment: Dict[int, bool]) -> Status:
        """
        Checks if the Clause is satisfied given the assignment.
        :param assignment: The assignment the Clause is checked against.
        :return: Status of the Clause. As specified in the Status Enum.
        """

        # if the length of the clause is zero it is always false (Definition of the empty conjunction)
        if len(self.literals) == 0:
            return Status.CONTRADICTION

        # the literals of the clause are checked if they are in the assignment and if they are
        # it is checked if they resolve to true. If they do the clause is satisfied under the assignment
        # and SATISFIED is returned
        checked_literal_counter = 0
        for literal in self.literals:
            if abs(literal) in assignment.keys():
                checked_literal_counter += 1
                val = assignment[abs(literal)]
                if literal > 0 and val or literal < 0 and not val:
                    return Status.SATISFIED

        # if not all literals of the clause are found in the assignment there is still hope to make it true
        if checked_literal_counter < len(self.literals):
            return Status.UNSATURATED

        # if all literals were checked all hope is lost and the clause is false under the assignment
        return Status.CONTRADICTION

    def set_watchers(self, assignment: Dict[int, bool], new_variable: int):
        """
        Updates the watch pointers in-place following the assignment of a new variable.
        :param assignment: A given assignment of variables
        :param new_variable: The last updated variable in the assignment
        """

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

        # and because of that we need to find a new not assigned and not watched literal
        for i, literal in enumerate(self.literals):
            if abs(literal) not in assignment.keys() and self.watch_pointer2 != i:
                self.watch_pointer1 = i
                break

    def bcp(self, assignment: Dict[int, bool]) -> Optional[Tuple[int, bool]]:
        """
        Runs on iteration of BCP on the Clause given the assignment.
        This does not give all assignments that are effected by the given assignment.
        For all effected assignments this has for be run in a loop until no new assignments
        are effected.
        :param assignment: The assignment that BCP is run against
        :return: The assignment of all variables that are effected by the given assignment
        """
        # if the literal is
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
    """
    A non-recursive DPLL Solver that uses watch literals to speed up BCP
    """
    def __init__(self, clauses: List[list[int]], timeout=float("inf")):
        # if len(clauses) == 0:
        #     raise ValueError("literals can not be empty")

        # constructs the clauses and saves them in a list
        self.clauses = [Clause(literals) for literals in clauses]

        # stores all variables that appear in the clauses and stores them in a set
        self.variables = set()
        for clause in self.clauses:
            self.variables.update([abs(lit) for lit in clause.literals])

        self.assignment = {}
        self.decision_level = 0

        # the variable stack stores all variables assigned by decision and by bcp so that they can be undone
        # in the correct order
        self.variable_stack = []

        # the backtracking relates the decision levels to the indices in the variable stack
        # The first element is the starting signifies the variables that are forced by the initial BCP
        self.backtracking_stack = [0]

        self.timeout = timeout
        self.num_decisions = 0

    def is_sat(self) -> Status:
        """
        Checks if the current assignment
        :param assignment:
        :return:
        """

        is_at_least_one_clause_unsaturated = False

        # iterate through all clauses and if one clause is false under the assignment
        # then CONTRADICTION is returned. If not and all variables that appear in all clauses are
        # assigned then the CNF is true. If not all variables are assigned, then the CNF is not yet decided
        for clause in self.clauses:
            clause_status = clause.is_sat(self.assignment)
            if clause_status == Status.CONTRADICTION:
                return Status.CONTRADICTION
            elif clause_status == Status.UNSATURATED:
                is_at_least_one_clause_unsaturated = True
            
        if not is_at_least_one_clause_unsaturated:
            return Status.SATISFIED

        return Status.UNSATURATED
    
    def add_decision(self, variable: int, value: bool):
        """
        Adds a decision variable to the solver.
        :param variable:  The variable to add.
        :param value: The value of the variable to add: {True, False}
        """
        if variable <= 0:
            raise ValueError("variable has to be greater than 0")
        if variable not in self.variables:
            raise ValueError("assignment is not possible, since the variable is not contained in the formula")
        if variable in self.assignment.keys():
            raise ValueError("assigned variables can not be assigned again")

        self.num_decisions += 1

        # we increase the decision level by 1 and add the new variable to the stack. Further we append a new element
        # to the backtracking stack and set it to the length of the variable stack, so that it points to the end
        # of the variable stack
        self.decision_level += 1
        self.variable_stack.append(variable)
        self.backtracking_stack.append(len(self.variable_stack))

        # the variable and its value are added to the current assignment
        self.assignment[variable] = value

        # we also need to reset the watch pointers for each clause ... could be improved by tracking the relations
        # of clauses and variables
        for clause in self.clauses:
            clause.set_watchers(self.assignment, variable)

    def backtrack(self):
        """
        Resets the state of the Solver to the state before the previous decision.
        :return:
        """

        # if decision level is zero, the method is idempotent
        if self.decision_level == 0:
            return

        # we retrieve all variables in the assignment that we need to remove with the help of the variable stack and the
        # backtracking stack. We then remove them peu a peu.
        to_remove_variables = self.variable_stack[self.backtracking_stack[-2]:]
        for variable in to_remove_variables:
            del self.assignment[variable]

        # Also the variable stack and the backtracking stack have to be popped respectively
        self.variable_stack = self.variable_stack[:self.backtracking_stack[-2]]
        self.backtracking_stack = self.backtracking_stack[:-1]

        # the decision level is also decreased by 1
        self.decision_level -= 1
        
    def bcp(self) -> Dict[int, bool]:
        """
        This runs a single loop of BCP on the CNF. To get all forced assignments
        this needs to be run until {} is returned.
        :return: The forced assignments from a single iteration of BCP
        """

        forced_assignments = {}

        for clause in self.clauses:
            # if the clause is satisfied, we can simply go on to the next clause
            if clause.is_sat(self.assignment) == Status.SATISFIED:
                continue

            # we retrieve the forced assignments from the clause and if it is empty we go to the next clause
            clause_forced_assignment = clause.bcp(self.assignment)
            if clause_forced_assignment is None:
                continue

            # if one clause forces an assignment of one variable and another clause forces an assignment of different
            # polarity of the same variable we have a conflict an throw an Exception
            if clause_forced_assignment[0] in forced_assignments.keys()\
                and clause_forced_assignment[1] is not forced_assignments[clause_forced_assignment[0]]:
                raise ImpossibleAssignmentError("bcp forces different assignments of same variable")

            # I think this can be removed, because if something was assigned prior to bcp it should not be able to
            # assign it again via bcp
            elif clause_forced_assignment[0] in self.assignment.keys()\
                and clause_forced_assignment[1] is not self.assignment[clause_forced_assignment[0]]:
                raise ImpossibleAssignmentError("bcp forces that violates previous assignments")

            # if we found some forced variable assignment we add it to the forced assignment dict
            else:
                forced_assignments[clause_forced_assignment[0]] = clause_forced_assignment[1]

        # this is a helper to add the forced assignment to the assignment of the solver and also to update the
        # watch literals of the clauses
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

    def get_model(self) -> Dict[int, bool]:
        """
        Returns the constructed model of the solver.
        :return: The assignment of the solver if it found a solution; {} else
        """
        return self.assignment if self.is_sat() == Status.SATISFIED else {}

    def get_num_decisions(self):
        """
        Gets the number of decision made during the solving process.
        :return: Number of decisions made during the solving process.
        """
        return self.num_decisions

    def solve(self)->bool:
        """
        Non-recursive implementation of DPLL.
        :return: True if a model was found, False otherwise.
        """
        start_time = time.perf_counter()

        variables = self.variables.copy()
        variable_stack = []
        while True:
            if time.perf_counter() - start_time > self.timeout:
                raise TimeoutError("Timed out")
            while True:
                try:
                    contradiction_by_bcp = False
                    forced_assignments = self.bcp()
                    #print(forced_assignments)

                # if an impossible assignment is forced by bcp we set a flag so that we go on like the state of the
                # solver is CONTRADICTION
                except ImpossibleAssignmentError:
                    contradiction_by_bcp = True
                    break

                # if no further forced assignment was found we can go on to the next step
                if forced_assignments == {}:
                    break

            # if we found a model we return it
            if self.is_sat() == Status.SATISFIED:
                return True

            # if we found a contradiction (either by the current assignment or via bcp) we *
            elif self.is_sat() == Status.CONTRADICTION or contradiction_by_bcp:
                # * either return that no model exists when there is nothing more to do
                if len(variable_stack) == 0:
                    return False

                # * or backtrack and use the top variable from the stack and add it again as a decision with
                # the opposite polarity
                variable, dl = variable_stack.pop()
                while self.decision_level != dl:
                    self.backtrack()

                try:
                    self.add_decision(variable, False)

                # I think this can also be removed, since we check below if the variable is already in the assignment
                except ImpossibleAssignmentError:
                    pass

            # if the state of the cnf is not decided yet, *
            elif self.is_sat() == Status.UNSATURATED:

                # we add a decision variable ... maybe something more refined could be used here ... to the stack
                # and also add it to the assignment
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

                # like above I think this can be removed
                except ImpossibleAssignmentError:
                    pass



    







            


