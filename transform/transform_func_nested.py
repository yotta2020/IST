import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from ist_utils import text, get_indent

# 存储函数类型信息的字典
function_type_cache = {}

# 存储声明信息的全局字典，值为列表类型
declarations = {}

# 存储变量信息的全局字典
var_info_cache = {}


def match_func_not_nested(root):
    global declarations
    declarations = {}

    def check(node):
        # 获取当前编程语言
        from transform.lang import get_lang
        lang = get_lang()

        # 根据语言选择函数调用节点类型
        call_type = "method_invocation" if lang == "java" else "call_expression"

        # 检查是否为函数调用表达式
        if node.type != call_type:
            return False

        # 检查是否有嵌套的函数调用
        if lang == "java":
            args = node.child_by_field_name("arguments")
            if args and args.type == "argument_list":
                for arg in args.children:
                    if arg.type == "method_invocation":
                        # 记录嵌套调用的位置
                        if str(arg) not in declarations:
                            declarations[str(arg)] = []
                        declarations[str(arg)].append(node)
                        return True
                    # 递归检查参数中的嵌套调用
                    if check(arg):
                        return True
        else:
            for child in node.children:
                if child.type == "argument_list":
                    for arg in child.children:
                        if arg.type == "call_expression":
                            # 记录嵌套调用的位置
                            if str(arg) not in declarations:
                                declarations[str(arg)] = []
                            declarations[str(arg)].append(node)
                            return True
                        # 递归检查参数中的嵌套调用
                        if check(arg):
                            return True
                elif child.type == "call_expression":
                    # 记录嵌套调用的位置
                    if str(child) not in declarations:
                        declarations[str(child)] = []
                    declarations[str(child)].append(node)
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


def match_func_nested(root):
    global var_info_cache, declarations
    # 清空
    matched_nodes = []
    var_info_cache = {}
    declarations = {}

    def collect_vars(u, scope=None):
        current_scope = u if u.type == "compound_statement" or u.type == "block" else scope
        if current_scope:
            # 根据不同语言选择变量声明节点类型
            from transform.lang import get_lang
            lang = get_lang()
            declaration_type = "declaration" if lang == "c" else "local_variable_declaration"
            declarator_type = "init_declarator" if lang == "c" else "variable_declarator"

            children = [c for c in u.children if c.type == declaration_type]
            for child in children:
                id1 = None
                call1 = None
                for c in child.children:
                    if c.type == declarator_type:
                        for gc in c.children:
                            if gc.type == "identifier":
                                id1 = text(gc)
                            elif gc.type == "call_expression" or gc.type == "method_invocation":
                                call1 = gc
                if id1 and call1:
                    if id1 not in var_info_cache:
                        var_info_cache[id1] = []
                    var_info_cache[id1].append((child, call1, current_scope))
        for v in u.children:
            collect_vars(v, current_scope)

    def check_nested_call(node):
        # 检查是否有嵌套的函数调用
        from transform.lang import get_lang
        lang = get_lang()
        if lang == "java":
            args = node.child_by_field_name("arguments")
            if args and args.type == "arguments":
                for arg in args.children:
                    if arg.type == "method_invocation":
                        # 记录嵌套调用的位置
                        if str(arg) not in declarations:
                            declarations[str(arg)] = []
                        declarations[str(arg)].append(node)
                        return True
                    # 递归检查参数中的嵌套调用
                    if check_nested_call(arg):
                        return True
        else:
            for child in node.children:
                if child.type == "argument_list":
                    for arg in child.children:
                        if arg.type == "call_expression":
                            # 记录嵌套调用的位置
                            if str(arg) not in declarations:
                                declarations[str(arg)] = []
                            declarations[str(arg)].append(node)
                            return True
                        # 递归检查参数中的嵌套调用
                        if check_nested_call(arg):
                            return True
                elif child.type == "call_expression":
                    # 记录嵌套调用的位置
                    if str(child) not in declarations:
                        declarations[str(child)] = []
                    declarations[str(child)].append(node)
                    return True
        return False

    def match(u, scope=None):
        current_scope = u if u.type == "compound_statement" or u.type == "block" else scope
        from transform.lang import get_lang
        lang = get_lang()
        for c in u.children:
            # 根据语言选择函数调用节点类型
            call_type = "method_invocation" if lang == "java" else "call_expression"
            if c.type == call_type:
                # 检查是否有嵌套调用
                if check_nested_call(c):
                    matched_nodes.append(c)
                # 检查函数调用的直接参数
                if lang == "java":
                    args = c.child_by_field_name("arguments")
                    if args and args.type == "argument_list":
                        for param in args.children:
                            if param.type == "identifier" and text(param) in var_info_cache:
                                # 检查变量是否在同一作用域内
                                for var_node, _, var_scope in var_info_cache[text(param)]:
                                    if var_scope == current_scope:
                                        matched_nodes.append(c)
                                        if str(var_node) not in declarations:
                                            declarations[str(var_node)] = []
                                        declarations[str(var_node)].append(c)
                else:
                    for arg in c.children:
                        if arg.type == "argument_list":
                            for param in arg.children:
                                if param.type == "identifier" and text(param) in var_info_cache:
                                    # 检查变量是否在同一作用域内
                                    for var_node, _, var_scope in var_info_cache[text(param)]:
                                        if var_scope == current_scope:
                                            matched_nodes.append(c)
                                            if str(var_node) not in declarations:
                                                declarations[str(var_node)] = []
                                            declarations[str(var_node)].append(c)
                        elif arg.type == "identifier" and text(arg) in var_info_cache:
                            # 检查变量是否在同一作用域内
                            for var_node, _, var_scope in var_info_cache[text(arg)]:
                                if var_scope == current_scope:
                                    matched_nodes.append(c)
                                    if str(var_node) not in declarations:
                                        declarations[str(var_node)] = []
                                    declarations[str(var_node)].append(c)
        for v in u.children:
            match(v, current_scope)

    collect_vars(root)
    match(root)
    return matched_nodes


