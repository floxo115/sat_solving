class DIMACSReader:
    def __init__(self):
        self.num_vars = 0
        self.num_clauses = 0
        self.clauses = []

    def get_clauses(self):
        clauses = []
        for clause in self.clauses:
            new_clause = []
            for (polarity, variable) in clause:
                new_clause.append(polarity * (variable+1))
            clauses.append(new_clause)

        return clauses

    def read(self, fn:str):
        with open(fn, "r") as f:
            line = f.readline()
            line_split = line.split(" ")
            assert line_split[0] == "p"
            assert line_split[1] == "cnf"

            self.num_vars = int(line_split[2])
            self.num_clauses = int(line_split[3])

            while (line := f.readline()):
                literals = line.split(" ")
                assert literals[-1] == "0\n"
                literals = literals[:-1]

                clause = []
                for literal in literals:
                    literal = int(literal)
                    clause.append((1 if literal > 0 else -1, abs(literal) - 1)) # -1 to get the same index as for array indices
                
                self.clauses.append(clause)

            