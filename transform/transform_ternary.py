import os, sys
import re
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from ist_utils import replace_from_blob, traverse_rec_func, text, get_indent
from transform.lang import get_lang


def is_simple_assignment(node):
    """Check if node is a simple assignment expression (without complex expressions)"""
    if node.type != "assignment_expression":
        return False


    return len(node.children) == 3 and text(node.children[1]) == "="


def find_block_content(node):
    """Helper to find the content of a block, supporting both C and Java"""
    lang = get_lang()

    if lang == "c" and node.type == "compound_statement":
        return node
    elif lang in ["java", "c_sharp"] and node.type == "block":
        return node

    # 针对Java的特殊处理
    if lang == "java":
        body = node.child_by_field_name("body")
        if body:
            return body

    # Search deeper if not found
    for child in node.children:
        if hasattr(child, 'children'):
            result = find_block_content(child)
            if result:
                return result

    return None


def find_expression_statement(node):
    """Helper to find expression statements in blocks, supporting both C and Java"""
    # Check direct match
    if node.type == "expression_statement":
        return node

    # 针对Java的特殊处理
    lang = get_lang()
    if lang == "java":
        expr = node.child_by_field_name("expression")
        if expr and expr.type == "expression_statement":
            return expr

    # Search deeper
    for child in node.children:
        if hasattr(child, 'children'):
            result = find_expression_statement(child)
            if result:
                return result

    return None


def find_assignment(node):
    """Helper to find assignment expressions, supporting both C and Java"""
    # 添加语言检测
    lang = get_lang()

    # 检查直接匹配
    if node.type == "assignment_expression":
        return node

    # Java特定处理: 可能需要特殊处理field_name的方式获取赋值节点
    if lang == "java":
        # 尝试使用field_name方式
        expr = node.child_by_field_name("assignment")
        if expr and expr.type == "assignment_expression":
            return expr

    # 如果找到了表达式语句，检查其第一个子节点
    if node.type == "expression_statement" and node.children and node.children[0].type == "assignment_expression":
        return node.children[0]

    # 搜索更深层
    for child in node.children:
        if hasattr(child, 'children'):
            result = find_assignment(child)
            if result:
                return result

    return None


def find_method_identifier(node):
    """Find method identifier in Java method declarations"""
    if node.type == "identifier":
        return node

    for child in node.children:
        if hasattr(child, 'children'):
            result = find_method_identifier(child)
            if result:
                return result

    return None


"""==========================match========================"""


def match_if_to_ternary(root):
    """Match if-else statements that can be converted to ternary operators"""
    lang = get_lang()

    def check(node):

        if node.type != "if_statement":
            return False

        # 针对Java的特殊处理
        if_body = None
        else_body = None

        if lang == "java":
            # 尝试使用field_name直接获取
            if_body = node.child_by_field_name("consequence")
            else_clause = node.child_by_field_name("alternative")

            if else_clause:
                # else_clause可能直接是else_body，或者可能是包含else_body的节点
                if else_clause.type == "block":
                    else_body = else_clause
                else:
                    # 尝试在else_clause中查找block
                    for child in else_clause.children:
                        if child.type == "block":
                            else_body = child
                            break

        # 如果Java特殊处理没成功，回退到通用方式
        if not if_body or not else_body:

            else_clause = None
            for child in node.children:
                if child.type == "else_clause":
                    else_clause = child
                    break

            if not else_clause:
                return False


            if_body = None
            for child in node.children:

                if lang == "c" and child.type == "compound_statement":
                    if_body = child
                    break
                elif lang in ["java", "c_sharp"] and child.type == "block":
                    if_body = child
                    break

                elif lang in ["java", "c_sharp"] and child.type not in ["if", "parenthesized_expression",
                                                                        "else_clause"]:
                    if_body = child
                    break


            else_body = None
            for child in else_clause.children:
                if lang == "c" and child.type == "compound_statement":
                    else_body = child
                    break
                elif lang in ["java", "c_sharp"] and child.type == "block":
                    else_body = child
                    break
                elif lang in ["java", "c_sharp"] and child.type not in ["else"]:
                    else_body = child
                    break

        if not if_body or not else_body:
            return False

        # 从if和else的body中提取赋值表达式
        if_assign = find_assignment(if_body)
        else_assign = find_assignment(else_body)

        # 检查赋值表达式是否相同
        if if_assign and else_assign and is_simple_assignment(if_assign) and is_simple_assignment(else_assign):
            if lang == "java":
                # 获取Java中赋值表达式的左侧
                if_left_op = if_assign.child_by_field_name("left")
                else_left_op = else_assign.child_by_field_name("left")

                if if_left_op and else_left_op:
                    return text(if_left_op) == text(else_left_op)

            # 回退到常规检查
            return text(if_assign.children[0]) == text(else_assign.children[0])

        # 同时检查if和else的返回语句
        if_return = None
        else_return = None

        # 找到if_body中的return语句
        if if_body.type == "return_statement":
            if_return = if_body
        else:
            for child in if_body.children:
                if child.type == "return_statement":
                    if_return = child
                    break

        # 找到else_body中的return语句
        if else_body.type == "return_statement":
            else_return = else_body
        else:
            for child in else_body.children:
                if child.type == "return_statement":
                    else_return = child
                    break

        # 如果找到了return语句，检查它们是否返回相同的表达式
        if if_return and else_return:
            return True

        return False

    res = []

    def match(u):
        if check(u):
            res.append(u)
        for v in u.children:
            match(v)

    match(root)
    return res


