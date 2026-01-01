# Copyright 2025 Michael Maillet, Damien Davison, and Sacha Davison
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from XAgent.data_structure.node import ToolNode


class TaskSearchTree:
    """
    TaskSearchTree represents a tree data structure with specific task searching behavior. 

    Attributes:
        root (ToolNode): Root node of the tree.
        now_expand_num (int): Maintains current expanding number for nodes during traversal.
    """
    
    def __init__(self):
        """Initializes TaskSearchTree with a root ToolNode and default expanding number."""
        self.root: ToolNode = ToolNode()
        self.root.expand_num = 0
        self.now_expand_num = 1

    def get_depth(self):
        """
        Gets the depth of the tree from the current root node.

        Returns:
            int: The depth of the tree
        """
        return self.root.get_depth()
    
    def get_subtree_size(self):
        """
        Gets the number of nodes (or size) of the subtree from the current root node.

        Returns:
            int: The number of nodes in the subtree
        """
        return self.root.get_subtree_size()
    
    def make_father_relation(self, father, child):
        """
        Establishes a parent-child relationship between two given nodes.

        Args:
            father (ToolNode): The parent node in the relation.
            child (ToolNode): The child node in the relation.

        Raises:
            TypeError: If the father or child is not a ToolNode instance.
        """
        if not (isinstance(father, ToolNode) and isinstance(child, ToolNode)):
            raise TypeError("Father and child both need to be instances of ToolNode.")

        child.expand_num = self.now_expand_num
        self.now_expand_num += 1

        child.father = father
        father.children.append(child)
