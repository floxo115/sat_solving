import pytest
from second_part.solver import DLPPSolver, ImpossibleAssignmentError

def test_init_with_valid_input():
    solver = DLPPSolver([[1,-2,3,-4,5], [-1], [-10,20,-30,40], [-40, 50]])
    assert solver.assignment == {}
    assert solver.backtracking_stack == [0]
    assert solver.variable_stack == []
    assert solver.decision_level == 0
    assert solver.variables == set([1,2,3,4,5, 10,20,30,40,50])

def test_init_with_empty_clause():
    with pytest.raises(ValueError):
        DLPPSolver([[1,-2,3,-4,5], [], [-10,20,-30,40], [-40, 50]])

def test_init_with_empty_cnf():
    with pytest.raises(ValueError):
        DLPPSolver([])

def test_add_decision_with_valid_variables():
    solver = DLPPSolver([[1,-2,3,-4,5], [0], [-10,20,-30,40], [-40, 50]])
    solver.add_decision(50, True)
    assert solver.decision_level == 1
    assert solver.backtracking_stack == [0, 1]
    assert solver.variable_stack == [50]
    assert solver.assignment == {50: True}

    solver.add_decision(1, False)
    assert solver.decision_level == 2
    assert solver.backtracking_stack == [0, 1, 2]
    assert solver.variable_stack == [50, 1]
    assert solver.assignment == {50: True, 1: False}

    solver.add_decision(20, False)
    assert solver.decision_level == 3
    assert solver.backtracking_stack == [0, 1, 2, 3]
    assert solver.variable_stack == [50, 1, 20]
    assert solver.assignment == {50: True, 1: False, 20: False}

def test_add_assignment_with_variable_not_in_cnf():
    solver = DLPPSolver([[1,-2,3,-4,5], [-1], [-10,20,-30,40], [-40, 50]])
    with pytest.raises(ValueError):
        solver.add_decision(100, True)

def test_add_assignment_with_impossible_variable():
    solver = DLPPSolver([[1,-2,3,-4,5], [-1], [-10,20,-30,40], [-40, 50]])
    with pytest.raises(ValueError):
        solver.add_decision(-100, True)

def test_add_assignment_with_already_assigned_variable():
    solver = DLPPSolver([[1,-2,3,-4,5], [-1], [-10,20,-30,40], [-40, 50]])
    solver.add_decision(40, True)
    with pytest.raises(ValueError):
        solver.add_decision(40, True)

def test_add_assignment_after_bcp_with_forced_assignments():
    solver = DLPPSolver([[1,-2,3,-4,5], [-1], [-10,20,-30,40],[10], [20], [-40, 50]])
    solver.bcp()
    solver.add_decision(40, True)
    assert solver.decision_level == 1
    assert solver.backtracking_stack == [0, 4]

def test_backtrack_from_zero_decision_level():
    solver = DLPPSolver([[1,-2,3,-4,5], [-1], [-10,20,-30,40], [-40, 50]])
    solver.backtrack()
    assert solver.assignment == {}
    assert solver.backtracking_stack == [0]
    assert solver.variable_stack == []
    assert solver.decision_level == 0

def test_backtrack_from_3_decision_levels():
    solver = DLPPSolver([[1,-2,3,-4,5], [-1], [-10,20,-30,40], [-40, 50]])
    solver.add_decision(1, True)
    solver.add_decision(2, False)
    solver.add_decision(40, False)
    solver.backtrack()

    assert solver.assignment == {1: True, 2: False}
    assert solver.backtracking_stack == [0, 1, 2]
    assert solver.variable_stack == [1, 2]
    assert solver.decision_level == 2

    solver.backtrack()
    assert solver.assignment == {1: True}
    assert solver.backtracking_stack == [0, 1]
    assert solver.variable_stack == [1]
    assert solver.decision_level == 1

    solver.backtrack()
    assert solver.assignment == {}
    assert solver.backtracking_stack == [0]
    assert solver.variable_stack == []
    assert solver.decision_level == 0

# def test_backtrack_from_3_levels_with_bcp():
#     solver = DLPPSolver([[1,-10, -20], [-1], [-10,20,-30,40],[10], [20], [-40, 50]])
#     solver.bcp()
#     solver.add_decision(40, True)
#     solver.backtrack()

def test_bcp_from_unit_clauses():
    solver = DLPPSolver([[1,-2,3,-4,5], [-1], [-10,20,-30,40], [10], [100], [-40, 50]])
    forced_assignments = solver.bcp()
    assert forced_assignments == {1: False, 10: True, 100: True}
    assert solver.backtracking_stack == [0]

def test_bcp_from_units_with_impossible_forced_assignments():
    solver = DLPPSolver([[1,-2,3,-4,5], [-1], [-10,20,-30,40], [10], [-10], [-40, 50]])
    with pytest.raises(ImpossibleAssignmentError):
        solver.bcp()

def test_bcp_from_units_with_contradiction_to_previous_assignments():
    solver = DLPPSolver([[1,-2,3,-4,5], [-1], [-10,20,-30,40], [10], [-40, 50]])
    solver.add_decision(10, False)
    with pytest.raises(ImpossibleAssignmentError):
        solver.bcp()

def test_bcp_with_multiple_steps():
    solver = DLPPSolver([[1, -10, 100], [-1], [-10,20,-30,40], [10], [-40, 50]])
    solver.bcp()
    for var in [1,10]:
        assert var in solver.variable_stack
    assert solver.decision_level == 0
    assert solver.backtracking_stack == [0]
    solver.add_decision(20, True)
    assert solver.decision_level == 1
    assert solver.backtracking_stack == [0, 3]
    solver.bcp()
    for var in [1, 10, 20, 100]:
        assert var in solver.variable_stack
    assert solver.decision_level == 1
    assert solver.backtracking_stack == [0, 3]
    solver.add_decision(40, True)
    solver.bcp()
    for var in [1, 10, 20, 100, 50]:
        assert var in solver.variable_stack
    assert solver.decision_level == 2
    assert solver.backtracking_stack == [0, 3, 5]


        