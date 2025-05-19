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
    assert ig.nodes[3].children == {0, }
    assert ig.nodes[-3].children == {0, }

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
    res = ig.create_node(-3, 1, [-2])  # creates the conflict
    with pytest.raises(ImplicationGraphException):
        ig.create_node(100, 1100, [])


def test_implication_graph_get_conflict_clause():
    ig = ImplicationGraph()

    # IG from paper / example IGraph1
    ig.create_node(-7, 1, [])
    ig.create_node(-8, 2, [])
    ig.create_node(-9, 3, [])
    ig.create_node(-1, 4, [])
    ig.create_node(2, 4, [-1])
    ig.create_node(3, 4, [-1, -7])
    ig.create_node(4, 4, [2, 3])
    ig.create_node(6, 4, [4, -9])
    ig.create_node(5, 4, [-8, 4])
    ig.create_node(-5, 4, [6])

    res = ig.get_conflict_clause()
    assert res == ({-9, -8, 4}, 3)

    # if we add a link from x3 to x9 we should end up at the decision as the UIP
    ig = ImplicationGraph()
    ig.create_node(-7, 1, [])
    ig.create_node(-8, 2, [])
    ig.create_node(-1, 4, [])
    ig.create_node(2, 4, [-1])
    ig.create_node(3, 4, [-1, -7])
    ig.create_node(-9, 4, [3])
    ig.create_node(4, 4, [2, 3])
    ig.create_node(6, 4, [4, -9])
    ig.create_node(5, 4, [-8, 4])
    ig.create_node(-5, 4, [6])

    res = ig.get_conflict_clause()
    print(res)
    assert res == ({-1, -7, -8}, 2)

    ig = ImplicationGraph()

    # if we remove x3-x4 and add a link between x2 and x8 we should get x2 as UIP
    ig.create_node(-7, 1, [])
    ig.create_node(-9, 3, [])
    ig.create_node(-1, 4, [])
    ig.create_node(2, 4, [-1])
    ig.create_node(-8, 4, [2])
    ig.create_node(3, 4, [-1, -7])
    ig.create_node(4, 4, [2])
    ig.create_node(6, 4, [4, -9])
    ig.create_node(5, 4, [-8, 4])
    ig.create_node(-5, 4, [6])

    res = ig.get_conflict_clause()
    assert res == ({2, -9}, 3)

    ig = ImplicationGraph()

    # IGraph from example3
    ig.create_node(1, 0, [])
    ig.create_node(2, 0, [])
    ig.create_node(3, 1, [])
    ig.create_node(4, 1, [1, 3])
    ig.create_node(5, 1, [2, 4])
    ig.create_node(6, 2, [])
    ig.create_node(7, 2, [4, 6])
    ig.create_node(8, 2, [5, 7])
    ig.create_node(9, 2, [8])
    ig.create_node(10, 3, [])
    ig.create_node(11, 3, [10])
    ig.create_node(12, 4, [])
    ig.create_node(13, 4, [11, 12])
    ig.create_node(14, 4, [4, 7, 13])
    ig.create_node(15, 4, [8, 9, 14])
    ig.create_node(16, 4, [13])
    ig.create_node(-15, 4, [16])

    res = ig.get_conflict_clause()
    assert res == ({13, 7, 4, 8, 9}, 2)

    ig = ImplicationGraph()

    # IGraph from example3
    ig.create_node(1, 0, [])
    ig.create_node(2, 0, [])
    ig.create_node(3, 1, [])
    ig.create_node(4, 1, [1, 3])
    ig.create_node(5, 1, [2, 4])
    ig.create_node(6, 2, [])
    ig.create_node(7, 2, [4, 6])
    ig.create_node(8, 2, [5, 7])
    ig.create_node(9, 2, [8])
    ig.create_node(10, 3, [])
    ig.create_node(11, 3, [10])
    ig.create_node(12, 4, [])
    ig.create_node(13, 4, [11, 12])
    ig.create_node(14, 4, [4, 7, 13])
    # here we add 3, 10 as parents
    ig.create_node(15, 4, [3, 8, 9, 10, 14])
    ig.create_node(16, 4, [13])
    # here we add 1,2 as parents
    ig.create_node(-15, 4, [1, 2, 16])

    res = ig.get_conflict_clause()
    assert res == ({13, 4, 7, 8, 9, 3, 10, 1, 2}, 3)

