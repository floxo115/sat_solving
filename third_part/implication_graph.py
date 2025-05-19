from enum import Enum
from typing import Dict, Iterable, Set


class ImplicationGraphException(Exception):
    def __init__(self, message: str):
        super().__init__(message)


class ImplicationGraphStates(Enum):
    CONFLICT = 0
    NOT_CONFLICT = 1


class Node(object):
    def __init__(self, variable: int, decision_level: int, parents: Iterable[int]):
        self.variable = variable

        if not 0 <= decision_level:
            raise ImplicationGraphException("decision_level can not be smaller than 0")
        self.decision_level = decision_level
        self.parents = set(parents)
        self.children = set([])

    def __repr__(self):
        s = f"Node({self.variable}, {self.decision_level}, {self.parents})"
        return s

    def __str__(self):
        return self.__repr__()


CONFLICT_NODE_IDX = 0


class ImplicationGraph(object):
    def __init__(self):
        self.nodes: Dict[int, Node] = {}

    def create_node(self, variable: int, decision_level: int, parents: Iterable[int]) -> ImplicationGraphStates:
        """
        Creates a new node for the Implication Graph. If there is a conflict, it will also create a conflict node.
        :param variable: Variable of the new node together with its assignment. I.E.: -1 for the variable 1 with assignment
        False...
        :param decision_level: The decision level of the new node
        :param parents: A list of the parents of the new node.
        :return: ImplicationGraphStates.CONFLICT if a conflict occurs. Else ImplicationGraphStates.NOT_CONFLICT
        """
        if variable == 0:
            raise ImplicationGraphException("conflict can not be assigned manually")

        if variable in self.nodes.keys():
            raise ImplicationGraphException("variable can not be assigned again")

        if decision_level < 0:
            raise ImplicationGraphException("decision_level can not be smaller than 0")

        if not all([parent in self.nodes.keys() for parent in parents]):
            raise ImplicationGraphException("parents have to be present in the graph")

        if CONFLICT_NODE_IDX in self.nodes.keys():
            raise ImplicationGraphException("there is a conflict in the graph")

        # the parents of the new node need to be updated
        for parent in parents:
            self.nodes[parent].children.add(variable)

        # we create a new node
        node = Node(variable, decision_level, parents)

        # if the opposite polarity of the new variable is already present, we have a conflict
        if -variable in self.nodes.keys():
            # we create a new conflict node and set it as child of the new node and its opposite node
            self.nodes[variable] = node
            self.nodes[variable].children.add(CONFLICT_NODE_IDX)
            conflict_var = self.nodes[-variable]
            conflict_var.children.add(CONFLICT_NODE_IDX)
            conflict = Node(CONFLICT_NODE_IDX, decision_level, [variable, conflict_var.variable])
            self.nodes[CONFLICT_NODE_IDX] = conflict

            return ImplicationGraphStates.CONFLICT
        else:
            # if everything is OK we just append the new node
            self.nodes[variable] = node
            return ImplicationGraphStates.NOT_CONFLICT

    def get_conflict_clause(self) -> Set[int]:
        if self.nodes[CONFLICT_NODE_IDX] is None:
            raise ImplicationGraphException("no UIP without a conflict clause")

        cur_dec_level = self.nodes[CONFLICT_NODE_IDX].decision_level
        C = {cur_dec_level: []}
        C[cur_dec_level].extend(self.nodes[CONFLICT_NODE_IDX].parents)

        visited = [0]
        while len(C[cur_dec_level]) > 1:
            for n in reversed(C[cur_dec_level]):
                cur_node = self.nodes[n]
                if all([ch in visited for ch in cur_node.children]):
                    parents = cur_node.parents
                    for parent in parents:
                        if parent not in C.setdefault(self.nodes[parent].decision_level, []):
                            C.setdefault(self.nodes[parent].decision_level, []).append(parent)
                    C[cur_dec_level].remove(n)
                    visited.append(n)
                    break

        result = []
        for variables in C.values():
            result.extend(variables)

        return set(result)


    def __repr__(self):
        s = "ImplicationGraph(\n"
        for k, v in self.nodes.items():
            if k == 0:
                k = "0==CONFLICT"
            s += f"key: {str(k)}\nvalue\t{str(v)}\n"

        s += ")"

        return s

    def __str__(self):
        return self.__repr__()
