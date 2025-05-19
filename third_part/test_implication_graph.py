import pytest

from third_part.implication_graph import ImplicationGraph, CONFLICT_NODE_IDX, ImplicationGraphStates, \
    ImplicationGraphException


def test_implication_graph_init():
    ig = ImplicationGraph()
    assert ig.nodes == {}


def test_implication_graph_add_node():
    ig = ImplicationGraph()
    res = ig.create_node(1, 0, [])
    assert res == ImplicationGraphStates.NOT_CONFLICT
    assert len(ig.nodes) == 1
    assert ig.nodes[1].variable == 1
    assert ig.nodes[1].parents == set()
    assert ig.nodes[1].children == set()

    res = ig.create_node(-2, 1, [])
    assert len(ig.nodes) == 2
    assert ig.nodes[-2].variable == -2
    assert ig.nodes[-2].parents == set()
    assert ig.nodes[-2].children == set()

    res = ig.create_node(3, 1, [1, -2])
    assert res == ImplicationGraphStates.NOT_CONFLICT
    assert len(ig.nodes) == 3
    assert ig.nodes[3].variable == 3
    assert ig.nodes[3].parents == {1, -2}
    assert ig.nodes[3].children == set()

    assert ig.nodes[1].children == {3, }
    assert ig.nodes[-2].children == {3, }

    res = ig.create_node(-3, 1, [-2])
    assert res == ImplicationGraphStates.CONFLICT
    assert len(ig.nodes) == 5
    assert ig.nodes[3].children == {0,}
    assert ig.nodes[-3].children == {0,}

    assert ig.nodes[CONFLICT_NODE_IDX].variable == CONFLICT_NODE_IDX
    assert ig.nodes[CONFLICT_NODE_IDX].parents == {3, -3}
    assert ig.nodes[CONFLICT_NODE_IDX].children == set()

def test_implication_graph_add_edge_with_errors():
    ig = ImplicationGraph()
    res = ig.create_node(1, 0, [])
    res = ig.create_node(-2, 1, [])
    res = ig.create_node(3, 1, [1, -2])

    # try to add existing node
    with pytest.raises(ImplicationGraphException):
        ig.create_node(-2, 3, [])

    # try to add negative decision level
    with pytest.raises(ImplicationGraphException):
        ig.create_node(-2, -2, [])

    # try adding node with non-existent parents
    with pytest.raises(ImplicationGraphException):
        ig.create_node(-2, -1, [100, 50])

    # try adding node that is already in the graph
    with pytest.raises(ImplicationGraphException):
        ig.create_node(-2, 10, [])

    # try to add to the graph after a conflict occures
    res = ig.create_node(-3, 1, [-2]) # creates the conflict
    with pytest.raises(ImplicationGraphException):
        ig.create_node(100, 1100, [])