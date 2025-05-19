import pytest
from .solver import Clause, Status

def test_init_clause():
    clause = Clause([-1,2,-6, 10])
    assert clause.literals == [-1,2,-6, 10]
    assert clause.watch_pointer1 == 0
    assert clause.watch_pointer2 == 1

def test_init_clause_with_one_literal():
    clause = Clause([-1])
    assert clause.literals == [-1]
    assert clause.watch_pointer1 == 0
    assert clause.watch_pointer2 == 0

# def test_init_clause_with_no_literal():
#     with pytest.raises(ValueError):
#         Clause([])

def test_is_sat_with_true_assignment():
    clause = Clause([-1,2,-6, 10])
    assignment = {1:True, 2: False, 6: False}
    assert clause.is_sat(assignment) == Status.SATISFIED

def test_is_sat_with_false_assignment():
    clause = Clause([-1,2,-6, 10])
    assignment = {1:True, 2: False, 6: True, 10: False}
    assert clause.is_sat(assignment) == Status.CONTRADICTION

def test_is_sat_with_no_assignment():
    clause = Clause([-1,2,-6, 10])
    assignment = {2:False, 1: True}
    assert clause.is_sat(assignment) == Status.UNSATURATED

def test_watched_literals_with_unit_clause():
    clause = Clause([-1])
    assert clause.watch_pointer1 == clause.watch_pointer2 == 0

def test_set_watched_literals_no_assignment_to_them():
    clause = Clause([-1,2,-6, 10])
    clause.watch_pointer1 = 2
    clause.watch_pointer2 = 1
    clause.set_watchers({1: True, 10: False},  10)
    assert clause.watch_pointer1 == 2
    assert clause.watch_pointer2 == 1

def test_set_watched_literals_true_assignment():
    clause = Clause([-1,2,-6, 10])
    clause.watch_pointer1 = 2
    clause.watch_pointer2 = 1
    clause.set_watchers({1: True, 10: False, 2: True},  2)
    # they swap because watch pointer 1 can only point to new variable assignment
    assert clause.watch_pointer1 == 1
    assert clause.watch_pointer2 == 2

    clause = Clause([-1,2,-6, 10])
    clause.watch_pointer1 = 2
    clause.watch_pointer2 = 1
    clause.set_watchers({1: True, 10: False, 6: False},  6)
    # nothing happens
    assert clause.watch_pointer1 == 2
    assert clause.watch_pointer2 == 1

def test_set_watched_literals_false_assignment_with_open_literals():
    clause = Clause([-1,2,-6, 10])
    clause.watch_pointer1 = 2
    clause.watch_pointer2 = 1
    clause.set_watchers({6:False},  6)
    # watch pointer has to go to new position 0
    assert clause.watch_pointer1 == 0
    assert clause.watch_pointer2 == 1

    clause = Clause([-1,2,-6, 10])
    clause.watch_pointer1 = 2
    clause.watch_pointer2 = 1
    clause.set_watchers({1: False, 6:False},  6)
    # watch pointer has to go to new position 3
    assert clause.watch_pointer1 == 3
    assert clause.watch_pointer2 == 1 

def test_bcp_with_unit_clause():
    clause = Clause([-1])
    assert clause.bcp({2: True}) == (1, False)

def test_bcp_with_pointer_to_true():
    clause = Clause([-1,2,-6, 10])
    clause.set_watchers({1:False, 2: True}, 2)
    bcp_res = clause.bcp({1:False, 2: True})
    # if watch pointer points to a True literal nothing should happen
    assert bcp_res is None

def test_bcp_with_pointer_to_false():
    clause = Clause([-1,2,-6, 10])
    clause.set_watchers({1:False, 2: False}, 2)
    bcp_res = clause.bcp({1:False, 2: False})
    assert bcp_res is None

def test_bcp_with_pointer_unassigned_and_other_pointer_false_and_rest_false():
    clause = Clause([-1,2,-6, 10])
    clause.set_watchers({1:False, 2: False, 10: False}, 2)
    bcp_res = clause.bcp({1:False, 2: False, 10: False})
    assert bcp_res == (6, False)

def test_bcp_with_pointer_unassigned_and_other_pointer_false_and_rest_has_one_true():
    clause = Clause([-1,2,-6, 10])
    clause.set_watchers({1:False, 2: False, 10: True}, 2)
    bcp_res = clause.bcp({1:False, 2: False, 10: True})
    assert bcp_res is None




    