from itertools import product
from time import perf_counter
from typing import Dict


class SimpleSolver:
    def __init__(self, clauses, timeout=float("inf")):
        """
        Initialize the solver.
        :param clauses: a list of clauses of the form [[(polarity, variable), ...], ...] e.g. [[(1, 5),...],...]
        :param timeout: (optional) timeout in seconds
        """
        # get the number of variables
        variables = {}
        for clause in clauses:
            for literal in clause:
                variables[literal[1]] = True
        self.num_variables = len(variables)


        self.clauses = clauses
        self.model = []
        self.num_decisions = 0

        self.timeout = timeout

    def solve(self) -> bool:
        """
        Solves the given SAT problem
        :return: True if a model was found, False else
        """
        start_time = perf_counter()

        # tries all possible assignments by iterating over all lists with elements out of {0,1} of length n
        for assignment in  product([0,1], repeat=self.num_variables):
            # every new assignment can be seen as a decision
            self.num_decisions += 1

            if perf_counter() - start_time > self.timeout:
                raise TimeoutError()

            # each clause is tested against the assignment
            for clause in self.clauses:

                # each clause is asserted to be not satisfied
                clause_val = False
                for literal in clause:
                    # if one literal is True by the assignment the clause is true
                    # and the next clause can be checked
                    val = bool(assignment[literal[1]])
                    if literal[0] == -1:
                        val = not val
                    if val is True:
                        clause_val = True
                        break

                # if one clause is false by the assignment the whole CNF is false
                if clause_val is False:
                    break
            else:
                # if there was no clause that was false under the assignment
                # the current assignment is a model for the CNF
                self.model = assignment
                return True

        # if all possibilities were exhausted there is no model for the CNF and it is unsatisfiable
        return False

    def get_num_decisions(self) -> int:
        """
        Returns the number of decisions made
        :return: number of decisions
        """
        return self.num_decisions

    def get_model(self) -> Dict[int, bool]:
        """
        Returns the model
        :return: The model. Empty dictionary if no model was found
        """
        model = {}
        for i, value in enumerate(self.model):
            model[i + 1] = value == 1

        return model