def match_ternary_to_if(root):
    """Match ternary operator expressions that can be converted to if-else statements"""
    lang = get_lang()

    def check(node):

        if node.type == "assignment_expression":

            rhs = None
            if lang == "java":
                rhs = node.child_by_field_name("right")
                if not rhs and len(node.children) >= 3:
                    rhs = node.children[2]
            else:  # C and other languages
                if len(node.children) >= 3:
                    rhs = node.children[2]

            if rhs and has_ternary_expression(rhs, lang):
                return True


        if node.type == "return_statement":

            if has_ternary_in_source(text(node), "return"):
                return True


        declaration_types = [
            "declaration",  # C
            "variable_declaration",  # Java
            "local_variable_declaration",  # Java
            "field_declaration",  # Java
        ]

        if node.type in declaration_types:
            # 检查源代码是否包含问号和冒号
            if has_ternary_in_source(text(node)):
                return True

            # 深入检查子节点
            if deep_search_ternary(node, lang):
                return True

        return False

    # Helper function to check if a node contains a ternary expression
    def has_ternary_expression(node, lang):

        if (lang == "c" and node.type == "conditional_expression") or \
                (lang == "java" and node.type in ["conditional_expression", "ternary_expression",
                                                  "conditional_operator", "ternary_operator"]):
            return True

        # 检查源代码是否包含问号和冒号
        source = text(node)
        if "?" in source and ":" in source:
            return True

        return False

    # Helper function to search for ternary expressions in source code
    def has_ternary_in_source(source, prefix=""):
        if prefix:
            if prefix in source and "?" in source and ":" in source:
                return True
        else:
            if "=" in source and "?" in source and ":" in source:
                return True
        return False

    # Helper function to deep search for ternary expressions
    def deep_search_ternary(node, lang):
        if has_ternary_expression(node, lang):
            return True

        if hasattr(node, 'children'):
            for child in node.children:
                if deep_search_ternary(child, lang):
                    return True

        return False

    res = []

    def match(u):
        if check(u):
            res.append(u)
        for v in u.children:
            match(v)

    match(root)
    return res

"""==========================replace========================"""


