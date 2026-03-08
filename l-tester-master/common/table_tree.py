# 作者：小林
from views.web.web_model import Web_element


async def create_tree(model, pid: int = 0, fields: list = None, search: dict = None):
    """
    获取树形结构，支持动态选择字段
    :param model:
    :param pid:
    :param fields: 需要返回的字段列表
    :return: 树形结构列表
    """
    search_data = {
        **search,
        'pid': pid
    }
    nodes = await model.filter(**search_data).values(*fields)
    tree = []
    for node in nodes:
        # 当前节点的数据字典
        node_data = {field: node[field] for field in fields}
        # 递归查找子节点
        children = await create_tree(model, pid=node['id'], fields=fields, search=search_data)
        if children:
            node_data['children'] = children
        tree.append(node_data)

    return tree

async def del_tree_node(tree, type):
    """
    递归剔除树形结构中 type=2 的节点
    :param tree: 树形结构数据（列表形式）
    :return: 剔除后的树形结构
    """
    if not tree or not isinstance(tree, list):
        return []

    # 过滤掉 type=2 的节点，并递归处理子节点
    result = []
    for node in tree:
        if node.get("type") != type:  # 剔除 type=2 的节点
            if "children" in node and node["children"]:  # 如果有子节点，递归处理
                node["children"] = await del_tree_node(node["children"], type)
            result.append(node)
    return result