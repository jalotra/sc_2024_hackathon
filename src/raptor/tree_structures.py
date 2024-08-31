from typing import Dict, List, Set
import json 

class Node:
    """
    Represents a node in the hierarchical tree structure.
    """

    def __init__(self, text: str, index: int, children: Set[int], embeddings : List[float]) -> None:
        self.text = text
        self.index = index
        self.children = children
        self.embeddings = embeddings
    
    def __str__(self) -> str:
        return json.dumps({
            "text" : self.text,
            "index" : self.index,
            "children_ids" : list(self.children)
        })
    
    def __repr__(self) -> str:
        return json.dumps({
            "text" : self.text,
            "index" : self.index,
            "children_ids" : list(self.children)
        })


class Tree:

    def __init__(
        self, 
        all_nodes : Dict[int, Node],
        root_nodes : Dict[int, Node],
        leaf_nodes : Dict[int, Node],
        num_layers : int,
        layer_to_nodes : Dict[int, List[Node]]
    ) -> None:
        self.all_nodes = all_nodes
        self.root_nodes = root_nodes
        self.leaf_nodes = leaf_nodes
        self.num_layers = num_layers
        self.layer_to_nodes = layer_to_nodes
    
    def __str__(self):
        return json.dumps({
            "all_nodes" : self.all_nodes,
            "root_nodes" : self.root_nodes,
            "leaf_nodes" : self.leaf_nodes,
            "num_layers" : self.num_layers,
            "layer_to_nodes" : self.layer_to_nodes
        })

    def __repr__(self) -> str:
        return json.dumps({
            "all_nodes" : self.all_nodes,
            "root_nodes" : self.root_nodes,
            "leaf_nodes" : self.leaf_nodes,
            "num_layers" : self.num_layers,
            "layer_to_nodes" : self.layer_to_nodes
        })