def convert_if_to_ternary(node, code):
    """Convert if-else statement to ternary operator"""
    lang = get_lang()

    if (lang == "c" and node.type == "init_declarator") or \
            (lang == "java" and node.type == "local_variable_declaration"):
        # 提取变量名和三元表达式
        var_name = None
        ternary = None

        # C语言处理
        if lang == "c":
            var_name = text(node.children[0])
            for child in node.children:
                if child.type == "conditional_expression":
                    ternary = child
                    break

        # Java处理
        elif lang == "java":
            declarator = node.child_by_field_name("declarator")
            if declarator:
                var_name = text(declarator)
                initializer = node.child_by_field_name("initializer")
                if initializer:
                    ternary = initializer.child_by_field_name("value")

        if not var_name or not ternary:
            return None

        # 提取三元表达式各部分
        condition, true_expr, false_expr = extract_ternary_parts(ternary, lang)
        if not all([condition, true_expr, false_expr]):
            return None

        # 生成声明+if-else赋值的代码
        indent = get_indent(node.start_byte, code)
        new_code = []
        if lang == "c":
            # 原声明语句可能带类型，如 int a = ...;
            decl_part = text(node.parent.children[0])  # 获取类型部分
            new_code.append(f"{decl_part} {var_name};\n")
            new_code.append(f"{' ' * indent}if ({condition}) {{\n")
            new_code.append(f"{' ' * (indent + 4)}{var_name} = {true_expr};\n")
            new_code.append(f"{' ' * indent}}} else {{\n")
            new_code.append(f"{' ' * (indent + 4)}{var_name} = {false_expr};\n")
            new_code.append(f"{' ' * indent}}}")
        else:  # Java
            decl_part = text(node).split('=')[0].strip()  # 提取声明部分
            new_code.append(f"{decl_part};\n")
            new_code.append(f"{' ' * indent}if ({condition}) {{\n")
            new_code.append(f"{' ' * (indent + 4)}{var_name} = {true_expr};\n")
            new_code.append(f"{' ' * indent}}} else {{\n")
            new_code.append(f"{' ' * (indent + 4)}{var_name} = {false_expr};\n")
            new_code.append(f"{' ' * indent}}}")

        return [
            (node.end_byte, node.start_byte),
            (node.start_byte, "".join(new_code))
        ]

    # 提取条件
    condition_node = None
    for child in node.children:
        if child.type == "parenthesized_expression":
            condition_node = child
            break
        # Java可能使用field_name
        elif lang == "java" and not condition_node:
            cond = node.child_by_field_name("condition")
            if cond:
                condition_node = cond
                break

    if not condition_node:
        return None

    condition = text(condition_node)

    # 查找if体和else子句
    if_body = None
    else_clause = None

    # 针对Java的特殊处理
    if lang == "java":
        if_body = node.child_by_field_name("consequence")  # Java常用field名
        else_clause = node.child_by_field_name("alternative")  # Java常用field名

    # 如果field_name方式未找到，回退到遍历
    if not if_body or not else_clause:
        for child in node.children:
            if lang == "c" and child.type == "compound_statement":
                if_body = child
            elif lang in ["java", "c_sharp"] and child.type == "block":
                if_body = child
            elif lang in ["java", "c_sharp"] and child.type not in ["if", "parenthesized_expression", "else_clause"]:
                if_body = child
            elif child.type == "else_clause":
                else_clause = child

    if not if_body or not else_clause:
        return None

    # 获取else体
    else_body = None
    if lang == "java":
        # Java可能直接有else_body
        else_body = else_clause  # 如果else_clause就是body

    # 如果没找到，回退到遍历
    if not else_body:
        for child in else_clause.children:
            if lang == "c" and child.type == "compound_statement":
                else_body = child
            elif lang in ["java", "c_sharp"] and child.type == "block":
                else_body = child
            elif lang in ["java", "c_sharp"] and child.type not in ["else"]:
                else_body = child

    if not else_body:
        return None

    # 检查赋值
    if_assign = find_assignment(if_body)
    else_assign = find_assignment(else_body)

    if if_assign and else_assign and is_simple_assignment(if_assign) and is_simple_assignment(else_assign):
        # 提取变量和值
        variable = None
        true_value = None
        false_value = None

        if lang == "java":
            # 尝试通过field_name获取
            var_node = if_assign.child_by_field_name("left")
            true_node = if_assign.child_by_field_name("right")
            false_node = else_assign.child_by_field_name("right")

            if var_node and true_node and false_node:
                variable = text(var_node)
                true_value = text(true_node)
                false_value = text(false_node)
            else:
                # 回退到位置索引方法
                variable = text(if_assign.children[0])
                true_value = text(if_assign.children[2])
                false_value = text(else_assign.children[2])
        else:
            # C语言和回退方法
            variable = text(if_assign.children[0])
            true_value = text(if_assign.children[2])
            false_value = text(else_assign.children[2])

        # 创建三元表达式
        ternary_expr = f"{variable} = {condition} ? {true_value} : {false_value};"

        # 获取适当的缩进
        indent = get_indent(node.start_byte, code)

        # 返回操作以用三元替换if-else
        return [
            (node.end_byte, node.start_byte),
            (node.start_byte, f"{' ' * indent}{ternary_expr}")
        ]

    # 检查return语句
    if_return = None
    else_return = None

    # 查找return语句
    if if_body.type == "return_statement":
        if_return = if_body
    else:
        for child in if_body.children:
            if child.type == "return_statement":
                if_return = child
                break

    if else_body.type == "return_statement":
        else_return = else_body
    else:
        for child in else_body.children:
            if child.type == "return_statement":
                else_return = child
                break

    if if_return and else_return:
        # 提取return值
        true_expr = None
        false_expr = None

        if lang == "java":
            # 尝试通过field_name获取
            true_expr_node = if_return.child_by_field_name("value") or if_return.child_by_field_name("expression")
            false_expr_node = else_return.child_by_field_name("value") or else_return.child_by_field_name("expression")

            if true_expr_node and false_expr_node:
                true_expr = text(true_expr_node)
                false_expr = text(false_expr_node)
            else:
                # 回退到遍历方法
                for child in if_return.children:
                    if child.type not in ["return", ";"]:
                        true_expr = text(child)
                        break
                for child in else_return.children:
                    if child.type not in ["return", ";"]:
                        false_expr = text(child)
                        break
        else:
            # C语言和回退方法
            for child in if_return.children:
                if child.type not in ["return", ";"]:
                    true_expr = text(child)
                    break
            for child in else_return.children:
                if child.type not in ["return", ";"]:
                    false_expr = text(child)
                    break

        if true_expr and false_expr:
            # 创建三元return语句
            ternary_return = f"return {condition} ? {true_expr} : {false_expr};"

            # 获取适当的缩进
            indent = get_indent(node.start_byte, code)

            # 返回操作以用三元return替换if-else return
            return [
                (node.end_byte, node.start_byte),
                (node.start_byte, f"{' ' * indent}{ternary_return}")
            ]

    return None


