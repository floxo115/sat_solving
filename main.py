from glob import glob


from dimacs_reader import DIMACSReader
from first_part import SimpleSolver
from second_part import DLPPSolver


def main():
    files = glob("./test-formulas/*.in")
    for file in files:
        print(f"solving file {file}", flush=True)
        dimacs_reader = DIMACSReader()
        dimacs_reader.read(file)

        solver1 = SimpleSolver(dimacs_reader.num_vars, dimacs_reader.clauses, timeout=10)
        solver2 = DLPPSolver(dimacs_reader.get_clauses(), timeout=10)
        try:
            is_sat1 = solver1.solve()
            is_sat2 = solver2.solve()
            print(is_sat1 == is_sat2)
            if is_sat1 != is_sat2:
                print(is_sat1, is_sat2)
                raise Exception()
        except TimeoutError:
            print("timeout")
        print()


if __name__ == "__main__":
    print("starting solver")
    main()