def cvt_func_nested(node, code):
    # 获取函数调用中使用的变量信息
    id1 = None
    call1 = None
    replacement = None
    current_scope = None

    # 获取当前作用域
    parent = node
    while parent:
        if parent.type == "compound_statement" or parent.type == "block":
            current_scope = parent
            break
        parent = parent.parent

    # 遍历函数调用的参数，查找变量
    from transform.lang import get_lang
    lang = get_lang()
    if lang == "java":
        args = node.child_by_field_name("arguments")
        if args and args.type == "argument_list":
            for arg in args.children:
                if arg.type == "identifier":
                    id1 = text(arg)
                    # 从var_info_cache中获取变量的声明信息
                    if id1 in var_info_cache:
                        for var_node, c, var_scope in var_info_cache[id1]:
                            # 检查变量是否在同一作用域内
                            if var_scope == current_scope:
                                replacement = arg
                                call1 = c
                                break

        if not (id1 and call1 and replacement):
            return None

        # 检查变量在declarations字典中的引用次数
        has_other_refs = len(declarations.get(str(call1.parent.parent), [])) > 1

        # 获取变量的声明节点
        var_node = call1.parent.parent

        if not var_node:
            return None

        delete = []
        inserts = []

        # 如果变量只有一次引用，删除声明语句
        if not has_other_refs:
            delete.append((var_node.end_byte + 1, var_node.start_byte - get_indent(var_node.start_byte, code)))

        # 替换函数调用
        delete.append((replacement.end_byte, replacement.start_byte))
        inserts.append((replacement.start_byte, text(call1)))

        return delete + inserts
    else:  # C语言处理逻辑
        for child in node.children:
            if child.type == "argument_list":
                for arg in child.children:
                    if arg.type == "identifier":
                        id1 = text(arg)
                        # 从var_info_cache中获取变量的声明信息
                        if id1 in var_info_cache:
                            for var_node, c, var_scope in var_info_cache[id1]:
                                # 检查变量是否在同一作用域内
                                if var_scope == current_scope:
                                    replacement = arg
                                    call1 = c
                                    break
            elif child.type == "identifier":
                id1 = text(child)
                if id1 in var_info_cache:
                    for var_node, c, var_scope in var_info_cache[id1]:
                        if var_scope == current_scope:
                            replacement = child
                            call1 = c
                            break

        if not (id1 and call1 and replacement):
            return None

        # 检查变量在declarations字典中的引用次数
        has_other_refs = len(declarations.get(str(call1.parent.parent), [])) > 1

        # 获取变量的声明节点
        var_node = call1.parent.parent

        if not var_node:
            return None

        delete = []
        inserts = []

        # 如果变量只有一次引用，删除声明语句
        if not has_other_refs:
            delete.append((var_node.end_byte + 1, var_node.start_byte - get_indent(var_node.start_byte, code)))

        # 替换函数调用
        delete.append((replacement.end_byte, replacement.start_byte))
        inserts.append((replacement.start_byte, text(call1)))

        return delete + inserts
    return None