def convert_ternary_to_if(node, code):
    """Convert ternary operator to if-else statement"""
    lang = get_lang()

    # 检查是否是带有三元的赋值
    is_assignment = node.type == "assignment_expression"
    is_return = node.type == "return_statement"

    if is_assignment:
        # 获取变量名和三元表达式
        variable = None
        ternary = None

        if lang == "java":
            # 尝试通过field_name获取
            variable_node = node.child_by_field_name("left")
            ternary = node.child_by_field_name("right")

            if variable_node:
                variable = text(variable_node)
            else:
                # 回退到位置索引方法
                variable = text(node.children[0])
                ternary = node.children[2]
        else:
            # C语言和回退方法
            variable = text(node.children[0])
            ternary = node.children[2]

        # 提取条件、true和false表达式
        condition = None
        true_expr = None
        false_expr = None

        if lang == "c":
            if len(ternary.children) >= 5:  # condition ? true_expr : false_expr
                condition = text(ternary.children[0])
                true_expr = text(ternary.children[2])
                false_expr = text(ternary.children[4])
        elif lang == "java":
            # 尝试使用field_name方式处理Java的三元表达式
            condition_node = ternary.child_by_field_name("condition")
            true_node = ternary.child_by_field_name("consequence") or ternary.child_by_field_name("then_expression")
            false_node = ternary.child_by_field_name("alternative") or ternary.child_by_field_name("else_expression")

            if condition_node and true_node and false_node:
                condition = text(condition_node)
                true_expr = text(true_node)
                false_expr = text(false_node)
            elif len(ternary.children) >= 5:  # 回退到基于子节点位置的方法
                condition = text(ternary.children[0])
                true_expr = text(ternary.children[2])
                false_expr = text(ternary.children[4])
        elif lang == "c_sharp":
            if len(ternary.children) >= 5:
                condition = text(ternary.children[0])
                true_expr = text(ternary.children[2])
                false_expr = text(ternary.children[4])

        if not condition or not true_expr or not false_expr:
            return None

        # 获取适当的缩进
        indent = get_indent(node.start_byte, code)

        # 创建if-else语句
        if_else_stmt = (
            f"if ({condition}) {{\n"
            f"{' ' * (indent + 4)}{variable} = {true_expr};\n"
            f"{' ' * indent}}} else {{\n"
            f"{' ' * (indent + 4)}{variable} = {false_expr};\n"
            f"{' ' * indent}}}"
        )

        # 返回操作以用if-else替换三元
        return [
            (node.end_byte, node.start_byte),
            (node.start_byte, if_else_stmt)
        ]

    elif is_return:
        # 查找三元表达式
        ternary = None
        for child in node.children:
            if lang == "c" and child.type == "conditional_expression":
                ternary = child
                break
            elif lang == "java":
                # 处理Java的三元表达式节点
                if child.type in ["conditional_expression", "ternary_expression"]:
                    ternary = child
                    break
                # 尝试使用field_name
                condition = child.child_by_field_name("condition")
                if condition:
                    ternary = child
                    break
            elif lang == "c_sharp" and child.type in ["conditional_expression", "ternary_expression"]:
                ternary = child
                break

        # Java可能将ternary作为expression/value字段
        if not ternary and lang == "java":
            expr_node = node.child_by_field_name("expression") or node.child_by_field_name("value")
            if expr_node and expr_node.type in ["conditional_expression", "ternary_expression"]:
                ternary = expr_node

        if not ternary:
            return None

        # 提取条件、true和false表达式
        condition = None
        true_expr = None
        false_expr = None

        if lang == "c":
            if len(ternary.children) >= 5:
                condition = text(ternary.children[0])
                true_expr = text(ternary.children[2])
                false_expr = text(ternary.children[4])
        elif lang == "java":
            # 尝试使用field_name方式
            condition_node = ternary.child_by_field_name("condition")
            true_node = ternary.child_by_field_name("consequence") or ternary.child_by_field_name("then_expression")
            false_node = ternary.child_by_field_name("alternative") or ternary.child_by_field_name("else_expression")

            if condition_node and true_node and false_node:
                condition = text(condition_node)
                true_expr = text(true_node)
                false_expr = text(false_node)
            elif len(ternary.children) >= 5:  # 回退到基于子节点位置的方法
                condition = text(ternary.children[0])
                true_expr = text(ternary.children[2])
                false_expr = text(ternary.children[4])
        elif lang == "c_sharp":
            if len(ternary.children) >= 5:
                condition = text(ternary.children[0])
                true_expr = text(ternary.children[2])
                false_expr = text(ternary.children[4])

        if not condition or not true_expr or not false_expr:
            return None

        # 获取适当的缩进
        indent = get_indent(node.start_byte, code)

        # 创建带返回的if-else语句
        if_else_stmt = (
            f"if ({condition}) {{\n"
            f"{' ' * (indent + 4)}return {true_expr};\n"
            f"{' ' * indent}}} else {{\n"
            f"{' ' * (indent + 4)}return {false_expr};\n"
            f"{' ' * indent}}}"
        )

        # 返回操作以用if-else返回替换三元返回
        return [
            (node.end_byte, node.start_byte),
            (node.start_byte, if_else_stmt)
        ]
    elif node.type in ["declaration", "variable_declaration", "local_variable_declaration", "field_declaration"]:
        # Try to extract information using regex first
        source = text(node)

        # 匹配
        pattern = r'([\w<>\[\]]+(?:\s+\w+)*)\s+(\w+)\s*=\s*(.+?)\s*\?\s*(.+?)\s*:\s*(.+?)\s*;'
        match = re.search(pattern, source)

        if match:
            var_type = match.group(1).strip()
            var_name = match.group(2).strip()
            condition = match.group(3).strip()
            true_expr = match.group(4).strip()
            false_expr = match.group(5).strip()

            # 创建if-else代码
            indent = get_indent(node.start_byte, code)
            if_else_stmt = (
                f"{var_type} {var_name};\n"
                f"{' ' * indent}if ({condition}) {{\n"
                f"{' ' * (indent + 4)}{var_name} = {true_expr};\n"
                f"{' ' * indent}}} else {{\n"
                f"{' ' * (indent + 4)}{var_name} = {false_expr};\n"
                f"{' ' * indent}}}"
            )

            return [
                (node.end_byte, node.start_byte),
                (node.start_byte, f"{' ' * indent}{if_else_stmt}")
            ]

        # 如果正则匹配失败，尝试使用特定语言的方法
        var_type, var_name, condition, true_expr, false_expr = extract_from_declaration(node, lang)

        if var_type and var_name and condition and true_expr and false_expr:
            # 创建if-else代码
            indent = get_indent(node.start_byte, code)
            if_else_stmt = (
                f"{var_type} {var_name};\n"
                f"{' ' * indent}if ({condition}) {{\n"
                f"{' ' * (indent + 4)}{var_name} = {true_expr};\n"
                f"{' ' * indent}}} else {{\n"
                f"{' ' * (indent + 4)}{var_name} = {false_expr};\n"
                f"{' ' * indent}}}"
            )

            return [
                (node.end_byte, node.start_byte),
                (node.start_byte, f"{' ' * indent}{if_else_stmt}")
            ]
    return None


