from itertools import product
from time import perf_counter

class SimpleSolver:
    def __init__(self, num_variables, clauses, timeout=float("inf")):
        self.num_variables = num_variables
        self.clauses = clauses
        self.model = []

        self.timeout = timeout

    def solve(self):
        start_time = perf_counter()
        for assignment in  product([0,1], repeat=self.num_variables):
            if perf_counter() - start_time > self.timeout:
                raise TimeoutError()
            for clause in self.clauses:
                clause_val = False
                for literal in clause:
                    val = bool(assignment[literal[1]])
                    if literal[0] == -1:
                        val = not val
                    if val is True:
                        clause_val = True
                        break
                
                if clause_val is False:
                    break
            else:
                self.model = assignment
                return True
        return False