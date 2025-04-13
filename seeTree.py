from tree_sitter import Language, Parser  # 解析器库
from graphviz import Digraph  # 绘图库
from typing import List, Tuple

def ast_bfs(root):
    """ traversal AST Tree stack By BFS"""
    node_list = []  # node_list: [(node_id, node_type), ...]
    edge_list = []  # edge_list: [(parent_id, child_id), ...]

    # queue for BFS
    root_tuple = (root, None)  # 根节点
    queue = []
    queue.append(root_tuple)  # tuple (Node<> node, int parent_id)

    # BFS
    while queue:
        # 出队
        (node, parent_id) = queue.pop(0)

        node_type = str(node.type).strip()  # 结点的类型
        node_text = str(node.text.decode())  # 代码的内容，可以用于显示(目前没有用)
        node_id = str(len(node_list))  # ID

        node_str = node_type + "\n" + node_text
        node_item = (node_id, node_str)  # tuple（node_id, node_string）  node_str是你想展示的内容
        node_list.append(node_item)

        # 如果有父节点，添加一条从父节点到当前节点的边
        if parent_id is not None:
            edge_list.append((parent_id, node_id))

        # 遍历子节点入队
        for child in node.children:
            queue.append((child, node_id))

    return node_list, edge_list


def draw_tree(graph_name: str, node_list: List[Tuple], edge_list: List[Tuple]):
    """ draw a tree
    """
    # 创建一个Digraph对象
    dot = Digraph(comment=graph_name)
    # 绘制结点
    for node in node_list:
        dot.node(name=node[0], label=node[1], shape="box")
    # 绘制连线
    for edge in edge_list:
        dot.edge(tail_name=edge[0], head_name=edge[1], lable="")
    return dot