"""==========================count========================"""


def count_if_to_ternary(root):
    """Count if statements that can be converted to ternary operators"""
    nodes = match_if_to_ternary(root)
    return len(nodes)


def count_ternary_to_if(root):
    """Count ternary expressions that can be converted to if statements"""
    nodes = match_ternary_to_if(root)
    return len(nodes)


def extract_ternary_parts(node, lang):
    """递归提取三元表达式的条件、true表达式和false表达式"""
    condition = None
    true_expr = None
    false_expr = None

    # 检查节点类型
    if node.type in ["conditional_expression", "ternary_expression", "conditional_operator", "ternary_operator"]:
        # 处理Java的字段名
        if lang == "java":
            condition_node = node.child_by_field_name("condition") or node.child_by_field_name(
                "predicate") or node.child_by_field_name("test")
            true_node = node.child_by_field_name("consequence") or node.child_by_field_name(
                "then_expression") or node.child_by_field_name("true_expression")
            false_node = node.child_by_field_name("alternative") or node.child_by_field_name(
                "else_expression") or node.child_by_field_name("false_expression")

            if condition_node:
                condition = text(condition_node)
            if true_node:
                true_expr = text(true_node)
            if false_node:
                false_expr = text(false_node)

        # 回退到子节点遍历（适用于C和Java的特殊情况）
        if not condition:
            # 查找条件部分（第一个子节点可能是括号表达式）
            current = node
            while current.children[0].type == "parenthesized_expression":
                current = current.children[0]
            condition = text(current.children[0])
            true_expr = text(current.children[2])
            false_expr = text(current.children[4])

    # 正则匹配复杂或嵌套表达式
    if not (condition and true_expr and false_expr):
        source = text(node)
        # 改进正则表达式，处理括号和嵌套
        match = re.search(r'([\s\S]+?)\s*\?\s*([\s\S]+?)\s*:\s*([\s\S]+)', source)
        if match:
            condition = match.group(1).strip()
            true_expr = match.group(2).strip()
            false_expr = match.group(3).strip()

    return condition, true_expr, false_expr