def cvt_func_not_nested(node, code):
    result = extract_nested_call(node)
    if result:
        delete = []
        inserts = []
        declarations = set()  # 使用集合来避免重复声明
        global temp_var_counter
        if not 'temp_var_counter' in globals():
            temp_var_counter = 0
        # 根据编程语言选择变量声明方式
        from transform.lang import get_lang
        lang = get_lang()
        # 获取函数名和返回类型
        func_name = None
        for nested_call in result:
            if ((lang == "java" and nested_call.type == "method_invocation") or (
                    lang != "java" and nested_call.type == "call_expression")):
                var_name = f"temp_result_{temp_var_counter}"
                if lang == "java":
                    name_node = nested_call.child_by_field_name("name")
                    if name_node:
                        func_name = text(name_node)
                else:
                    for child in nested_call.children:
                        if child.type == "identifier":
                            func_name = text(child)
                            break
                # 获取函数的返回类型
                root = node
                while root.parent is not None:
                    root = root.parent
                return_type = get_function_return_type(root, func_name)
                if lang == "c":
                    type_str = return_type if return_type else "int"
                    decl_text = f"{type_str} {var_name} = {text(nested_call)};"
                elif lang == "java" or lang == "c_sharp":
                    decl_text = f"var {var_name} = {text(nested_call)};"
                elif lang == "python":
                    decl_text = f"{var_name} = {text(nested_call)}"
                declarations.add(decl_text)  # 使用add而不是append
                delete.append((nested_call.end_byte, nested_call.start_byte))
                inserts.append((nested_call.start_byte, var_name))
                temp_var_counter += 1
        if declarations and delete:
            # 将集合转换为列表并排序，确保声明顺序一致
            sorted_declarations = sorted(list(declarations))
            decl_text = f"\n{' ' * get_indent(node.parent.parent.start_byte, code)}".join(sorted_declarations)
            # 查找最后一个声明语句
            current = node
            while current and current.type not in ["compound_statement", "block"]:
                current = current.parent
            if current:
                last_decl = None
                for child in current.children:
                    # 根据语言选择声明节点类型
                    declaration_type = "declaration" if lang == "c" else "local_variable_declaration"
                    if child.type == declaration_type:
                        last_decl = child
                # 如果找到了最后一个声明语句，在其后插入新的声明
                if last_decl:
                    inserts.append((last_decl.end_byte, f"\n{' ' * get_indent(last_decl.start_byte, code)}{decl_text}"))
                else:
                    # 如果没有找到声明语句，则在作用域开始处插入
                    first_stmt = next((c for c in current.children if c.type not in ["{", "}", None]), None)
                    if first_stmt:
                        inserts.append(
                            (first_stmt.start_byte, f"{decl_text}\n{' ' * get_indent(first_stmt.start_byte, code)}"))
                    else:
                        inserts.append(
                            (current.start_byte + 1, f"\n{' ' * get_indent(current.start_byte, code)}{decl_text}\n"))
            return delete + inserts
    return None