def test_implication_graph_delete_node():
    ig = ImplicationGraph()

    # IG from paper / example IGraph1
    ig.create_node(-7, 1, [])
    ig.create_node(-8, 2, [])
    ig.create_node(-9, 3, [])
    ig.create_node(-1, 4, [])
    ig.create_node(2, 4, [-1])
    ig.create_node(3, 4, [-1, -7])
    ig.create_node(4, 4, [2, 3])
    ig.create_node(6, 4, [4, -9])
    ig.create_node(5, 4, [-8, 4])
    ig.create_node(-5, 4, [6])

    ig.delete_node(-1)
    assert len(ig.nodes) == 3
    assert set(ig.nodes.keys()) == {-9, -7, -8}

    ig = ImplicationGraph()

    # IG from paper / example IGraph1
    ig.create_node(-7, 1, [])
    ig.create_node(-8, 2, [])
    ig.create_node(-9, 3, [])
    ig.create_node(-1, 4, [])
    ig.create_node(2, 4, [-1])
    ig.create_node(3, 4, [-1, -7])
    ig.create_node(4, 4, [2, 3])
    ig.create_node(6, 4, [4, -9])
    ig.create_node(5, 4, [-8, 4])
    ig.create_node(-5, 4, [6])

    ig.delete_node(3)
    assert len(ig.nodes) == 5
    assert set(ig.nodes.keys()) == {-7, -1, 2, -8, -9}

    ig = ImplicationGraph()

    # IGraph from example3
    ig.create_node(1, 0, [])
    ig.create_node(2, 0, [])
    ig.create_node(3, 1, [])
    ig.create_node(4, 1, [1, 3])
    ig.create_node(5, 1, [2, 4])
    ig.create_node(6, 2, [])
    ig.create_node(7, 2, [4, 6])
    ig.create_node(8, 2, [5, 7])
    ig.create_node(9, 2, [8])
    ig.create_node(10, 3, [])
    ig.create_node(11, 3, [10])
    ig.create_node(12, 4, [])
    ig.create_node(13, 4, [11, 12])
    ig.create_node(14, 4, [4, 7, 13])
    ig.create_node(15, 4, [8, 9, 14])
    ig.create_node(16, 4, [13])
    ig.create_node(-15, 4, [16])

    ig.delete_node(1)
    assert len(ig.nodes) == 9
    assert set(ig.nodes.keys()) == {2,3,6,10,12, 11,13,16,-15}

    ig = ImplicationGraph()

    # IGraph from example3
    ig.create_node(1, 0, [])
    ig.create_node(2, 0, [])
    ig.create_node(3, 1, [])
    ig.create_node(4, 1, [1, 3])
    ig.create_node(5, 1, [2, 4])
    ig.create_node(6, 2, [])
    ig.create_node(7, 2, [4, 6])
    ig.create_node(8, 2, [5, 7])
    ig.create_node(9, 2, [8])
    ig.create_node(10, 3, [])
    ig.create_node(11, 3, [10])
    ig.create_node(12, 4, [])
    ig.create_node(13, 4, [11, 12])
    ig.create_node(14, 4, [4, 7, 13])
    ig.create_node(15, 4, [8, 9, 14])
    ig.create_node(16, 4, [13])
    ig.create_node(-15, 4, [16])

    ig.delete_node(7)
    assert len(ig.nodes) == 12
    assert set(ig.nodes.keys()) == {1,2,3,4,5,6,10,11,12,13,16,-15}

    assert len(ig.nodes[-15].children) == 0
    assert len(ig.nodes[13].children) == 1