def extract_from_declaration(node, lang):
    """Helper function to extract information from a variable declaration with ternary initializer"""
    var_type = None
    var_name = None
    condition = None
    true_expr = None
    false_expr = None

    # Java
    if lang == "java":
        # 尝试提取类型
        type_node = find_node_by_type(node, ["primitive_type", "type_identifier"])
        if type_node:
            var_type = text(type_node)

        # 尝试提取变量名和三元表达式
        declarator = find_node_by_type(node, ["variable_declarator"])
        if declarator:
            name_node = find_node_by_type(declarator, ["identifier"])
            if name_node:
                var_name = text(name_node)

            # 尝试找到初始化器
            initializer = None
            for field in ["initializer", "value"]:
                initializer = declarator.child_by_field_name(field)
                if initializer:
                    break

            if initializer:
                ternary_node = find_ternary_expr(initializer, lang)
                if ternary_node:
                    condition, true_expr, false_expr = extract_ternary_parts(ternary_node, lang)

    #  C
    elif lang == "c":
        # 尝试提取类型
        type_node = find_node_by_type(node, ["primitive_type", "type_identifier"])
        if type_node:
            var_type = text(type_node)

        # 尝试提取变量名和三元表达式
        init_declarator = find_node_by_type(node, ["init_declarator"])
        if init_declarator:
            name_node = find_node_by_type(init_declarator, ["identifier"])
            if name_node:
                var_name = text(name_node)

            initializer = find_node_by_type(init_declarator, ["initializer"])
            if initializer:
                ternary_node = find_ternary_expr(initializer, lang)
                if ternary_node:
                    condition, true_expr, false_expr = extract_ternary_parts(ternary_node, lang)

    return var_type, var_name, condition, true_expr, false_expr


def find_node_by_type(node, types):
    """Helper function to find a node of specific types in the AST"""
    if node.type in types:
        return node

    for child in node.children:
        if hasattr(child, 'children'):
            result = find_node_by_type(child, types)
            if result:
                return result

    return None


def find_ternary_expr(node, lang):
    """Helper function to find a ternary expression node in the AST"""
    # 检查当前节点是否为三元表达式
    ternary_types = ["conditional_expression"]
    if lang == "java":
        ternary_types.extend(["ternary_expression", "conditional_operator", "ternary_operator"])

    if node.type in ternary_types:
        return node

    # 搜索子节点
    for child in node.children:
        if hasattr(child, 'children'):
            result = find_ternary_expr(child, lang)
            if result:
                return result

    return None