def extract_nested_call(call_node):
    # 获取当前编程语言
    from transform.lang import get_lang
    lang = get_lang()

    # 根据语言选择函数调用节点类型
    call_type = "method_invocation" if lang == "java" else "call_expression"

    if call_node.type != call_type:
        return None

    nested_calls = []
    # 收集所有嵌套的函数调用
    if lang == "java":
        args = call_node.child_by_field_name("arguments")
        if args and args.type == "argument_list":
            for arg in args.children:
                if arg.type == "method_invocation":
                    nested_calls.append(arg)
    else:
        for child in call_node.children:
            if child.type == "argument_list":
                for arg in child.children:
                    if arg.type == "call_expression":
                        nested_calls.append(arg)
            elif child.type == "call_expression":
                nested_calls.append(child)

    if not nested_calls:
        return None

    return nested_calls


def count_func_nested(root):
    # 统计嵌套函数调用的数量
    count = 0

    def check_nested_call(node):
        # 获取当前编程语言
        from transform.lang import get_lang
        lang = get_lang()

        if lang == "java":
            args = node.child_by_field_name("arguments")
            if args and args.type == "argument_list":
                for arg in args.children:
                    if arg.type == "method_invocation":
                        return True
                    # 递归检查参数中的嵌套调用
                    if check_nested_call(arg):
                        return True
        else:
            for child in node.children:
                if child.type == "argument_list":
                    for arg in child.children:
                        if arg.type == "call_expression":
                            return True
                        # 递归检查参数中的嵌套调用
                        if check_nested_call(arg):
                            return True
                elif child.type == "call_expression":
                    return True
        return False

    def traverse(u):
        nonlocal count
        # 获取当前编程语言
        from transform.lang import get_lang
        lang = get_lang()

        # 检查当前节点是否为函数调用
        if (lang == "java" and u.type == "method_invocation") or \
                (lang != "java" and u.type == "call_expression"):
            if check_nested_call(u):
                count += 1

        # 递归遍历子节点
        for v in u.children:
            traverse(v)

    traverse(root)
    return count


def count_func_not_nested(root):
    # 统计包含嵌套函数调用的函数调用表达式数量
    count = 0

    def check(node):
        if node.type not in ["call_expression", "method_invocation"]:
            return False

        for child in node.children:
            if child.type == "argument_list" or child.type == "arguments":
                for arg in child.children:
                    if arg.type == "call_expression" or arg.type == "method_invocation":
                        return True
            elif child.type == "call_expression" or child.type == "method_invocation":
                return True
        return False

    def traverse(u):
        nonlocal count
        if check(u):
            count += 1
        for v in u.children:
            traverse(v)

    traverse(root)
    return count


def get_function_return_type(root, function_name):
    # 获取当前编程语言
    from transform.lang import get_lang
    lang = get_lang()

    def traverse(node):
        # 根据不同语言处理函数定义节点
        if lang == "c" and node.type == "function_definition":
            # 获取函数名
            declarator = node.child_by_field_name("declarator")
            if declarator:
                for child in declarator.children:
                    if child.type == "identifier" and text(child) == function_name:
                        # 获取返回类型
                        type_node = node.child_by_field_name("type")
                        return text(type_node) if type_node else "void"

        elif lang == "java" and node.type == "method_declaration":
            # 获取方法名
            name_node = node.child_by_field_name("name")
            if name_node and text(name_node) == function_name:
                # 获取返回类型
                type_node = node.child_by_field_name("type")
                return text(type_node) if type_node else "void"

        elif lang == "c_sharp" and node.type == "method_declaration":
            # 获取方法名
            name_node = node.child_by_field_name("name")
            if name_node and text(name_node) == function_name:
                # 获取返回类型
                type_node = node.child_by_field_name("type")
                return text(type_node) if type_node else "void"

        elif lang == "python" and node.type == "function_definition":
            # 获取函数名
            name_node = node.child_by_field_name("name")
            if name_node and text(name_node) == function_name:
                # Python是动态类型的，通过类型注解获取返回类型
                returns_node = node.child_by_field_name("return_type")
                return text(returns_node) if returns_node else "object"

        # 递归遍历子节点
        for child in node.children:
            result = traverse(child)
            if result:
                return result

        return None

    return traverse(root)
