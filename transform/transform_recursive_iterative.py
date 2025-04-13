import sys, os

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from ist_utils import text, get_indent, replace_from_blob
from transform.lang import get_lang
import re

"""==========================辅助数据结构和函数========================"""

# 定义递归模式类型
RECURSIVE_PATTERN_FACTORIAL = "factorial"
RECURSIVE_PATTERN_FIBONACCI = "fibonacci"
RECURSIVE_PATTERN_SUM = "sum"
RECURSIVE_PATTERN_TREE_TRAVERSAL = "tree_traversal"
RECURSIVE_PATTERN_BINARY_SEARCH = "binary_search"
RECURSIVE_PATTERN_QUICK_SORT = "quick_sort"
RECURSIVE_PATTERN_MERGE_SORT = "merge_sort"
RECURSIVE_PATTERN_POWER = "power"
RECURSIVE_PATTERN_GCD = "gcd"
RECURSIVE_PATTERN_COMBINATION = "combination"
RECURSIVE_PATTERN_PERMUTATION = "permutation"
RECURSIVE_PATTERN_UNKNOWN = "unknown"

# 堆栈辅助结构模板
STACK_STRUCTURE_TEMPLATES = {
    "c": """
typedef struct Node {
    %s
    struct Node* next;
} Node;

typedef struct {
    Node* top;
} Stack;

Stack* createStack() {
    Stack* stack = (Stack*)malloc(sizeof(Stack));
    stack->top = NULL;
    return stack;
}

int isEmpty(Stack* stack) {
    return stack->top == NULL;
}

void push(Stack* stack, %s) {
    Node* node = (Node*)malloc(sizeof(Node));
    %s
    node->next = stack->top;
    stack->top = node;
}

%s pop(Stack* stack) {
    if (isEmpty(stack)) {
        fprintf(stderr, "Error: Stack underflow\\n");
        exit(1);
    }
    Node* temp = stack->top;
    stack->top = stack->top->next;
    %s result = %s;
    free(temp);
    return result;
}

void freeStack(Stack* stack) {
    Node* current = stack->top;
    while (current != NULL) {
        Node* temp = current;
        current = current->next;
        free(temp);
    }
    free(stack);
}
""",
    "java": """
private static class Stack<%s> {
    private static class Node {
        %s value;
        Node next;

        Node(%s value) {
            this.value = value;
            this.next = null;
        }
    }

    private Node top;

    public Stack() {
        this.top = null;
    }

    public boolean isEmpty() {
        return top == null;
    }

    public void push(%s value) {
        Node node = new Node(value);
        node.next = top;
        top = node;
    }

    public %s pop() {
        if (isEmpty()) {
            throw new RuntimeException("Stack underflow");
        }
        %s value = top.value;
        top = top.next;
        return value;
    }
}
""",
    "c_sharp": """
private class Stack<%s> {
    private class Node {
        public %s Value { get; set; }
        public Node Next { get; set; }

        public Node(%s value) {
            this.Value = value;
            this.Next = null;
        }
    }

    private Node top;

    public Stack() {
        this.top = null;
    }

    public bool IsEmpty() {
        return top == null;
    }

    public void Push(%s value) {
        Node node = new Node(value);
        node.Next = top;
        top = node;
    }

    public %s Pop() {
        if (IsEmpty()) {
            throw new InvalidOperationException("Stack underflow");
        }
        %s value = top.Value;
        top = top.Next;
        return value;
    }
}
"""
}

# 多参数帧结构模板
FRAME_STRUCTURE_TEMPLATES = {
    "c": """
typedef struct {
    %s
} Frame;

typedef struct FrameNode {
    Frame frame;
    struct FrameNode* next;
} FrameNode;

typedef struct {
    FrameNode* top;
} FrameStack;

FrameStack* createFrameStack() {
    FrameStack* stack = (FrameStack*)malloc(sizeof(FrameStack));
    stack->top = NULL;
    return stack;
}

int isFrameStackEmpty(FrameStack* stack) {
    return stack->top == NULL;
}

void pushFrame(FrameStack* stack, Frame frame) {
    FrameNode* node = (FrameNode*)malloc(sizeof(FrameNode));
    node->frame = frame;
    node->next = stack->top;
    stack->top = node;
}

Frame popFrame(FrameStack* stack) {
    if (isFrameStackEmpty(stack)) {
        fprintf(stderr, "Error: FrameStack underflow\\n");
        exit(1);
    }
    FrameNode* temp = stack->top;
    stack->top = stack->top->next;
    Frame result = temp->frame;
    free(temp);
    return result;
}

void freeFrameStack(FrameStack* stack) {
    FrameNode* current = stack->top;
    while (current != NULL) {
        FrameNode* temp = current;
        current = current->next;
        free(temp);
    }
    free(stack);
}
""",
    "java": """
private static class Frame {
    %s

    public Frame(%s) {
        %s
    }
}

private static class FrameStack {
    private static class Node {
        Frame frame;
        Node next;

        Node(Frame frame) {
            this.frame = frame;
            this.next = null;
        }
    }

    private Node top;

    public FrameStack() {
        this.top = null;
    }

    public boolean isEmpty() {
        return top == null;
    }

    public void push(Frame frame) {
        Node node = new Node(frame);
        node.next = top;
        top = node;
    }

    public Frame pop() {
        if (isEmpty()) {
            throw new RuntimeException("FrameStack underflow");
        }
        Frame frame = top.frame;
        top = top.next;
        return frame;
    }

    public Frame peek() {
        if (isEmpty()) {
            throw new RuntimeException("FrameStack underflow");
        }
        return top.frame;
    }
}
""",
    "c_sharp": """
private class Frame {
    %s

    public Frame(%s) {
        %s
    }
}

private class FrameStack {
    private class Node {
        public Frame Frame { get; set; }
        public Node Next { get; set; }

        public Node(Frame frame) {
            this.Frame = frame;
            this.Next = null;
        }
    }

    private Node top;

    public FrameStack() {
        this.top = null;
    }

    public bool IsEmpty() {
        return top == null;
    }

    public void Push(Frame frame) {
        Node node = new Node(frame);
        node.Next = top;
        top = node;
    }

    public Frame Pop() {
        if (IsEmpty()) {
            throw new InvalidOperationException("FrameStack underflow");
        }
        Frame frame = top.Frame;
        top = top.Next;
        return frame;
    }

    public Frame Peek() {
        if (IsEmpty()) {
            throw new InvalidOperationException("FrameStack underflow");
        }
        return top.Frame;
    }
}
"""
}

"""==========================匹配函数========================"""


def match_recursive_functions(root):
    recursive_funcs = {}

    # 第一步：收集所有函数声明
    def collect_functions(node):
        # 添加语言检测
        lang = get_lang()

        if node.type in ["function_definition", "method_declaration"]:
            func_name = None

            # 获取函数名
            if node.type == "function_definition":  # C
                for child in node.children:
                    if child.type == "function_declarator":
                        for decl_child in child.children:
                            if decl_child.type == "identifier":
                                func_name = text(decl_child)
                                break
            else:  # Java/C#
                # 添加对Java的特殊处理
                if lang == "java":
                    # 尝试通过field_name获取
                    name_node = node.child_by_field_name("name")
                    if name_node:
                        func_name = text(name_node)
                    else:
                        # 回退到遍历子节点
                        for child in node.children:
                            if child.type == "identifier":
                                func_name = text(child)
                                break
                            # 处理Java的method_header
                            elif child.type == "method_header":
                                for sub_child in child.children:
                                    if sub_child.type == "identifier":
                                        func_name = text(sub_child)
                                        break
                            # 更深层次查找
                            elif hasattr(child, "children"):
                                for sub_child in child.children:
                                    if sub_child.type == "identifier":
                                        func_name = text(sub_child)
                                        break
                else:  # 原有C#处理逻辑
                    for child in node.children:
                        if child.type == "identifier":
                            func_name = text(child)
                            break

            if func_name:
                recursive_funcs[func_name] = {
                    "node": node,
                    "is_recursive": False,
                    "recursive_calls": 0,
                    "recursion_locations": []
                }

        for child in node.children:
            collect_functions(child)

    # 第二步：检查每个函数是否递归调用自身
    def check_recursion(node, func_name):
        # 添加语言检测
        lang = get_lang()

        # 修改：根据语言选择函数调用节点类型
        call_type = "method_invocation" if lang == "java" else "call_expression"

        if node.type == call_type:
            callee = None

            # 修改：根据语言获取被调用函数名
            if lang == "java":
                name_node = node.child_by_field_name("name")
                if name_node:
                    callee = text(name_node)
            else:  # C/C#
                for child in node.children:
                    if child.type == "identifier":
                        callee = text(child)
                        break

            if callee and callee == func_name:
                recursive_funcs[func_name]["recursive_calls"] += 1
                recursive_funcs[func_name]["recursion_locations"].append(node)
                return True

        for child in node.children:
            if check_recursion(child, func_name):
                recursive_funcs[func_name]["is_recursive"] = True

        return recursive_funcs[func_name]["is_recursive"]

    # 其余代码保持不变
    collect_functions(root)

    for func_name, info in recursive_funcs.items():
        check_recursion(info["node"], func_name)

    res = []
    for func_name, info in recursive_funcs.items():
        if info["is_recursive"]:
            res.append(info["node"])

    return res


def match_mutual_recursive_functions(root):
    """
    匹配互递归函数 - 多个函数相互递归调用的情况
    """
    functions = {}

    # 第一步：收集所有函数声明
    def collect_functions(node):
        if node.type in ["function_definition", "method_declaration"]:
            func_name = None

            # 获取函数名
            if node.type == "function_definition":  # C
                for child in node.children:
                    if child.type == "function_declarator":
                        for decl_child in child.children:
                            if decl_child.type == "identifier":
                                func_name = text(decl_child)
                                break
            else:  # Java/C#
                for child in node.children:
                    if child.type == "identifier":
                        func_name = text(child)
                        break

            if func_name:
                functions[func_name] = {
                    "node": node,
                    "calls": set(),
                    "in_mutual_recursion": False
                }

        for child in node.children:
            collect_functions(child)

    # 第二步：收集每个函数调用了哪些其他函数
    def collect_calls(node, func_name):
        if node.type == "call_expression":
            callee = None

            # 获取被调用的函数名
            for child in node.children:
                if child.type == "identifier":
                    callee = text(child)
                    break

            if callee and callee != func_name and callee in functions:
                functions[func_name]["calls"].add(callee)

        for child in node.children:
            collect_calls(child, func_name)

    collect_functions(root)

    # 收集函数调用关系
    for func_name, info in functions.items():
        collect_calls(info["node"], func_name)

    # 检测互递归
    def is_mutually_recursive(func_name, target, visited=None):
        if visited is None:
            visited = set()

        if func_name in visited:
            return False

        visited.add(func_name)

        if target in functions[func_name]["calls"]:
            return True

        for called in functions[func_name]["calls"]:
            if called in functions and is_mutually_recursive(called, target, visited):
                return True

        return False

    mutual_recursive_groups = []
    processed = set()

    for func_name in functions:
        if func_name in processed:
            continue

        mutual_group = set()

        for other_func in functions:
            if other_func != func_name and other_func not in processed:
                if (other_func in functions[func_name]["calls"] and
                        is_mutually_recursive(other_func, func_name)):
                    mutual_group.add(func_name)
                    mutual_group.add(other_func)
                    functions[func_name]["in_mutual_recursion"] = True
                    functions[other_func]["in_mutual_recursion"] = True

        if mutual_group:
            mutual_recursive_groups.append(mutual_group)
            processed.update(mutual_group)

    # 返回互递归函数的节点
    res = []
    for func_name, info in functions.items():
        if info["in_mutual_recursion"]:
            res.append(info["node"])

    return res, mutual_recursive_groups


def match_iterative_functions(root):
    """
    匹配使用迭代实现的函数 - 通常包含循环但不调用自身
    增强版本支持更多迭代模式
    """
    iterative_funcs = {}

    # 第一步：收集所有函数声明
    def collect_functions(node):
        # 添加语言检测
        lang = get_lang()

        if node.type in ["function_definition", "method_declaration"]:
            func_name = None

            # 修改：根据语言获取函数名
            if node.type == "function_definition":  # C
                for child in node.children:
                    if child.type == "function_declarator":
                        for decl_child in child.children:
                            if decl_child.type == "identifier":
                                func_name = text(decl_child)
                                break
            else:  # Java/C#
                # 添加对Java的特殊处理
                if lang == "java":
                    # 尝试通过field_name获取
                    name_node = node.child_by_field_name("name")
                    if name_node:
                        func_name = text(name_node)
                    else:
                        # 回退到遍历子节点
                        for child in node.children:
                            if child.type == "identifier":
                                func_name = text(child)
                                break
                            # 处理Java的method_header
                            elif child.type == "method_header":
                                for sub_child in child.children:
                                    if sub_child.type == "identifier":
                                        func_name = text(sub_child)
                                        break
                else:
                    for child in node.children:
                        if child.type == "identifier":
                            func_name = text(child)
                            break

            if func_name:
                iterative_funcs[func_name] = {
                    "node": node,
                    "has_loop": False,
                    "is_recursive": False,
                    "loop_types": [],
                    "pattern": None
                }

        for child in node.children:
            collect_functions(child)

    # 第二步：检查每个函数是否包含循环且不递归调用自身
    def check_loop(node, func_info):
        if node.type in ["for_statement", "while_statement", "do_statement"]:
            func_info["has_loop"] = True
            func_info["loop_types"].append(node.type)

            # 尝试识别迭代模式
            loop_text = text(node)

            if "+=" in loop_text:
                if "result" in loop_text or "sum" in loop_text:
                    func_info["pattern"] = RECURSIVE_PATTERN_SUM
                elif "i++" in loop_text or "i+1" in loop_text:
                    if "*=" in loop_text or "result *" in loop_text:
                        func_info["pattern"] = RECURSIVE_PATTERN_FACTORIAL
                    elif "prev" in loop_text or "temp" in loop_text:
                        func_info["pattern"] = RECURSIVE_PATTERN_FIBONACCI
            elif "*=" in loop_text:
                if "pow" in loop_text or "power" in loop_text:
                    func_info["pattern"] = RECURSIVE_PATTERN_POWER
                else:
                    func_info["pattern"] = RECURSIVE_PATTERN_FACTORIAL
            elif "mid" in loop_text and ("left" in loop_text or "right" in loop_text):
                func_info["pattern"] = RECURSIVE_PATTERN_BINARY_SEARCH
            elif "partition" in loop_text or "pivot" in loop_text:
                func_info["pattern"] = RECURSIVE_PATTERN_QUICK_SORT
            elif "merge" in loop_text:
                func_info["pattern"] = RECURSIVE_PATTERN_MERGE_SORT
            elif "stack" in loop_text or "push" in loop_text:
                func_info["pattern"] = RECURSIVE_PATTERN_TREE_TRAVERSAL
            elif "%" in loop_text or "remainder" in loop_text:
                func_info["pattern"] = RECURSIVE_PATTERN_GCD

        for child in node.children:
            check_loop(child, func_info)

    def check_recursion(node, func_name):
        # 添加语言检测
        lang = get_lang()

        # 修改：根据语言选择函数调用节点类型
        call_type = "method_invocation" if lang == "java" else "call_expression"

        if node.type == call_type:
            callee = None

            # 修改：根据语言获取被调用函数名
            if lang == "java":
                name_node = node.child_by_field_name("name")
                if name_node:
                    callee = text(name_node)
            else:  # C/C#
                for child in node.children:
                    if child.type == "identifier":
                        callee = text(child)
                        break

            if callee and callee == func_name:
                return True

        # 递归检查子节点
        for child in node.children:
            if check_recursion(child, func_name):
                return True

        return False

    # 其余代码保持不变
    collect_functions(root)

    for func_name, info in iterative_funcs.items():
        check_loop(info["node"], info)
        info["is_recursive"] = check_recursion(info["node"], func_name)

    res = []
    for func_name, info in iterative_funcs.items():
        if info["has_loop"] and not info["is_recursive"]:
            res.append(info["node"])

    return res


"""==========================递归模式分析函数========================"""


def analyze_recursive_pattern(node, func_name):
    """
    分析递归函数的模式，返回模式类型和相关信息
    """
    # 添加语言检测
    lang = get_lang()
    # 检查函数名称中的提示
    func_name_lower = func_name.lower()
    if "factorial" in func_name_lower:
        return RECURSIVE_PATTERN_FACTORIAL
    elif "fibonacci" in func_name_lower or "fib" in func_name_lower:
        return RECURSIVE_PATTERN_FIBONACCI
    elif "sum" in func_name_lower or "add" in func_name_lower:
        return RECURSIVE_PATTERN_SUM
    elif "traverse" in func_name_lower or "inorder" in func_name_lower or "preorder" in func_name_lower or "postorder" in func_name_lower:
        return RECURSIVE_PATTERN_TREE_TRAVERSAL
    elif "search" in func_name_lower and "binary" in func_name_lower:
        return RECURSIVE_PATTERN_BINARY_SEARCH
    elif "quicksort" in func_name_lower or "quick_sort" in func_name_lower:
        return RECURSIVE_PATTERN_QUICK_SORT
    elif "mergesort" in func_name_lower or "merge_sort" in func_name_lower:
        return RECURSIVE_PATTERN_MERGE_SORT
    elif "power" in func_name_lower or "pow" in func_name_lower:
        return RECURSIVE_PATTERN_POWER
    elif "gcd" in func_name_lower or "greatest_common_divisor" in func_name_lower:
        return RECURSIVE_PATTERN_GCD
    elif "permutation" in func_name_lower or "permute" in func_name_lower:
        return RECURSIVE_PATTERN_PERMUTATION
    elif "combination" in func_name_lower or "choose" in func_name_lower:
        return RECURSIVE_PATTERN_COMBINATION

    # 分析函数体以识别模式
    body = None

    # 根据语言查找函数体/方法体
    if lang == "c":
        for child in node.children:
            if child.type == "compound_statement":
                body = child
                break
    else:  # Java/C#
        # 尝试通过field_name获取
        body = node.child_by_field_name("body")
        if not body:
            # 回退到遍历
            for child in node.children:
                if child.type == "block":
                    body = child
                    break

    if not body:
        return RECURSIVE_PATTERN_UNKNOWN

    body_text = text(body)

    # 识别模式特征
    if "*" in body_text and func_name in body_text and "-1" in body_text:
        return RECURSIVE_PATTERN_FACTORIAL
    elif "+" in body_text and func_name in body_text and "-1" in body_text and "-2" in body_text:
        return RECURSIVE_PATTERN_FIBONACCI
    elif "+" in body_text and func_name in body_text and "-1" in body_text:
        return RECURSIVE_PATTERN_SUM
    elif "mid" in body_text and ("left" in body_text or "right" in body_text):
        return RECURSIVE_PATTERN_BINARY_SEARCH
    elif "partition" in body_text or "pivot" in body_text:
        return RECURSIVE_PATTERN_QUICK_SORT
    elif "merge" in body_text:
        return RECURSIVE_PATTERN_MERGE_SORT
    elif ("left" in body_text and "right" in body_text) or "tree" in body_text:
        return RECURSIVE_PATTERN_TREE_TRAVERSAL
    elif "*" in body_text and "power" in body_text:
        return RECURSIVE_PATTERN_POWER
    elif "%" in body_text or "remainder" in body_text:
        return RECURSIVE_PATTERN_GCD
    elif "swap" in body_text or "permute" in body_text:
        return RECURSIVE_PATTERN_PERMUTATION
    elif "choose" in body_text or "combination" in body_text:
        return RECURSIVE_PATTERN_COMBINATION

    return RECURSIVE_PATTERN_UNKNOWN


def is_simple_recursive_function(node):
    """
    检查是否是简单的递归函数，如阶乘、斐波那契等
    这些函数更容易转换为迭代形式
    增强版本支持更多模式
    """
    # 获取函数名
    func_name = None
    if node.type == "function_definition":  # C
        for child in node.children:
            if child.type == "function_declarator":
                for decl_child in child.children:
                    if decl_child.type == "identifier":
                        func_name = text(decl_child)
                        break
    else:  # Java/C#
        for child in node.children:
            if child.type == "identifier":
                func_name = text(child)
                break
                # 处理带类型参数的方法声明（如泛型）
            elif child.type == "method_header":
                for sub_child in child.children:
                    if sub_child.type == "identifier":
                        func_name = text(sub_child)
                        break

    if not func_name:
        return False

    # 分析递归模式
    pattern = analyze_recursive_pattern(node, func_name)

    # 这些模式通常有简单的迭代转换
    simple_patterns = [
        RECURSIVE_PATTERN_FACTORIAL,
        RECURSIVE_PATTERN_FIBONACCI,
        RECURSIVE_PATTERN_SUM,
        RECURSIVE_PATTERN_POWER,
        RECURSIVE_PATTERN_GCD
    ]

    return pattern in simple_patterns


def is_tail_recursive(node, func_name):
    """
    检查函数是否是尾递归函数
    尾递归是指递归调用是函数体中最后执行的操作
    """
    # 查找所有递归调用
    recursive_calls = []

    def find_recursive_calls(n):
        if n.type == "call_expression":
            callee = None
            for child in n.children:
                if child.type == "identifier":
                    callee = text(child)
                    break

            if callee and callee == func_name:
                # 找到包含此调用的语句
                current = n
                while current and current.parent and current.parent.type not in ["compound_statement", "block"]:
                    current = current.parent

                if current and current.parent:
                    recursive_calls.append(current)

        for child in n.children:
            find_recursive_calls(child)

    find_recursive_calls(node)

    # 检查递归调用是否都是在返回语句中
    for call in recursive_calls:
        if call.type != "return_statement":
            parent = call
            while parent and parent.type != "return_statement" and parent.parent and parent.parent.type not in [
                "compound_statement", "block"]:
                parent = parent.parent

            if not parent or parent.type != "return_statement":
                return False

    return len(recursive_calls) > 0


def is_tree_recursive(node, func_name):
    """
    检查函数是否是树递归函数
    树递归是指函数中多次调用自身，如斐波那契数列
    """
    # 统计递归调用次数
    recursive_calls = 0

    def count_recursive_calls(n):
        nonlocal recursive_calls
        if n.type == "call_expression":
            callee = None
            for child in n.children:
                if child.type == "identifier":
                    callee = text(child)
                    break

            if callee and callee == func_name:
                recursive_calls += 1

        for child in n.children:
            count_recursive_calls(child)

    count_recursive_calls(node)

    return recursive_calls > 1


def analyze_parameters(node):
    """分析函数参数，增强版本支持Java/C#的复杂参数类型"""
    lang = get_lang()
    params = []

    if lang == "c":  # C语言
        # 原有C语言处理代码保持不变
        if node.type == "function_definition":
            for child in node.children:
                if child.type == "function_declarator":
                    for decl_child in child.children:
                        if decl_child.type == "parameter_list":
                            for param in decl_child.children:
                                if param.type == "parameter_declaration":
                                    param_name = None
                                    param_type = None
                                    is_pointer = False

                                    for param_child in param.children:
                                        if param_child.type == "identifier":
                                            param_name = text(param_child)
                                        elif param_child.type in ["primitive_type", "type_identifier"]:
                                            param_type = text(param_child)
                                        elif param_child.type == "pointer_declarator":
                                            is_pointer = True
                                            for ptr_child in param_child.children:
                                                if ptr_child.type == "identifier":
                                                    param_name = text(ptr_child)

                                    if param_name and param_type:
                                        params.append({
                                            "name": param_name,
                                            "type": param_type,
                                            "is_pointer": is_pointer
                                        })
    else:  # Java/C#
        # 添加Java/C#专用处理代码
        if node.type == "method_declaration":
            # 尝试直接通过field_name获取参数列表
            params_node = node.child_by_field_name("parameters")
            if params_node and params_node.type == "formal_parameters":
                for param in params_node.children:
                    if param.type == "formal_parameter":
                        param_name = None
                        param_type = None

                        # 尝试通过field_name获取
                        name_node = param.child_by_field_name("name")
                        type_node = param.child_by_field_name("type")

                        if name_node:
                            param_name = text(name_node)
                        if type_node:
                            param_type = text(type_node)

                        # 回退到遍历
                        if not param_name or not param_type:
                            for param_child in param.children:
                                if param_child.type == "identifier" and not param_name:
                                    param_name = text(param_child)
                                elif param_child.type in ["primitive_type", "type_identifier"] and not param_type:
                                    param_type = text(param_child)

                        if param_name and param_type:
                            params.append({
                                "name": param_name,
                                "type": param_type,
                                "is_pointer": False
                            })
            else:
                # 如果没有通过field_name找到，递归搜索
                def find_formal_parameters(n):
                    if n.type == "formal_parameters":
                        return n
                    for child in n.children:
                        if hasattr(child, "children"):
                            result = find_formal_parameters(child)
                            if result:
                                return result
                    return None

                formal_params = find_formal_parameters(node)

                if formal_params:
                    # 处理找到的formal_parameters
                    # 这部分代码与原有代码类似，但需要适配Java的节点结构
                    for param in formal_params.children:
                        if param.type == "formal_parameter":
                            param_name = None
                            param_type = None

                            for param_child in param.children:
                                if param_child.type == "identifier":
                                    param_name = text(param_child)
                                elif param_child.type in ["primitive_type", "type_identifier"]:
                                    param_type = text(param_child)

                            if param_name and param_type:
                                params.append({
                                    "name": param_name,
                                    "type": param_type,
                                    "is_pointer": False
                                })

    return params


def find_method_identifier_recursive(node):
    """Helper function to recursively find identifiers in complex method structures"""
    if node.type == "identifier":
        return text(node)

    if hasattr(node, "children"):
        for child in node.children:
            result = find_method_identifier_recursive(child)
            if result:
                return result

    return None


def find_block_or_compound_statement(node):
    """Find the function body/block in different languages"""
    if node.type in ["compound_statement", "block"]:
        return node

    if hasattr(node, "children"):
        for child in node.children:
            result = find_block_or_compound_statement(child)
            if result:
                return result

    return None


def extract_function_info(node):
    """提取函数名和返回类型，改进对Java/C#的支持"""
    lang = get_lang()
    func_name = None
    return_type = None

    # 根据语言选择处理方式
    if lang == "c":  # C语言
        if node.type == "function_definition":
            # 获取返回类型
            for child in node.children:
                if child.type in ["primitive_type", "type_identifier"]:
                    return_type = text(child)
                elif child.type == "function_declarator":
                    for decl_child in child.children:
                        if decl_child.type == "identifier":
                            func_name = text(decl_child)
                            break
    else:  # Java/C#
        if node.type == "method_declaration":
            # 尝试通过field_name获取类型和名称
            type_node = node.child_by_field_name("type")
            if type_node:
                return_type = text(type_node)

            name_node = node.child_by_field_name("name")
            if name_node:
                func_name = text(name_node)
            else:
                # 如果field_name不可用，回退到子节点遍历
                for child in node.children:
                    if child.type in ["primitive_type", "type_identifier"] and not return_type:
                        return_type = text(child)
                    elif child.type == "identifier" and not func_name:
                        func_name = text(child)
                    # 处理method_header包含的信息
                    elif child.type == "method_header":
                        for sub_child in child.children:
                            if sub_child.type in ["primitive_type", "type_identifier"] and not return_type:
                                return_type = text(sub_child)
                            elif sub_child.type == "identifier" and not func_name:
                                func_name = text(sub_child)

    return func_name, return_type

def extract_base_case(node, func_name):
    """
    提取递归函数的基本情况
    """
    base_cases = []

    def find_base_cases(n):
        if n.type == "if_statement":
            # 检查if语句是否不包含递归调用，可能是基本情况
            has_recursive_call = False

            def check_for_recursive_call(m):
                nonlocal has_recursive_call
                if m.type == "call_expression":
                    callee = None
                    for child in m.children:
                        if child.type == "identifier":
                            callee = text(child)
                            break

                    if callee and callee == func_name:
                        has_recursive_call = True

                for child in m.children:
                    check_for_recursive_call(child)

            check_for_recursive_call(n)

            if not has_recursive_call:
                base_cases.append(n)

        for child in n.children:
            find_base_cases(child)

    find_base_cases(node)

    return base_cases


def extract_recursive_step(node, func_name):
    """
    提取递归函数的递归步骤
    """
    recursive_steps = []

    def find_recursive_steps(n):
        if n.type == "call_expression":
            callee = None
            for child in n.children:
                if child.type == "identifier":
                    callee = text(child)
                    break

            if callee and callee == func_name:
                # 找到包含此调用的语句
                current = n
                while current and current.parent and current.parent.type not in ["compound_statement", "block"]:
                    current = current.parent

                if current and current.parent:
                    recursive_steps.append((current, n))

        for child in n.children:
            find_recursive_steps(child)

    find_recursive_steps(node)

    return recursive_steps


def analyze_recursive_argument_patterns(node, func_name, params):
    """
    分析递归调用中参数的变化模式
    """
    if not params:
        return {}

    recursive_calls = []

    def find_recursive_calls(n):
        if n.type == "call_expression":
            callee = None
            for child in n.children:
                if child.type == "identifier":
                    callee = text(child)
                    break

            if callee and callee == func_name:
                args = []
                for child in n.children:
                    if child.type == "argument_list":
                        for arg in child.children:
                            if arg.type not in ["(", ")", ","]:
                                args.append(text(arg))

                recursive_calls.append(args)

        for child in n.children:
            find_recursive_calls(child)

    find_recursive_calls(node)

    if not recursive_calls:
        return {}

    # 分析每个参数的变化模式
    param_patterns = {}
    for i, param in enumerate(params):
        param_name = param["name"]
        param_patterns[param_name] = {"pattern": None, "operations": []}

        for call_args in recursive_calls:
            if i < len(call_args):
                arg = call_args[i]

                # 识别常见的参数变化模式
                if arg == param_name:
                    continue  # 参数值未变化
                elif param_name + " + 1" in arg or param_name + "+1" in arg:
                    param_patterns[param_name]["pattern"] = "increment"
                    param_patterns[param_name]["operations"].append("+1")
                elif param_name + " - 1" in arg or param_name + "-1" in arg:
                    param_patterns[param_name]["pattern"] = "decrement"
                    param_patterns[param_name]["operations"].append("-1")
                elif "* 2" in arg or "*2" in arg:
                    param_patterns[param_name]["pattern"] = "multiply"
                    param_patterns[param_name]["operations"].append("*2")
                elif "/ 2" in arg or "/2" in arg:
                    param_patterns[param_name]["pattern"] = "divide"
                    param_patterns[param_name]["operations"].append("/2")
                elif "mid" in arg:
                    param_patterns[param_name]["pattern"] = "binary_search"
                elif param_name + " + " in arg:
                    param_patterns[param_name]["pattern"] = "add"
                    match = re.search(r'\+ (\w+)', arg)
                    if match:
                        param_patterns[param_name]["operations"].append("+" + match.group(1))
                elif param_name + " - " in arg:
                    param_patterns[param_name]["pattern"] = "subtract"
                    match = re.search(r'- (\w+)', arg)
                    if match:
                        param_patterns[param_name]["operations"].append("-" + match.group(1))
                else:
                    param_patterns[param_name]["pattern"] = "unknown"
                    param_patterns[param_name]["operations"].append(arg)

    return param_patterns


"""==========================转换函数========================"""


def create_stack_structure(lang, value_type, field_names=None):
    """
    创建适合当前语言的堆栈结构代码
    """
    if not field_names:
        if lang == "c":
            node_fields = f"{value_type} value;"
            push_fields = f"node->value = value;"
            pop_expr = "temp->value"
        else:  # Java/C#
            return STACK_STRUCTURE_TEMPLATES[lang] % (
            value_type, value_type, value_type, value_type, value_type, value_type)
    else:
        # 多字段堆栈结构（用于框架栈）
        if lang == "c":
            node_fields = "\n    ".join([f"{field['type']} {field['name']};" for field in field_names])
            push_fields = "\n    ".join(
                [f"node->value.{field['name']} = value.{field['name']};" for field in field_names])
            pop_expr = "temp->value"
        else:  # Java/C#
            fields_decl = "\n        ".join([f"public {field['type']} {field['name']};" for field in field_names])
            param_decl = ", ".join([f"{field['type']} {field['name']}" for field in field_names])
            fields_init = "\n            ".join([f"this.{field['name']} = {field['name']};" for field in field_names])

            if lang == "java":
                return FRAME_STRUCTURE_TEMPLATES[lang] % (fields_decl, param_decl, fields_init)
            else:  # C#
                return FRAME_STRUCTURE_TEMPLATES[lang] % (fields_decl, param_decl, fields_init)

    if lang == "c":
        return STACK_STRUCTURE_TEMPLATES[lang] % (
        node_fields, value_type, push_fields, value_type, value_type, pop_expr)

    return ""


def convert_recursive_factorial_to_iterative(node, code, func_name, return_type, params, base_indent, inner_indent):
    """
    将递归阶乘函数转换为迭代实现
    """
    param_name = params[0]["name"]

    new_body = "{\n"
    new_body += f"{' ' * inner_indent}if ({param_name} <= 1) {{\n"
    new_body += f"{' ' * (inner_indent + 4)}return 1;\n"
    new_body += f"{' ' * inner_indent}}}\n\n"
    new_body += f"{' ' * inner_indent}int result = 1;\n"
    new_body += f"{' ' * inner_indent}for (int i = 2; i <= {param_name}; i++) {{\n"
    new_body += f"{' ' * (inner_indent + 4)}result *= i;\n"
    new_body += f"{' ' * inner_indent}}}\n\n"
    new_body += f"{' ' * inner_indent}return result;\n"
    new_body += f"{' ' * base_indent}}}"

    return new_body


def convert_recursive_fibonacci_to_iterative(node, code, func_name, return_type, params, base_indent, inner_indent):
    """
    将递归斐波那契函数转换为迭代实现
    """
    param_name = params[0]["name"]

    new_body = "{\n"
    new_body += f"{' ' * inner_indent}if ({param_name} <= 1) {{\n"
    new_body += f"{' ' * (inner_indent + 4)}return {param_name};\n"
    new_body += f"{' ' * inner_indent}}}\n\n"
    new_body += f"{' ' * inner_indent}int a = 0;\n"
    new_body += f"{' ' * inner_indent}int b = 1;\n"
    new_body += f"{' ' * inner_indent}int result = 0;\n\n"
    new_body += f"{' ' * inner_indent}for (int i = 2; i <= {param_name}; i++) {{\n"
    new_body += f"{' ' * (inner_indent + 4)}result = a + b;\n"
    new_body += f"{' ' * (inner_indent + 4)}a = b;\n"
    new_body += f"{' ' * (inner_indent + 4)}b = result;\n"
    new_body += f"{' ' * inner_indent}}}\n\n"
    new_body += f"{' ' * inner_indent}return b;\n"
    new_body += f"{' ' * base_indent}}}"

    return new_body


def convert_recursive_sum_to_iterative(node, code, func_name, return_type, params, base_indent, inner_indent):
    """
    将递归求和函数转换为迭代实现
    """
    param_name = params[0]["name"]

    new_body = "{\n"
    new_body += f"{' ' * inner_indent}if ({param_name} <= 0) {{\n"
    new_body += f"{' ' * (inner_indent + 4)}return 0;\n"
    new_body += f"{' ' * inner_indent}}}\n\n"
    new_body += f"{' ' * inner_indent}int sum = 0;\n"
    new_body += f"{' ' * inner_indent}for (int i = 1; i <= {param_name}; i++) {{\n"
    new_body += f"{' ' * (inner_indent + 4)}sum += i;\n"
    new_body += f"{' ' * inner_indent}}}\n\n"
    new_body += f"{' ' * inner_indent}return sum;\n"
    new_body += f"{' ' * base_indent}}}"

    return new_body


def convert_recursive_power_to_iterative(node, code, func_name, return_type, params, base_indent, inner_indent):
    """
    将递归求幂函数转换为迭代实现
    """
    base_param = params[0]["name"]
    exp_param = params[1]["name"]

    new_body = "{\n"
    new_body += f"{' ' * inner_indent}if ({exp_param} == 0) {{\n"
    new_body += f"{' ' * (inner_indent + 4)}return 1;\n"
    new_body += f"{' ' * inner_indent}}}\n\n"
    new_body += f"{' ' * inner_indent}int result = 1;\n"
    new_body += f"{' ' * inner_indent}for (int i = 0; i < {exp_param}; i++) {{\n"
    new_body += f"{' ' * (inner_indent + 4)}result *= {base_param};\n"
    new_body += f"{' ' * inner_indent}}}\n\n"
    new_body += f"{' ' * inner_indent}return result;\n"
    new_body += f"{' ' * base_indent}}}"

    return new_body


def convert_recursive_gcd_to_iterative(node, code, func_name, return_type, params, base_indent, inner_indent):
    """
    将递归最大公约数函数转换为迭代实现
    """
    a_param = params[0]["name"]
    b_param = params[1]["name"]

    new_body = "{\n"
    new_body += f"{' ' * inner_indent}if ({b_param} == 0) {{\n"
    new_body += f"{' ' * (inner_indent + 4)}return {a_param};\n"
    new_body += f"{' ' * inner_indent}}}\n\n"
    new_body += f"{' ' * inner_indent}int a = {a_param};\n"
    new_body += f"{' ' * inner_indent}int b = {b_param};\n"
    new_body += f"{' ' * inner_indent}int temp;\n\n"
    new_body += f"{' ' * inner_indent}while (b != 0) {{\n"
    new_body += f"{' ' * (inner_indent + 4)}temp = b;\n"
    new_body += f"{' ' * (inner_indent + 4)}b = a % b;\n"
    new_body += f"{' ' * (inner_indent + 4)}a = temp;\n"
    new_body += f"{' ' * inner_indent}}}\n\n"
    new_body += f"{' ' * inner_indent}return a;\n"
    new_body += f"{' ' * base_indent}}}"

    return new_body


def convert_recursive_binary_search_to_iterative(node, code, func_name, return_type, params, base_indent, inner_indent):
    """
    将递归二分查找函数转换为迭代实现
    """
    array_param = params[0]["name"]
    target_param = None
    left_param = None
    right_param = None

    # 尝试识别参数名称
    for param in params[1:]:
        name = param["name"]
        if name in ["target", "key", "x", "value"]:
            target_param = name
        elif name in ["left", "low", "start", "l"]:
            left_param = name
        elif name in ["right", "high", "end", "r"]:
            right_param = name

    # 使用默认名称
    if not target_param:
        target_param = params[1]["name"] if len(params) > 1 else "target"
    if not left_param:
        left_param = params[2]["name"] if len(params) > 2 else "left"
    if not right_param:
        right_param = params[3]["name"] if len(params) > 3 else "right"

    new_body = "{\n"
    new_body += f"{' ' * inner_indent}int {left_param} = 0;\n"
    new_body += f"{' ' * inner_indent}int {right_param} = ";

    # 检查右边界是否已作为参数传入
    if len(params) > 3 and right_param == params[3]["name"]:
        new_body += f"{right_param};\n\n"
    else:
        new_body += f"/* array length - 1 */;\n\n"

    new_body += f"{' ' * inner_indent}while ({left_param} <= {right_param}) {{\n"
    new_body += f"{' ' * (inner_indent + 4)}int mid = {left_param} + ({right_param} - {left_param}) / 2;\n\n"
    new_body += f"{' ' * (inner_indent + 4)}// Check if target is present at mid\n"
    new_body += f"{' ' * (inner_indent + 4)}if ({array_param}[mid] == {target_param}) {{\n"
    new_body += f"{' ' * (inner_indent + 8)}return mid;\n"
    new_body += f"{' ' * (inner_indent + 4)}}}\n\n"
    new_body += f"{' ' * (inner_indent + 4)}// If target greater, ignore left half\n"
    new_body += f"{' ' * (inner_indent + 4)}if ({array_param}[mid] < {target_param}) {{\n"
    new_body += f"{' ' * (inner_indent + 8)}{left_param} = mid + 1;\n"
    new_body += f"{' ' * (inner_indent + 4)}}} else {{\n"
    new_body += f"{' ' * (inner_indent + 8)}{right_param} = mid - 1;\n"
    new_body += f"{' ' * (inner_indent + 4)}}}\n"
    new_body += f"{' ' * inner_indent}}}\n\n"
    new_body += f"{' ' * inner_indent}// Element not present\n"
    new_body += f"{' ' * inner_indent}return -1;\n"
    new_body += f"{' ' * base_indent}}}"

    return new_body


def convert_recursive_tree_traversal_to_iterative(node, code, func_name, return_type, params, base_indent, inner_indent,
                                                  lang):
    """
    将递归树遍历函数转换为迭代实现
    """
    root_param = params[0]["name"]

    # 判断是哪种遍历方式
    body_text = ""
    for child in node.children:
        if child.type in ["compound_statement", "block"]:
            body_text = text(child)
            break

    traversal_type = "inorder"  # 默认
    if "visit" in body_text:
        if "left" in body_text and body_text.find("visit") < body_text.find("left"):
            traversal_type = "preorder"
        elif "right" in body_text and body_text.find("visit") > body_text.find("right"):
            traversal_type = "postorder"

    # 创建堆栈结构
    stack_struct = create_stack_structure(lang, "TreeNode*" if lang == "c" else "TreeNode")

    new_body = "{\n"

    if traversal_type == "inorder":
        new_body += f"{' ' * inner_indent}// Iterative Inorder Traversal\n"
        if lang == "c":
            new_body += f"{' ' * inner_indent}if ({root_param} == NULL) {{\n"
            new_body += f"{' ' * (inner_indent + 4)}return;\n"
            new_body += f"{' ' * inner_indent}}}\n\n"
            new_body += f"{' ' * inner_indent}Stack* stack = createStack();\n"
            new_body += f"{' ' * inner_indent}TreeNode* current = {root_param};\n\n"
            new_body += f"{' ' * inner_indent}while (current != NULL || !isEmpty(stack)) {{\n"
            new_body += f"{' ' * (inner_indent + 4)}// Reach the leftmost node of the current node\n"
            new_body += f"{' ' * (inner_indent + 4)}while (current != NULL) {{\n"
            new_body += f"{' ' * (inner_indent + 8)}push(stack, current);\n"
            new_body += f"{' ' * (inner_indent + 8)}current = current->left;\n"
            new_body += f"{' ' * (inner_indent + 4)}}}\n\n"
            new_body += f"{' ' * (inner_indent + 4)}// Current must be NULL at this point\n"
            new_body += f"{' ' * (inner_indent + 4)}current = pop(stack);\n\n"
            new_body += f"{' ' * (inner_indent + 4)}// Visit the node\n"
            new_body += f"{' ' * (inner_indent + 4)}printf(\"%d \", current->value); // Or other visit operation\n\n"
            new_body += f"{' ' * (inner_indent + 4)}// Go to the right subtree\n"
            new_body += f"{' ' * (inner_indent + 4)}current = current->right;\n"
            new_body += f"{' ' * inner_indent}}}\n\n"
            new_body += f"{' ' * inner_indent}freeStack(stack);\n"
        elif lang == "java":
            new_body += f"{' ' * inner_indent}if ({root_param} == null) {{\n"
            new_body += f"{' ' * (inner_indent + 4)}return;\n"
            new_body += f"{' ' * inner_indent}}}\n\n"
            new_body += f"{' ' * inner_indent}Stack<TreeNode> stack = new Stack<>();\n"
            new_body += f"{' ' * inner_indent}TreeNode current = {root_param};\n\n"
            new_body += f"{' ' * inner_indent}while (current != null || !stack.isEmpty()) {{\n"
            new_body += f"{' ' * (inner_indent + 4)}// Reach the leftmost node of the current node\n"
            new_body += f"{' ' * (inner_indent + 4)}while (current != null) {{\n"
            new_body += f"{' ' * (inner_indent + 8)}stack.push(current);\n"
            new_body += f"{' ' * (inner_indent + 8)}current = current.left;\n"
            new_body += f"{' ' * (inner_indent + 4)}}}\n\n"
            new_body += f"{' ' * (inner_indent + 4)}// Current must be null at this point\n"
            new_body += f"{' ' * (inner_indent + 4)}current = stack.pop();\n\n"
            new_body += f"{' ' * (inner_indent + 4)}// Visit the node\n"
            new_body += f"{' ' * (inner_indent + 4)}System.out.print(current.value + \" \"); // Or other visit operation\n\n"
            new_body += f"{' ' * (inner_indent + 4)}// Go to the right subtree\n"
            new_body += f"{' ' * (inner_indent + 4)}current = current.right;\n"
            new_body += f"{' ' * inner_indent}}}\n"
        else:  # C#
            new_body += f"{' ' * inner_indent}if ({root_param} == null) {{\n"
            new_body += f"{' ' * (inner_indent + 4)}return;\n"
            new_body += f"{' ' * inner_indent}}}\n\n"
            new_body += f"{' ' * inner_indent}Stack<TreeNode> stack = new Stack<TreeNode>();\n"
            new_body += f"{' ' * inner_indent}TreeNode current = {root_param};\n\n"
            new_body += f"{' ' * inner_indent}while (current != null || stack.Count > 0) {{\n"
            new_body += f"{' ' * (inner_indent + 4)}// Reach the leftmost node of the current node\n"
            new_body += f"{' ' * (inner_indent + 4)}while (current != null) {{\n"
            new_body += f"{' ' * (inner_indent + 8)}stack.Push(current);\n"
            new_body += f"{' ' * (inner_indent + 8)}current = current.Left;\n"
            new_body += f"{' ' * (inner_indent + 4)}}}\n\n"
            new_body += f"{' ' * (inner_indent + 4)}// Current must be null at this point\n"
            new_body += f"{' ' * (inner_indent + 4)}current = stack.Pop();\n\n"
            new_body += f"{' ' * (inner_indent + 4)}// Visit the node\n"
            new_body += f"{' ' * (inner_indent + 4)}Console.Write(current.Value + \" \"); // Or other visit operation\n\n"
            new_body += f"{' ' * (inner_indent + 4)}// Go to the right subtree\n"
            new_body += f"{' ' * (inner_indent + 4)}current = current.Right;\n"
            new_body += f"{' ' * inner_indent}}}\n"
    elif traversal_type == "preorder":
        new_body += f"{' ' * inner_indent}// Iterative Preorder Traversal\n"
        if lang == "c":
            new_body += f"{' ' * inner_indent}if ({root_param} == NULL) {{\n"
            new_body += f"{' ' * (inner_indent + 4)}return;\n"
            new_body += f"{' ' * inner_indent}}}\n\n"
            new_body += f"{' ' * inner_indent}Stack* stack = createStack();\n"
            new_body += f"{' ' * inner_indent}push(stack, {root_param});\n\n"
            new_body += f"{' ' * inner_indent}while (!isEmpty(stack)) {{\n"
            new_body += f"{' ' * (inner_indent + 4)}TreeNode* current = pop(stack);\n\n"
            new_body += f"{' ' * (inner_indent + 4)}// Visit the node\n"
            new_body += f"{' ' * (inner_indent + 4)}printf(\"%d \", current->value); // Or other visit operation\n\n"
            new_body += f"{' ' * (inner_indent + 4)}// Push right child first so that left is processed first\n"
            new_body += f"{' ' * (inner_indent + 4)}if (current->right != NULL) {{\n"
            new_body += f"{' ' * (inner_indent + 8)}push(stack, current->right);\n"
            new_body += f"{' ' * (inner_indent + 4)}}}\n"
            new_body += f"{' ' * (inner_indent + 4)}if (current->left != NULL) {{\n"
            new_body += f"{' ' * (inner_indent + 8)}push(stack, current->left);\n"
            new_body += f"{' ' * (inner_indent + 4)}}}\n"
            new_body += f"{' ' * inner_indent}}}\n\n"
            new_body += f"{' ' * inner_indent}freeStack(stack);\n"
        elif lang == "java":
            new_body += f"{' ' * inner_indent}if ({root_param} == null) {{\n"
            new_body += f"{' ' * (inner_indent + 4)}return;\n"
            new_body += f"{' ' * inner_indent}}}\n\n"
            new_body += f"{' ' * inner_indent}Stack<TreeNode> stack = new Stack<>();\n"
            new_body += f"{' ' * inner_indent}stack.push({root_param});\n\n"
            new_body += f"{' ' * inner_indent}while (!stack.isEmpty()) {{\n"
            new_body += f"{' ' * (inner_indent + 4)}TreeNode current = stack.pop();\n\n"
            new_body += f"{' ' * (inner_indent + 4)}// Visit the node\n"
            new_body += f"{' ' * (inner_indent + 4)}System.out.print(current.value + \" \"); // Or other visit operation\n\n"
            new_body += f"{' ' * (inner_indent + 4)}// Push right child first so that left is processed first\n"
            new_body += f"{' ' * (inner_indent + 4)}if (current.right != null) {{\n"
            new_body += f"{' ' * (inner_indent + 8)}stack.push(current.right);\n"
            new_body += f"{' ' * (inner_indent + 4)}}}\n"
            new_body += f"{' ' * (inner_indent + 4)}if (current.left != null) {{\n"
            new_body += f"{' ' * (inner_indent + 8)}stack.push(current.left);\n"
            new_body += f"{' ' * (inner_indent + 4)}}}\n"
            new_body += f"{' ' * inner_indent}}}\n"
        else:  # C#
            new_body += f"{' ' * inner_indent}if ({root_param} == null) {{\n"
            new_body += f"{' ' * (inner_indent + 4)}return;\n"
            new_body += f"{' ' * inner_indent}}}\n\n"
            new_body += f"{' ' * inner_indent}Stack<TreeNode> stack = new Stack<TreeNode>();\n"
            new_body += f"{' ' * inner_indent}stack.Push({root_param});\n\n"
            new_body += f"{' ' * inner_indent}while (stack.Count > 0) {{\n"
            new_body += f"{' ' * (inner_indent + 4)}TreeNode current = stack.Pop();\n\n"
            new_body += f"{' ' * (inner_indent + 4)}// Visit the node\n"
            new_body += f"{' ' * (inner_indent + 4)}Console.Write(current.Value + \" \"); // Or other visit operation\n\n"
            new_body += f"{' ' * (inner_indent + 4)}// Push right child first so that left is processed first\n"
            new_body += f"{' ' * (inner_indent + 4)}if (current.Right != null) {{\n"
            new_body += f"{' ' * (inner_indent + 8)}stack.Push(current.Right);\n"
            new_body += f"{' ' * (inner_indent + 4)}}}\n"
            new_body += f"{' ' * (inner_indent + 4)}if (current.Left != null) {{\n"
            new_body += f"{' ' * (inner_indent + 8)}stack.Push(current.Left);\n"
            new_body += f"{' ' * (inner_indent + 4)}}}\n"
            new_body += f"{' ' * inner_indent}}}\n"
    else:  # postorder
        new_body += f"{' ' * inner_indent}// Iterative Postorder Traversal (using two stacks)\n"
        if lang == "c":
            new_body += f"{' ' * inner_indent}if ({root_param} == NULL) {{\n"
            new_body += f"{' ' * (inner_indent + 4)}return;\n"
            new_body += f"{' ' * inner_indent}}}\n\n"
            new_body += f"{' ' * inner_indent}Stack* stack1 = createStack();\n"
            new_body += f"{' ' * inner_indent}Stack* stack2 = createStack();\n\n"
            new_body += f"{' ' * inner_indent}push(stack1, {root_param});\n\n"
            new_body += f"{' ' * inner_indent}// First store postorder traversal in stack2\n"
            new_body += f"{' ' * inner_indent}while (!isEmpty(stack1)) {{\n"
            new_body += f"{' ' * (inner_indent + 4)}TreeNode* current = pop(stack1);\n"
            new_body += f"{' ' * (inner_indent + 4)}push(stack2, current);\n\n"
            new_body += f"{' ' * (inner_indent + 4)}if (current->left != NULL) {{\n"
            new_body += f"{' ' * (inner_indent + 8)}push(stack1, current->left);\n"
            new_body += f"{' ' * (inner_indent + 4)}}}\n"
            new_body += f"{' ' * (inner_indent + 4)}if (current->right != NULL) {{\n"
            new_body += f"{' ' * (inner_indent + 8)}push(stack1, current->right);\n"
            new_body += f"{' ' * (inner_indent + 4)}}}\n"
            new_body += f"{' ' * inner_indent}}}\n\n"
            new_body += f"{' ' * inner_indent}// Now pop from stack2 to get postorder traversal\n"
            new_body += f"{' ' * inner_indent}while (!isEmpty(stack2)) {{\n"
            new_body += f"{' ' * (inner_indent + 4)}TreeNode* current = pop(stack2);\n"
            new_body += f"{' ' * (inner_indent + 4)}printf(\"%d \", current->value); // Or other visit operation\n"
            new_body += f"{' ' * inner_indent}}}\n\n"
            new_body += f"{' ' * inner_indent}freeStack(stack1);\n"
            new_body += f"{' ' * inner_indent}freeStack(stack2);\n"
        elif lang == "java":
            new_body += f"{' ' * inner_indent}if ({root_param} == null) {{\n"
            new_body += f"{' ' * (inner_indent + 4)}return;\n"
            new_body += f"{' ' * inner_indent}}}\n\n"
            new_body += f"{' ' * inner_indent}Stack<TreeNode> stack1 = new Stack<>();\n"
            new_body += f"{' ' * inner_indent}Stack<TreeNode> stack2 = new Stack<>();\n\n"
            new_body += f"{' ' * inner_indent}stack1.push({root_param});\n\n"
            new_body += f"{' ' * inner_indent}// First store postorder traversal in stack2\n"
            new_body += f"{' ' * inner_indent}while (!stack1.isEmpty()) {{\n"
            new_body += f"{' ' * (inner_indent + 4)}TreeNode current = stack1.pop();\n"
            new_body += f"{' ' * (inner_indent + 4)}stack2.push(current);\n\n"
            new_body += f"{' ' * (inner_indent + 4)}if (current.left != null) {{\n"
            new_body += f"{' ' * (inner_indent + 8)}stack1.push(current.left);\n"
            new_body += f"{' ' * (inner_indent + 4)}}}\n"
            new_body += f"{' ' * (inner_indent + 4)}if (current.right != null) {{\n"
            new_body += f"{' ' * (inner_indent + 8)}stack1.push(current.right);\n"
            new_body += f"{' ' * (inner_indent + 4)}}}\n"
            new_body += f"{' ' * inner_indent}}}\n\n"
            new_body += f"{' ' * inner_indent}// Now pop from stack2 to get postorder traversal\n"
            new_body += f"{' ' * inner_indent}while (!stack2.isEmpty()) {{\n"
            new_body += f"{' ' * (inner_indent + 4)}TreeNode current = stack2.pop();\n"
            new_body += f"{' ' * (inner_indent + 4)}System.out.print(current.value + \" \"); // Or other visit operation\n"
            new_body += f"{' ' * inner_indent}}}\n"
        else:  # C#
            new_body += f"{' ' * inner_indent}if ({root_param} == null) {{\n"
            new_body += f"{' ' * (inner_indent + 4)}return;\n"
            new_body += f"{' ' * inner_indent}}}\n\n"
            new_body += f"{' ' * inner_indent}Stack<TreeNode> stack1 = new Stack<TreeNode>();\n"
            new_body += f"{' ' * inner_indent}Stack<TreeNode> stack2 = new Stack<TreeNode>();\n\n"
            new_body += f"{' ' * inner_indent}stack1.Push({root_param});\n\n"
            new_body += f"{' ' * inner_indent}// First store postorder traversal in stack2\n"
            new_body += f"{' ' * inner_indent}while (stack1.Count > 0) {{\n"
            new_body += f"{' ' * (inner_indent + 4)}TreeNode current = stack1.Pop();\n"
            new_body += f"{' ' * (inner_indent + 4)}stack2.Push(current);\n\n"
            new_body += f"{' ' * (inner_indent + 4)}if (current.Left != null) {{\n"
            new_body += f"{' ' * (inner_indent + 8)}stack1.Push(current.Left);\n"
            new_body += f"{' ' * (inner_indent + 4)}}}\n"
            new_body += f"{' ' * (inner_indent + 4)}if (current.Right != null) {{\n"
            new_body += f"{' ' * (inner_indent + 8)}stack1.Push(current.Right);\n"
            new_body += f"{' ' * (inner_indent + 4)}}}\n"
            new_body += f"{' ' * inner_indent}}}\n\n"
            new_body += f"{' ' * inner_indent}// Now pop from stack2 to get postorder traversal\n"
            new_body += f"{' ' * inner_indent}while (stack2.Count > 0) {{\n"
            new_body += f"{' ' * (inner_indent + 4)}TreeNode current = stack2.Pop();\n"
            new_body += f"{' ' * (inner_indent + 4)}Console.Write(current.Value + \" \"); // Or other visit operation\n"
            new_body += f"{' ' * inner_indent}}}\n"

    new_body += f"{' ' * base_indent}}}"

    # 添加堆栈结构定义
    return stack_struct + "\n\n" + new_body


def convert_recursive_to_iterative_general(node, code, func_name, return_type, params, param_patterns, base_indent,
                                           inner_indent, lang):
    """
    将一般递归函数转换为迭代实现（使用栈模拟）
    """
    # 创建框架结构
    frame_fields = []
    for param in params:
        frame_fields.append({"name": param["name"], "type": param["type"]})

    # 添加返回地址变量
    frame_fields.append({"name": "return_addr", "type": "int"})
    frame_fields.append({"name": "result", "type": return_type})

    frame_struct = None
    if lang == "c":
        # 创建帧结构
        frame_struct_template = "typedef struct {\n%s\n} Frame;\n"
        fields = []
        for field in frame_fields:
            fields.append(f"    {field['type']} {field['name']};")
        frame_struct = frame_struct_template % "\n".join(fields)

        # 创建栈结构
        frame_struct += FRAME_STRUCTURE_TEMPLATES[lang]
    else:
        # 创建帧和栈结构
        fields_decl = []
        for field in frame_fields:
            fields_decl.append(f"public {field['type']} {field['name']};")

        param_decl = []
        fields_init = []
        for field in frame_fields:
            param_decl.append(f"{field['type']} {field['name']}")
            fields_init.append(f"this.{field['name']} = {field['name']};")

        if lang == "java":
            frame_struct = FRAME_STRUCTURE_TEMPLATES[lang] % ("\n    ".join(fields_decl),
                                                              ", ".join(param_decl),
                                                              "\n        ".join(fields_init))
        else:  # C#
            frame_struct = FRAME_STRUCTURE_TEMPLATES[lang] % ("\n    ".join(fields_decl),
                                                              ", ".join(param_decl),
                                                              "\n        ".join(fields_init))

    # 提取基本情况和递归步骤
    base_cases = extract_base_case(node, func_name)
    recursive_steps = extract_recursive_step(node, func_name)

    if not base_cases or not recursive_steps:
        return None

    # 分析递归调用中参数的变化模式
    recursive_call_args = {}
    for step, call in recursive_steps:
        # 获取调用参数
        args = []
        for child in call.children:
            if child.type == "argument_list":
                for arg in child.children:
                    if arg.type not in ["(", ")", ","]:
                        args.append(text(arg))

        if args:
            recursive_call_args[text(step)] = args

    new_body = "{\n"

    # 添加栈初始化和第一个帧
    if lang == "c":
        new_body += f"{' ' * inner_indent}// Create a stack to simulate recursion\n"
        new_body += f"{' ' * inner_indent}FrameStack* stack = createFrameStack();\n\n"

        new_body += f"{' ' * inner_indent}// Initialize first frame with arguments\n"
        new_body += f"{' ' * inner_indent}Frame frame;\n"
        for param in params:
            new_body += f"{' ' * inner_indent}frame.{param['name']} = {param['name']};\n"
        new_body += f"{' ' * inner_indent}frame.return_addr = 0;\n\n"

        new_body += f"{' ' * inner_indent}// Push first frame to stack\n"
        new_body += f"{' ' * inner_indent}pushFrame(stack, frame);\n\n"

        new_body += f"{' ' * inner_indent}{return_type} result;\n\n"

        new_body += f"{' ' * inner_indent}// Main simulation loop\n"
        new_body += f"{' ' * inner_indent}while (!isFrameStackEmpty(stack)) {{\n"
        new_body += f"{' ' * (inner_indent + 4)}// Get current frame\n"
        new_body += f"{' ' * (inner_indent + 4)}Frame currentFrame = popFrame(stack);\n\n"

        # 展开参数
        for param in params:
            new_body += f"{' ' * (inner_indent + 4)}{param['type']} {param['name']} = currentFrame.{param['name']};\n"
        new_body += f"{' ' * (inner_indent + 4)}int return_addr = currentFrame.return_addr;\n\n"

        new_body += f"{' ' * (inner_indent + 4)}// Execute based on return address\n"
        new_body += f"{' ' * (inner_indent + 4)}switch (return_addr) {{\n"
        new_body += f"{' ' * (inner_indent + 8)}case 0: // Entry point\n"

        # 基本情况检查
        for i, base_case in enumerate(base_cases):
            base_condition = text(base_case.children[1])
            base_body = text(base_case.children[2])

            new_body += f"{' ' * (inner_indent + 12)}// Base case {i + 1}\n"
            new_body += f"{' ' * (inner_indent + 12)}if ({base_condition}) {{\n"

            # 提取基本情况的返回值
            if "return" in base_body:
                # 简单提取 return 语句的值
                return_match = re.search(r'return\s+(.+?);', base_body)
                if return_match:
                    return_value = return_match.group(1)
                    new_body += f"{' ' * (inner_indent + 16)}result = {return_value};\n"
                    new_body += f"{' ' * (inner_indent + 16)}break;\n"

            new_body += f"{' ' * (inner_indent + 12)}}}\n\n"

        # 递归调用处理
        for i, (step, call) in enumerate(recursive_steps):
            step_text = text(step)
            if step_text in recursive_call_args:
                args = recursive_call_args[step_text]

                new_body += f"{' ' * (inner_indent + 12)}// Recursive call {i + 1}\n"
                new_body += f"{' ' * (inner_indent + 12)}// Prepare new frame for recursive call\n"
                new_body += f"{' ' * (inner_indent + 12)}Frame newFrame;\n"

                # 设置新帧的参数
                for j, arg in enumerate(args):
                    if j < len(params):
                        new_body += f"{' ' * (inner_indent + 12)}newFrame.{params[j]['name']} = {arg};\n"

                # 设置返回地址
                new_body += f"{' ' * (inner_indent + 12)}newFrame.return_addr = {i + 1};\n"

                # 保存当前帧（供递归调用返回后使用）
                new_body += f"{' ' * (inner_indent + 12)}// Save current frame for when recursive call returns\n"
                new_body += f"{' ' * (inner_indent + 12)}currentFrame.return_addr = {i + 1};\n"
                for param in params:
                    new_body += f"{' ' * (inner_indent + 12)}currentFrame.{param['name']} = {param['name']};\n"

                new_body += f"{' ' * (inner_indent + 12)}// Push frames to stack (current frame first to be popped later)\n"
                new_body += f"{' ' * (inner_indent + 12)}pushFrame(stack, currentFrame);\n"
                new_body += f"{' ' * (inner_indent + 12)}pushFrame(stack, newFrame);\n"
                new_body += f"{' ' * (inner_indent + 12)}break;\n\n"

        # 返回地址处理
        for i in range(len(recursive_steps)):
            new_body += f"{' ' * (inner_indent + 8)}case {i + 1}: // Return from recursive call {i + 1}\n"

            # 提取递归调用结果的处理
            # 这部分依赖于具体的递归函数逻辑，下面是一个通用处理
            new_body += f"{' ' * (inner_indent + 12)}// Process result from recursive call\n"

            # 尝试分析递归调用的结果如何被使用
            for step, call in recursive_steps:
                if step.parent.type == "return_statement":
                    # 递归调用直接返回
                    new_body += f"{' ' * (inner_indent + 12)}// Return result directly\n"
                    new_body += f"{' ' * (inner_indent + 12)}break;\n"
                elif step.parent.type == "binary_expression":
                    # 递归调用结果参与运算
                    op = None
                    for child in step.parent.children:
                        if child.type == "+" or child.type == "-" or child.type == "*" or child.type == "/":
                            op = text(child)
                            break

                    if op:
                        # 简化处理，假设另一个操作数是个简单值
                        operand = None
                        if step.parent.children[0] != step and text(step.parent.children[0]) != func_name:
                            operand = text(step.parent.children[0])
                        elif step.parent.children[2] != step and text(step.parent.children[2]) != func_name:
                            operand = text(step.parent.children[2])

                        if operand:
                            new_body += f"{' ' * (inner_indent + 12)}// Combine result with another value\n"
                            new_body += f"{' ' * (inner_indent + 12)}result = currentFrame.result {op} {operand};\n"
                            new_body += f"{' ' * (inner_indent + 12)}break;\n"

            new_body += f"{' ' * (inner_indent + 12)}break;\n\n"

        new_body += f"{' ' * (inner_indent + 4)}}}\n"
        new_body += f"{' ' * inner_indent}}}\n\n"

        new_body += f"{' ' * inner_indent}// Clean up and return final result\n"
        new_body += f"{' ' * inner_indent}freeFrameStack(stack);\n"
        new_body += f"{' ' * inner_indent}return result;\n"
    else:  # Java/C#
        if lang == "java":
            new_body += f"{' ' * inner_indent}// Create a stack to simulate recursion\n"
            new_body += f"{' ' * inner_indent}FrameStack stack = new FrameStack();\n\n"

            new_body += f"{' ' * inner_indent}// Initialize first frame with arguments\n"
            new_body += f"{' ' * inner_indent}Frame frame = new Frame(\n"

            # 初始化参数
            param_inits = []
            for param in params:
                param_inits.append(f"{' ' * (inner_indent + 4)}{param['name']}")
            param_inits.append(f"{' ' * (inner_indent + 4)}0, // return_addr")
            param_inits.append(f"{' ' * (inner_indent + 4)}null // result")

            new_body += ",\n".join(param_inits) + "\n"
            new_body += f"{' ' * inner_indent});\n\n"

            new_body += f"{' ' * inner_indent}// Push first frame to stack\n"
            new_body += f"{' ' * inner_indent}stack.push(frame);\n\n"

            new_body += f"{' ' * inner_indent}{return_type} result = null;\n\n"

            new_body += f"{' ' * inner_indent}// Main simulation loop\n"
            new_body += f"{' ' * inner_indent}while (!stack.isEmpty()) {{\n"
            new_body += f"{' ' * (inner_indent + 4)}// Get current frame\n"
            new_body += f"{' ' * (inner_indent + 4)}Frame currentFrame = stack.pop();\n\n"

            # 展开参数
            for param in params:
                new_body += f"{' ' * (inner_indent + 4)}{param['type']} {param['name']} = currentFrame.{param['name']};\n"
            new_body += f"{' ' * (inner_indent + 4)}int returnAddr = currentFrame.returnAddr;\n\n"

            new_body += f"{' ' * (inner_indent + 4)}// Execute based on return address\n"
            new_body += f"{' ' * (inner_indent + 4)}switch (returnAddr) {{\n"
            new_body += f"{' ' * (inner_indent + 8)}case 0: // Entry point\n"
        else:  # C#
            new_body += f"{' ' * inner_indent}// Create a stack to simulate recursion\n"
            new_body += f"{' ' * inner_indent}FrameStack stack = new FrameStack();\n\n"

            new_body += f"{' ' * inner_indent}// Initialize first frame with arguments\n"
            new_body += f"{' ' * inner_indent}Frame frame = new Frame(\n"

            # 初始化参数
            param_inits = []
            for param in params:
                param_inits.append(f"{' ' * (inner_indent + 4)}{param['name']}")
            param_inits.append(f"{' ' * (inner_indent + 4)}0, // returnAddr")
            param_inits.append(f"{' ' * (inner_indent + 4)}default({return_type}) // result")

            new_body += ",\n".join(param_inits) + "\n"
            new_body += f"{' ' * inner_indent});\n\n"

            new_body += f"{' ' * inner_indent}// Push first frame to stack\n"
            new_body += f"{' ' * inner_indent}stack.Push(frame);\n\n"

            new_body += f"{' ' * inner_indent}{return_type} result = default({return_type});\n\n"

            new_body += f"{' ' * inner_indent}// Main simulation loop\n"
            new_body += f"{' ' * inner_indent}while (!stack.IsEmpty()) {{\n"
            new_body += f"{' ' * (inner_indent + 4)}// Get current frame\n"
            new_body += f"{' ' * (inner_indent + 4)}Frame currentFrame = stack.Pop();\n\n"

            # 展开参数
            for param in params:
                new_body += f"{' ' * (inner_indent + 4)}{param['type']} {param['name']} = currentFrame.{param['name']};\n"
            new_body += f"{' ' * (inner_indent + 4)}int returnAddr = currentFrame.returnAddr;\n\n"

            new_body += f"{' ' * (inner_indent + 4)}// Execute based on return address\n"
            new_body += f"{' ' * (inner_indent + 4)}switch (returnAddr) {{\n"
            new_body += f"{' ' * (inner_indent + 8)}case 0: // Entry point\n"

        # 基本情况检查 (Java / C#)
        for i, base_case in enumerate(base_cases):
            base_condition = text(base_case.children[1])
            base_body = text(base_case.children[2])

            new_body += f"{' ' * (inner_indent + 12)}// Base case {i + 1}\n"
            new_body += f"{' ' * (inner_indent + 12)}if ({base_condition}) {{\n"

            # 提取基本情况的返回值
            if "return" in base_body:
                # 简单提取 return 语句的值
                return_match = re.search(r'return\s+(.+?);', base_body)
                if return_match:
                    return_value = return_match.group(1)
                    new_body += f"{' ' * (inner_indent + 16)}result = {return_value};\n"
                    new_body += f"{' ' * (inner_indent + 16)}break;\n"

            new_body += f"{' ' * (inner_indent + 12)}}}\n\n"

        # 递归调用处理 (Java / C#)
        for i, (step, call) in enumerate(recursive_steps):
            step_text = text(step)
            if step_text in recursive_call_args:
                args = recursive_call_args[step_text]

                new_body += f"{' ' * (inner_indent + 12)}// Recursive call {i + 1}\n"
                new_body += f"{' ' * (inner_indent + 12)}// Prepare new frame for recursive call\n"

                # 准备递归调用参数
                param_inits = []
                for j, arg in enumerate(args):
                    if j < len(params):
                        param_inits.append(f"{' ' * (inner_indent + 16)}{arg}")

                # 设置返回地址和空结果
                param_inits.append(f"{' ' * (inner_indent + 16)}{i + 1}, // returnAddr")
                if lang == "java":
                    param_inits.append(f"{' ' * (inner_indent + 16)}null // result")
                else:  # C#
                    param_inits.append(f"{' ' * (inner_indent + 16)}default({return_type}) // result")

                new_body += f"{' ' * (inner_indent + 12)}Frame newFrame = new Frame(\n"
                new_body += ",\n".join(param_inits) + "\n"
                new_body += f"{' ' * (inner_indent + 12)});\n"

                # 保存当前帧（供递归调用返回后使用）
                new_body += f"{' ' * (inner_indent + 12)}// Save current frame for when recursive call returns\n"
                new_body += f"{' ' * (inner_indent + 12)}currentFrame.returnAddr = {i + 1};\n"

                # 参数可能已修改，需要更新
                for param in params:
                    new_body += f"{' ' * (inner_indent + 12)}currentFrame.{param['name']} = {param['name']};\n"

                new_body += f"{' ' * (inner_indent + 12)}// Push frames to stack (current frame first to be popped later)\n"
                if lang == "java":
                    new_body += f"{' ' * (inner_indent + 12)}stack.push(currentFrame);\n"
                    new_body += f"{' ' * (inner_indent + 12)}stack.push(newFrame);\n"
                else:  # C#
                    new_body += f"{' ' * (inner_indent + 12)}stack.Push(currentFrame);\n"
                    new_body += f"{' ' * (inner_indent + 12)}stack.Push(newFrame);\n"
                new_body += f"{' ' * (inner_indent + 12)}break;\n\n"

        # 返回地址处理 (Java / C#)
        for i in range(len(recursive_steps)):
            new_body += f"{' ' * (inner_indent + 8)}case {i + 1}: // Return from recursive call {i + 1}\n"

            # 提取递归调用结果的处理
            # 这部分依赖于具体的递归函数逻辑，下面是一个通用处理
            new_body += f"{' ' * (inner_indent + 12)}// Process result from recursive call\n"

            # 尝试分析递归调用的结果如何被使用
            for step, call in recursive_steps:
                if step.parent.type == "return_statement":
                    # 递归调用直接返回
                    new_body += f"{' ' * (inner_indent + 12)}// Return result directly\n"
                    new_body += f"{' ' * (inner_indent + 12)}break;\n"
                elif step.parent.type == "binary_expression":
                    # 递归调用结果参与运算
                    op = None
                    for child in step.parent.children:
                        if child.type == "+" or child.type == "-" or child.type == "*" or child.type == "/":
                            op = text(child)
                            break

                    if op:
                        # 简化处理，假设另一个操作数是个简单值
                        operand = None
                        if step.parent.children[0] != step and text(step.parent.children[0]) != func_name:
                            operand = text(step.parent.children[0])
                        elif step.parent.children[2] != step and text(step.parent.children[2]) != func_name:
                            operand = text(step.parent.children[2])

                        if operand:
                            new_body += f"{' ' * (inner_indent + 12)}// Combine result with another value\n"
                            new_body += f"{' ' * (inner_indent + 12)}result = currentFrame.result {op} {operand};\n"
                            new_body += f"{' ' * (inner_indent + 12)}break;\n"

            new_body += f"{' ' * (inner_indent + 12)}break;\n\n"

        new_body += f"{' ' * (inner_indent + 4)}}}\n"
        new_body += f"{' ' * inner_indent}}}\n\n"

        new_body += f"{' ' * inner_indent}// Return final result\n"
        new_body += f"{' ' * inner_indent}return result;\n"

    new_body += f"{' ' * base_indent}}}"

    # 添加帧和栈结构定义
    return frame_struct + "\n\n" + new_body


def convert_recursive_quicksort_to_iterative(node, code, func_name, return_type, params, base_indent, inner_indent,
                                             lang):
    """
    将递归快速排序转换为迭代实现
    """
    array_param = params[0]["name"]
    left_param = None
    right_param = None

    # 尝试识别参数名称
    for param in params[1:]:
        name = param["name"]
        if name in ["left", "low", "start", "l"]:
            left_param = name
        elif name in ["right", "high", "end", "r"]:
            right_param = name

    # 使用默认名称
    if not left_param:
        left_param = params[1]["name"] if len(params) > 1 else "left"
    if not right_param:
        right_param = params[2]["name"] if len(params) > 2 else "right"

    # 创建堆栈结构
    if lang == "c":
        stack_type = "int"
        stack_struct = """
typedef struct {
    int low;
    int high;
} Range;

typedef struct RangeNode {
    Range range;
    struct RangeNode* next;
} RangeNode;

typedef struct {
    RangeNode* top;
} RangeStack;

RangeStack* createRangeStack() {
    RangeStack* stack = (RangeStack*)malloc(sizeof(RangeStack));
    stack->top = NULL;
    return stack;
}

int isRangeStackEmpty(RangeStack* stack) {
    return stack->top == NULL;
}

void pushRange(RangeStack* stack, int low, int high) {
    RangeNode* node = (RangeNode*)malloc(sizeof(RangeNode));
    node->range.low = low;
    node->range.high = high;
    node->next = stack->top;
    stack->top = node;
}

Range popRange(RangeStack* stack) {
    if (isRangeStackEmpty(stack)) {
        fprintf(stderr, "Error: RangeStack underflow\\n");
        exit(1);
    }
    RangeNode* temp = stack->top;
    stack->top = stack->top->next;
    Range result = temp->range;
    free(temp);
    return result;
}

void freeRangeStack(RangeStack* stack) {
    RangeNode* current = stack->top;
    while (current != NULL) {
        RangeNode* temp = current;
        current = current->next;
        free(temp);
    }
    free(stack);
}
"""
    elif lang == "java":
        stack_struct = """
private static class Range {
    int low;
    int high;

    public Range(int low, int high) {
        this.low = low;
        this.high = high;
    }
}

private static class RangeStack {
    private static class Node {
        Range range;
        Node next;

        Node(Range range) {
            this.range = range;
            this.next = null;
        }
    }

    private Node top;

    public RangeStack() {
        this.top = null;
    }

    public boolean isEmpty() {
        return top == null;
    }

    public void push(int low, int high) {
        Node node = new Node(new Range(low, high));
        node.next = top;
        top = node;
    }

    public Range pop() {
        if (isEmpty()) {
            throw new RuntimeException("RangeStack underflow");
        }
        Range range = top.range;
        top = top.next;
        return range;
    }
}
"""
    else:  # C#
        stack_struct = """
private class Range {
    public int Low { get; set; }
    public int High { get; set; }

    public Range(int low, int high) {
        this.Low = low;
        this.High = high;
    }
}

private class RangeStack {
    private class Node {
        public Range Range { get; set; }
        public Node Next { get; set; }

        public Node(Range range) {
            this.Range = range;
            this.Next = null;
        }
    }

    private Node top;

    public RangeStack() {
        this.top = null;
    }

    public bool IsEmpty() {
        return top == null;
    }

    public void Push(int low, int high) {
        Node node = new Node(new Range(low, high));
        node.Next = top;
        top = node;
    }

    public Range Pop() {
        if (IsEmpty()) {
            throw new InvalidOperationException("RangeStack underflow");
        }
        Range range = top.Range;
        top = top.Next;
        return range;
    }
}
"""

    # 创建迭代版快速排序实现
    new_body = "{\n"

    if lang == "c":
        new_body += f"{' ' * inner_indent}// Create a stack for storing subarray ranges\n"
        new_body += f"{' ' * inner_indent}RangeStack* stack = createRangeStack();\n\n"

        # Partition helper function
        new_body += f"{' ' * inner_indent}// Helper function for partitioning\n"
        new_body += f"{' ' * inner_indent}int partition({array_param}, int {left_param}, int {right_param}) {{\n"
        new_body += f"{' ' * (inner_indent + 4)}int pivot = {array_param}[{right_param}];\n"
        new_body += f"{' ' * (inner_indent + 4)}int i = ({left_param} - 1);\n\n"
        new_body += f"{' ' * (inner_indent + 4)}for (int j = {left_param}; j <= {right_param} - 1; j++) {{\n"
        new_body += f"{' ' * (inner_indent + 8)}if ({array_param}[j] < pivot) {{\n"
        new_body += f"{' ' * (inner_indent + 12)}i++;\n"
        new_body += f"{' ' * (inner_indent + 12)}int temp = {array_param}[i];\n"
        new_body += f"{' ' * (inner_indent + 12)}{array_param}[i] = {array_param}[j];\n"
        new_body += f"{' ' * (inner_indent + 12)}{array_param}[j] = temp;\n"
        new_body += f"{' ' * (inner_indent + 8)}}}\n"
        new_body += f"{' ' * (inner_indent + 4)}}}\n\n"
        new_body += f"{' ' * (inner_indent + 4)}int temp = {array_param}[i + 1];\n"
        new_body += f"{' ' * (inner_indent + 4)}{array_param}[i + 1] = {array_param}[{right_param}];\n"
        new_body += f"{' ' * (inner_indent + 4)}{array_param}[{right_param}] = temp;\n"
        new_body += f"{' ' * (inner_indent + 4)}return (i + 1);\n"
        new_body += f"{' ' * inner_indent}}}\n\n"

        # Main quicksort loop
        new_body += f"{' ' * inner_indent}// Push initial range to stack\n"
        new_body += f"{' ' * inner_indent}pushRange(stack, {left_param}, {right_param});\n\n"

        new_body += f"{' ' * inner_indent}// Process stack until empty\n"
        new_body += f"{' ' * inner_indent}while (!isRangeStackEmpty(stack)) {{\n"
        new_body += f"{' ' * (inner_indent + 4)}// Pop range from stack\n"
        new_body += f"{' ' * (inner_indent + 4)}Range range = popRange(stack);\n"
        new_body += f"{' ' * (inner_indent + 4)}int low = range.low;\n"
        new_body += f"{' ' * (inner_indent + 4)}int high = range.high;\n\n"

        new_body += f"{' ' * (inner_indent + 4)}// Partition and get pivot index\n"
        new_body += f"{' ' * (inner_indent + 4)}if (low < high) {{\n"
        new_body += f"{' ' * (inner_indent + 8)}int pi = partition({array_param}, low, high);\n\n"

        new_body += f"{' ' * (inner_indent + 8)}// Push subarrays to stack\n"
        new_body += f"{' ' * (inner_indent + 8)}pushRange(stack, pi + 1, high);\n"
        new_body += f"{' ' * (inner_indent + 8)}pushRange(stack, low, pi - 1);\n"
        new_body += f"{' ' * (inner_indent + 4)}}}\n"
        new_body += f"{' ' * inner_indent}}}\n\n"

        new_body += f"{' ' * inner_indent}// Free stack\n"
        new_body += f"{' ' * inner_indent}freeRangeStack(stack);\n"

    elif lang == "java":
        new_body += f"{' ' * inner_indent}// Create a stack for storing subarray ranges\n"
        new_body += f"{' ' * inner_indent}RangeStack stack = new RangeStack();\n\n"

        # Partition helper function
        new_body += f"{' ' * inner_indent}// Helper function for partitioning\n"
        new_body += f"{' ' * inner_indent}class Partition {{\n"
        new_body += f"{' ' * (inner_indent + 4)}int apply(int[] arr, int low, int high) {{\n"
        new_body += f"{' ' * (inner_indent + 8)}int pivot = arr[high];\n"
        new_body += f"{' ' * (inner_indent + 8)}int i = (low - 1);\n\n"
        new_body += f"{' ' * (inner_indent + 8)}for (int j = low; j <= high - 1; j++) {{\n"
        new_body += f"{' ' * (inner_indent + 12)}if (arr[j] < pivot) {{\n"
        new_body += f"{' ' * (inner_indent + 16)}i++;\n"
        new_body += f"{' ' * (inner_indent + 16)}int temp = arr[i];\n"
        new_body += f"{' ' * (inner_indent + 16)}arr[i] = arr[j];\n"
        new_body += f"{' ' * (inner_indent + 16)}arr[j] = temp;\n"
        new_body += f"{' ' * (inner_indent + 12)}}}\n"
        new_body += f"{' ' * (inner_indent + 8)}}}\n\n"
        new_body += f"{' ' * (inner_indent + 8)}int temp = arr[i + 1];\n"
        new_body += f"{' ' * (inner_indent + 8)}arr[i + 1] = arr[high];\n"
        new_body += f"{' ' * (inner_indent + 8)}arr[high] = temp;\n"
        new_body += f"{' ' * (inner_indent + 8)}return (i + 1);\n"
        new_body += f"{' ' * (inner_indent + 4)}}}\n"
        new_body += f"{' ' * inner_indent}}}\n\n"
        new_body += f"{' ' * inner_indent}Partition partitioner = new Partition();\n\n"

        # Main quicksort loop
        new_body += f"{' ' * inner_indent}// Push initial range to stack\n"
        new_body += f"{' ' * inner_indent}stack.push({left_param}, {right_param});\n\n"

        new_body += f"{' ' * inner_indent}// Process stack until empty\n"
        new_body += f"{' ' * inner_indent}while (!stack.isEmpty()) {{\n"
        new_body += f"{' ' * (inner_indent + 4)}// Pop range from stack\n"
        new_body += f"{' ' * (inner_indent + 4)}Range range = stack.pop();\n"
        new_body += f"{' ' * (inner_indent + 4)}int low = range.low;\n"
        new_body += f"{' ' * (inner_indent + 4)}int high = range.high;\n\n"

        new_body += f"{' ' * (inner_indent + 4)}// Partition and get pivot index\n"
        new_body += f"{' ' * (inner_indent + 4)}if (low < high) {{\n"
        new_body += f"{' ' * (inner_indent + 8)}int pi = partitioner.apply({array_param}, low, high);\n\n"

        new_body += f"{' ' * (inner_indent + 8)}// Push subarrays to stack\n"
        new_body += f"{' ' * (inner_indent + 8)}stack.push(pi + 1, high);\n"
        new_body += f"{' ' * (inner_indent + 8)}stack.push(low, pi - 1);\n"
        new_body += f"{' ' * (inner_indent + 4)}}}\n"
        new_body += f"{' ' * inner_indent}}}\n"

    else:  # C#
        new_body += f"{' ' * inner_indent}// Create a stack for storing subarray ranges\n"
        new_body += f"{' ' * inner_indent}RangeStack stack = new RangeStack();\n\n"

        # Partition helper function
        new_body += f"{' ' * inner_indent}// Helper function for partitioning\n"
        new_body += f"{' ' * inner_indent}int Partition(int[] arr, int low, int high) {{\n"
        new_body += f"{' ' * (inner_indent + 4)}int pivot = arr[high];\n"
        new_body += f"{' ' * (inner_indent + 4)}int i = (low - 1);\n\n"
        new_body += f"{' ' * (inner_indent + 4)}for (int j = low; j <= high - 1; j++) {{\n"
        new_body += f"{' ' * (inner_indent + 8)}if (arr[j] < pivot) {{\n"
        new_body += f"{' ' * (inner_indent + 12)}i++;\n"
        new_body += f"{' ' * (inner_indent + 12)}int temp = arr[i];\n"
        new_body += f"{' ' * (inner_indent + 12)}arr[i] = arr[j];\n"
        new_body += f"{' ' * (inner_indent + 12)}arr[j] = temp;\n"
        new_body += f"{' ' * (inner_indent + 8)}}}\n"
        new_body += f"{' ' * (inner_indent + 4)}}}\n\n"
        new_body += f"{' ' * (inner_indent + 4)}int temp = arr[i + 1];\n"
        new_body += f"{' ' * (inner_indent + 4)}arr[i + 1] = arr[high];\n"
        new_body += f"{' ' * (inner_indent + 4)}arr[high] = temp;\n"
        new_body += f"{' ' * (inner_indent + 4)}return (i + 1);\n"
        new_body += f"{' ' * inner_indent}}}\n\n"

        # Main quicksort loop
        new_body += f"{' ' * inner_indent}// Push initial range to stack\n"
        new_body += f"{' ' * inner_indent}stack.Push({left_param}, {right_param});\n\n"

        new_body += f"{' ' * inner_indent}// Process stack until empty\n"
        new_body += f"{' ' * inner_indent}while (!stack.IsEmpty()) {{\n"
        new_body += f"{' ' * (inner_indent + 4)}// Pop range from stack\n"
        new_body += f"{' ' * (inner_indent + 4)}Range range = stack.Pop();\n"
        new_body += f"{' ' * (inner_indent + 4)}int low = range.Low;\n"
        new_body += f"{' ' * (inner_indent + 4)}int high = range.High;\n\n"

        new_body += f"{' ' * (inner_indent + 4)}// Partition and get pivot index\n"
        new_body += f"{' ' * (inner_indent + 4)}if (low < high) {{\n"
        new_body += f"{' ' * (inner_indent + 8)}int pi = Partition({array_param}, low, high);\n\n"

        new_body += f"{' ' * (inner_indent + 8)}// Push subarrays to stack\n"
        new_body += f"{' ' * (inner_indent + 8)}stack.Push(pi + 1, high);\n"
        new_body += f"{' ' * (inner_indent + 8)}stack.Push(low, pi - 1);\n"
        new_body += f"{' ' * (inner_indent + 4)}}}\n"
        new_body += f"{' ' * inner_indent}}}\n"

    new_body += f"{' ' * base_indent}}}"

    # 添加堆栈结构定义
    return stack_struct + "\n\n" + new_body


def convert_recursive_merge_sort_to_iterative(node, code, func_name, return_type, params, base_indent, inner_indent,
                                              lang):
    """
    将递归归并排序转换为迭代实现
    """
    array_param = params[0]["name"]

    # 确定其他参数名
    left_param = None
    right_param = None

    for param in params[1:]:
        name = param["name"]
        if name in ["left", "low", "start", "l"]:
            left_param = name
        elif name in ["right", "high", "end", "r"]:
            right_param = name

    # 使用默认名称
    if not left_param:
        left_param = params[1]["name"] if len(params) > 1 else "left"
    if not right_param:
        right_param = params[2]["name"] if len(params) > 2 else "right"

    new_body = "{\n"

    if lang == "c":
        new_body += f"{' ' * inner_indent}// Base case\n"
        new_body += f"{' ' * inner_indent}if ({left_param} >= {right_param}) {{\n"
        new_body += f"{' ' * (inner_indent + 4)}return;\n"
        new_body += f"{' ' * inner_indent}}}\n\n"

        new_body += f"{' ' * inner_indent}// Iterative Merge Sort using bottom-up approach\n"
        new_body += f"{' ' * inner_indent}// First get the array size\n"
        new_body += f"{' ' * inner_indent}int n = {right_param} - {left_param} + 1;\n\n"

        new_body += f"{' ' * inner_indent}// Allocate a temporary array for merging\n"
        new_body += f"{' ' * inner_indent}int* temp = (int*)malloc(n * sizeof(int));\n"
        new_body += f"{' ' * inner_indent}if (temp == NULL) {{\n"
        new_body += f"{' ' * (inner_indent + 4)}fprintf(stderr, \"Memory allocation failed\\n\");\n"
        new_body += f"{' ' * (inner_indent + 4)}return;\n"
        new_body += f"{' ' * inner_indent}}}\n\n"

        # 合并函数
        new_body += f"{' ' * inner_indent}// Helper function to merge two subarrays\n"
        new_body += f"{' ' * inner_indent}void merge(int arr[], int l, int m, int r) {{\n"
        new_body += f"{' ' * (inner_indent + 4)}int i, j, k;\n"
        new_body += f"{' ' * (inner_indent + 4)}int n1 = m - l + 1;\n"
        new_body += f"{' ' * (inner_indent + 4)}int n2 = r - m;\n\n"

        new_body += f"{' ' * (inner_indent + 4)}// Copy data to temp arrays\n"
        new_body += f"{' ' * (inner_indent + 4)}for (i = 0; i < n1; i++)\n"
        new_body += f"{' ' * (inner_indent + 8)}temp[i] = arr[l + i];\n"
        new_body += f"{' ' * (inner_indent + 4)}for (j = 0; j < n2; j++)\n"
        new_body += f"{' ' * (inner_indent + 8)}temp[n1 + j] = arr[m + 1 + j];\n\n"

        new_body += f"{' ' * (inner_indent + 4)}// Merge the temp arrays back into arr[l..r]\n"
        new_body += f"{' ' * (inner_indent + 4)}i = 0;\n"
        new_body += f"{' ' * (inner_indent + 4)}j = n1;\n"
        new_body += f"{' ' * (inner_indent + 4)}k = l;\n"
        new_body += f"{' ' * (inner_indent + 4)}while (i < n1 && j < n1 + n2) {{\n"
        new_body += f"{' ' * (inner_indent + 8)}if (temp[i] <= temp[j]) {{\n"
        new_body += f"{' ' * (inner_indent + 12)}arr[k++] = temp[i++];\n"
        new_body += f"{' ' * (inner_indent + 8)}}} else {{\n"
        new_body += f"{' ' * (inner_indent + 12)}arr[k++] = temp[j++];\n"
        new_body += f"{' ' * (inner_indent + 8)}}}\n"
        new_body += f"{' ' * (inner_indent + 4)}}}\n\n"

        new_body += f"{' ' * (inner_indent + 4)}// Copy the remaining elements\n"
        new_body += f"{' ' * (inner_indent + 4)}while (i < n1) {{\n"
        new_body += f"{' ' * (inner_indent + 8)}arr[k++] = temp[i++];\n"
        new_body += f"{' ' * (inner_indent + 4)}}}\n"
        new_body += f"{' ' * (inner_indent + 4)}while (j < n1 + n2) {{\n"
        new_body += f"{' ' * (inner_indent + 8)}arr[k++] = temp[j++];\n"
        new_body += f"{' ' * (inner_indent + 4)}}}\n"
        new_body += f"{' ' * inner_indent}}}\n\n"

        # 主要迭代逻辑
        new_body += f"{' ' * inner_indent}// Perform bottom-up merge sort\n"
        new_body += f"{' ' * inner_indent}for (int width = 1; width < n; width = 2 * width) {{\n"
        new_body += f"{' ' * (inner_indent + 4)}for (int i = {left_param}; i <= {right_param}; i = i + 2 * width) {{\n"
        new_body += f"{' ' * (inner_indent + 8)}int left = i;\n"
        new_body += f"{' ' * (inner_indent + 8)}int mid = (i + width - 1 < {right_param}) ? i + width - 1 : {right_param};\n"
        new_body += f"{' ' * (inner_indent + 8)}int right = (i + 2 * width - 1 < {right_param}) ? i + 2 * width - 1 : {right_param};\n"
        new_body += f"{' ' * (inner_indent + 8)}if (mid < right) {{\n"
        new_body += f"{' ' * (inner_indent + 12)}merge({array_param}, left, mid, right);\n"
        new_body += f"{' ' * (inner_indent + 8)}}}\n"
        new_body += f"{' ' * (inner_indent + 4)}}}\n"
        new_body += f"{' ' * inner_indent}}}\n\n"

        new_body += f"{' ' * inner_indent}// Free the temporary array\n"
        new_body += f"{' ' * inner_indent}free(temp);\n"

    elif lang == "java":
        new_body += f"{' ' * inner_indent}// Base case\n"
        new_body += f"{' ' * inner_indent}if ({left_param} >= {right_param}) {{\n"
        new_body += f"{' ' * (inner_indent + 4)}return;\n"
        new_body += f"{' ' * inner_indent}}}\n\n"

        new_body += f"{' ' * inner_indent}// Iterative Merge Sort using bottom-up approach\n"
        new_body += f"{' ' * inner_indent}// First get the array size\n"
        new_body += f"{' ' * inner_indent}int n = {right_param} - {left_param} + 1;\n\n"

        new_body += f"{' ' * inner_indent}// Allocate a temporary array for merging\n"
        new_body += f"{' ' * inner_indent}int[] temp = new int[n];\n\n"

        # 合并函数
        new_body += f"{' ' * inner_indent}// Helper function to merge two subarrays\n"
        new_body += f"{' ' * inner_indent}class Merger {{\n"
        new_body += f"{' ' * (inner_indent + 4)}void merge(int[] arr, int l, int m, int r, int[] temp) {{\n"
        new_body += f"{' ' * (inner_indent + 8)}int i, j, k;\n"
        new_body += f"{' ' * (inner_indent + 8)}int n1 = m - l + 1;\n"
        new_body += f"{' ' * (inner_indent + 8)}int n2 = r - m;\n\n"

        new_body += f"{' ' * (inner_indent + 8)}// Copy data to temp arrays\n"
        new_body += f"{' ' * (inner_indent + 8)}for (i = 0; i < n1; i++)\n"
        new_body += f"{' ' * (inner_indent + 12)}temp[i] = arr[l + i];\n"
        new_body += f"{' ' * (inner_indent + 8)}for (j = 0; j < n2; j++)\n"
        new_body += f"{' ' * (inner_indent + 12)}temp[n1 + j] = arr[m + 1 + j];\n\n"

        new_body += f"{' ' * (inner_indent + 8)}// Merge the temp arrays back into arr[l..r]\n"
        new_body += f"{' ' * (inner_indent + 8)}i = 0;\n"
        new_body += f"{' ' * (inner_indent + 8)}j = n1;\n"
        new_body += f"{' ' * (inner_indent + 8)}k = l;\n"
        new_body += f"{' ' * (inner_indent + 8)}while (i < n1 && j < n1 + n2) {{\n"
        new_body += f"{' ' * (inner_indent + 12)}if (temp[i] <= temp[j]) {{\n"
        new_body += f"{' ' * (inner_indent + 16)}arr[k++] = temp[i++];\n"
        new_body += f"{' ' * (inner_indent + 12)}}} else {{\n"
        new_body += f"{' ' * (inner_indent + 16)}arr[k++] = temp[j++];\n"
        new_body += f"{' ' * (inner_indent + 12)}}}\n"
        new_body += f"{' ' * (inner_indent + 8)}}}\n\n"

        new_body += f"{' ' * (inner_indent + 8)}// Copy the remaining elements\n"
        new_body += f"{' ' * (inner_indent + 8)}while (i < n1) {{\n"
        new_body += f"{' ' * (inner_indent + 12)}arr[k++] = temp[i++];\n"
        new_body += f"{' ' * (inner_indent + 8)}}}\n"
        new_body += f"{' ' * (inner_indent + 8)}while (j < n1 + n2) {{\n"
        new_body += f"{' ' * (inner_indent + 12)}arr[k++] = temp[j++];\n"
        new_body += f"{' ' * (inner_indent + 8)}}}\n"
        new_body += f"{' ' * (inner_indent + 4)}}}\n"
        new_body += f"{' ' * inner_indent}}}\n\n"

        new_body += f"{' ' * inner_indent}Merger merger = new Merger();\n\n"

        # 主要迭代逻辑
        new_body += f"{' ' * inner_indent}// Perform bottom-up merge sort\n"
        new_body += f"{' ' * inner_indent}for (int width = 1; width < n; width = 2 * width) {{\n"
        new_body += f"{' ' * (inner_indent + 4)}for (int i = {left_param}; i <= {right_param}; i = i + 2 * width) {{\n"
        new_body += f"{' ' * (inner_indent + 8)}int left = i;\n"
        new_body += f"{' ' * (inner_indent + 8)}int mid = Math.min(i + width - 1, {right_param});\n"
        new_body += f"{' ' * (inner_indent + 8)}int right = Math.min(i + 2 * width - 1, {right_param});\n"
        new_body += f"{' ' * (inner_indent + 8)}if (mid < right) {{\n"
        new_body += f"{' ' * (inner_indent + 12)}merger.merge({array_param}, left, mid, right, temp);\n"
        new_body += f"{' ' * (inner_indent + 8)}}}\n"
        new_body += f"{' ' * (inner_indent + 4)}}}\n"
        new_body += f"{' ' * inner_indent}}}\n"

    else:  # C#
        new_body += f"{' ' * inner_indent}// Base case\n"
        new_body += f"{' ' * inner_indent}if ({left_param} >= {right_param}) {{\n"
        new_body += f"{' ' * (inner_indent + 4)}return;\n"
        new_body += f"{' ' * inner_indent}}}\n\n"

        new_body += f"{' ' * inner_indent}// Iterative Merge Sort using bottom-up approach\n"
        new_body += f"{' ' * inner_indent}// First get the array size\n"
        new_body += f"{' ' * inner_indent}int n = {right_param} - {left_param} + 1;\n\n"

        new_body += f"{' ' * inner_indent}// Allocate a temporary array for merging\n"
        new_body += f"{' ' * inner_indent}int[] temp = new int[n];\n\n"

        # 合并函数
        new_body += f"{' ' * inner_indent}// Helper function to merge two subarrays\n"
        new_body += f"{' ' * inner_indent}void Merge(int[] arr, int l, int m, int r, int[] temp) {{\n"
        new_body += f"{' ' * (inner_indent + 4)}int i, j, k;\n"
        new_body += f"{' ' * (inner_indent + 4)}int n1 = m - l + 1;\n"
        new_body += f"{' ' * (inner_indent + 4)}int n2 = r - m;\n\n"

        new_body += f"{' ' * (inner_indent + 4)}// Copy data to temp arrays\n"
        new_body += f"{' ' * (inner_indent + 4)}for (i = 0; i < n1; i++)\n"
        new_body += f"{' ' * (inner_indent + 8)}temp[i] = arr[l + i];\n"
        new_body += f"{' ' * (inner_indent + 4)}for (j = 0; j < n2; j++)\n"
        new_body += f"{' ' * (inner_indent + 8)}temp[n1 + j] = arr[m + 1 + j];\n\n"

        new_body += f"{' ' * (inner_indent + 4)}// Merge the temp arrays back into arr[l..r]\n"
        new_body += f"{' ' * (inner_indent + 4)}i = 0;\n"
        new_body += f"{' ' * (inner_indent + 4)}j = n1;\n"
        new_body += f"{' ' * (inner_indent + 4)}k = l;\n"
        new_body += f"{' ' * (inner_indent + 4)}while (i < n1 && j < n1 + n2) {{\n"
        new_body += f"{' ' * (inner_indent + 8)}if (temp[i] <= temp[j]) {{\n"
        new_body += f"{' ' * (inner_indent + 12)}arr[k++] = temp[i++];\n"
        new_body += f"{' ' * (inner_indent + 8)}}} else {{\n"
        new_body += f"{' ' * (inner_indent + 12)}arr[k++] = temp[j++];\n"
        new_body += f"{' ' * (inner_indent + 8)}}}\n"
        new_body += f"{' ' * (inner_indent + 4)}}}\n\n"

        new_body += f"{' ' * (inner_indent + 4)}// Copy the remaining elements\n"
        new_body += f"{' ' * (inner_indent + 4)}while (i < n1) {{\n"
        new_body += f"{' ' * (inner_indent + 8)}arr[k++] = temp[i++];\n"
        new_body += f"{' ' * (inner_indent + 4)}}}\n"
        new_body += f"{' ' * (inner_indent + 4)}while (j < n1 + n2) {{\n"
        new_body += f"{' ' * (inner_indent + 8)}arr[k++] = temp[j++];\n"
        new_body += f"{' ' * (inner_indent + 4)}}}\n"
        new_body += f"{' ' * inner_indent}}}\n\n"

        # 主要迭代逻辑
        new_body += f"{' ' * inner_indent}// Perform bottom-up merge sort\n"
        new_body += f"{' ' * inner_indent}for (int width = 1; width < n; width = 2 * width) {{\n"
        new_body += f"{' ' * (inner_indent + 4)}for (int i = {left_param}; i <= {right_param}; i = i + 2 * width) {{\n"
        new_body += f"{' ' * (inner_indent + 8)}int left = i;\n"
        new_body += f"{' ' * (inner_indent + 8)}int mid = Math.Min(i + width - 1, {right_param});\n"
        new_body += f"{' ' * (inner_indent + 8)}int right = Math.Min(i + 2 * width - 1, {right_param});\n"
        new_body += f"{' ' * (inner_indent + 8)}if (mid < right) {{\n"
        new_body += f"{' ' * (inner_indent + 12)}Merge({array_param}, left, mid, right, temp);\n"
        new_body += f"{' ' * (inner_indent + 8)}}}\n"
        new_body += f"{' ' * (inner_indent + 4)}}}\n"
        new_body += f"{' ' * inner_indent}}}\n"

    new_body += f"{' ' * base_indent}}}"

    return new_body


def convert_recursive_to_iterative(node, code):
    # 获取函数名和返回类型 - 使用新的函数
    func_name, return_type = extract_function_info(node)

    if not func_name or not return_type:
        return None

    # 分析参数 - 使用新的函数
    params = analyze_parameters(node)

    # 添加参数检查
    if not params:
        return None

    # 添加语言检测
    lang = get_lang()

    # 构建参数字符串
    param_str = ", ".join([f"{p['type']} {p['name']}" for p in params])

    # 获取基本缩进
    base_indent = get_indent(node.start_byte, code)
    inner_indent = base_indent + 4

    # 判断递归模式
    pattern = analyze_recursive_pattern(node, func_name)



    # 根据模式选择转换策略
    new_body = None

    if pattern == RECURSIVE_PATTERN_FACTORIAL:
        new_body = convert_recursive_factorial_to_iterative(
            node, code, func_name, return_type, params, base_indent, inner_indent
        )
    elif pattern == RECURSIVE_PATTERN_FIBONACCI:
        new_body = convert_recursive_fibonacci_to_iterative(
            node, code, func_name, return_type, params, base_indent, inner_indent
        )
    elif pattern == RECURSIVE_PATTERN_SUM:
        new_body = convert_recursive_sum_to_iterative(
            node, code, func_name, return_type, params, base_indent, inner_indent
        )
    elif pattern == RECURSIVE_PATTERN_POWER and len(params) > 1:
        new_body = convert_recursive_power_to_iterative(
            node, code, func_name, return_type, params, base_indent, inner_indent
        )
    elif pattern == RECURSIVE_PATTERN_GCD and len(params) > 1:
        new_body = convert_recursive_gcd_to_iterative(
            node, code, func_name, return_type, params, base_indent, inner_indent
        )
    elif pattern == RECURSIVE_PATTERN_BINARY_SEARCH:
        new_body = convert_recursive_binary_search_to_iterative(
            node, code, func_name, return_type, params, base_indent, inner_indent
        )
    elif pattern == RECURSIVE_PATTERN_TREE_TRAVERSAL:
        new_body = convert_recursive_tree_traversal_to_iterative(
            node, code, func_name, return_type, params, base_indent, inner_indent, lang
        )
    elif pattern == RECURSIVE_PATTERN_QUICK_SORT:
        new_body = convert_recursive_quicksort_to_iterative(
            node, code, func_name, return_type, params, base_indent, inner_indent, lang
        )
    elif pattern == RECURSIVE_PATTERN_MERGE_SORT:
        new_body = convert_recursive_merge_sort_to_iterative(
            node, code, func_name, return_type, params, base_indent, inner_indent, lang
        )
    else:
        # 分析递归调用中参数的变化模式
        param_patterns = analyze_recursive_argument_patterns(node, func_name, params)

        # 使用通用转换
        new_body = convert_recursive_to_iterative_general(
            node, code, func_name, return_type, params, param_patterns, base_indent, inner_indent, lang
        )

    if new_body:
        # 修改：根据语言构造新函数
        if lang == "c":
            new_function = f"{return_type} {func_name}({param_str}) {new_body}"
        else:  # Java/C#
            # 保留方法的修饰符
            modifiers = ""
            for child in node.children:
                if child.type == "modifiers":
                    modifiers = text(child) + " "
                    break

            new_function = f"{modifiers}{return_type} {func_name}({param_str}) {new_body}"

        return [(node.end_byte, node.start_byte), (node.start_byte, new_function)]

    return None


"""==========================迭代转递归函数========================"""


def convert_iterative_factorial_to_recursive(node, code, func_name, return_type, params, base_indent, inner_indent):
    """
    将迭代阶乘函数转换为递归实现
    """
    param_name = params[0]["name"]

    new_body = "{\n"
    new_body += f"{' ' * inner_indent}if ({param_name} <= 1) {{\n"
    new_body += f"{' ' * (inner_indent + 4)}return 1;\n"
    new_body += f"{' ' * inner_indent}}}\n"
    new_body += f"{' ' * inner_indent}return {param_name} * {func_name}({param_name} - 1);\n"
    new_body += f"{' ' * base_indent}}}"

    return new_body


def convert_iterative_fibonacci_to_recursive(node, code, func_name, return_type, params, base_indent, inner_indent):
    """
    将迭代斐波那契函数转换为递归实现
    """
    param_name = params[0]["name"]

    new_body = "{\n"
    new_body += f"{' ' * inner_indent}if ({param_name} <= 1) {{\n"
    new_body += f"{' ' * (inner_indent + 4)}return {param_name};\n"
    new_body += f"{' ' * inner_indent}}}\n"
    new_body += f"{' ' * inner_indent}return {func_name}({param_name} - 1) + {func_name}({param_name} - 2);\n"
    new_body += f"{' ' * base_indent}}}"

    return new_body


def convert_iterative_sum_to_recursive(node, code, func_name, return_type, params, base_indent, inner_indent):
    """
    将迭代求和函数转换为递归实现
    """
    param_name = params[0]["name"]

    new_body = "{\n"
    new_body += f"{' ' * inner_indent}if ({param_name} <= 0) {{\n"
    new_body += f"{' ' * (inner_indent + 4)}return 0;\n"
    new_body += f"{' ' * inner_indent}}}\n"
    new_body += f"{' ' * inner_indent}return {param_name} + {func_name}({param_name} - 1);\n"
    new_body += f"{' ' * base_indent}}}"

    return new_body


def convert_iterative_power_to_recursive(node, code, func_name, return_type, params, base_indent, inner_indent):
    """
    将迭代求幂函数转换为递归实现
    """
    base_param = params[0]["name"]
    exp_param = params[1]["name"]

    new_body = "{\n"
    new_body += f"{' ' * inner_indent}if ({exp_param} == 0) {{\n"
    new_body += f"{' ' * (inner_indent + 4)}return 1;\n"
    new_body += f"{' ' * inner_indent}}}\n"
    new_body += f"{' ' * inner_indent}return {base_param} * {func_name}({base_param}, {exp_param} - 1);\n"
    new_body += f"{' ' * base_indent}}}"

    return new_body


def convert_iterative_gcd_to_recursive(node, code, func_name, return_type, params, base_indent, inner_indent):
    """
    将迭代最大公约数函数转换为递归实现
    """
    a_param = params[0]["name"]
    b_param = params[1]["name"]

    new_body = "{\n"
    new_body += f"{' ' * inner_indent}if ({b_param} == 0) {{\n"
    new_body += f"{' ' * (inner_indent + 4)}return {a_param};\n"
    new_body += f"{' ' * inner_indent}}}\n"
    new_body += f"{' ' * inner_indent}return {func_name}({b_param}, {a_param} % {b_param});\n"
    new_body += f"{' ' * base_indent}}}"

    return new_body


def convert_iterative_binary_search_to_recursive(node, code, func_name, return_type, params, base_indent, inner_indent):
    """
    将迭代二分查找函数转换为递归实现
    """
    array_param = params[0]["name"]
    target_param = params[1]["name"] if len(params) > 1 else "target"
    left_param = params[2]["name"] if len(params) > 2 else "left"
    right_param = params[3]["name"] if len(params) > 3 else "right"

    new_body = "{\n"
    new_body += f"{' ' * inner_indent}// Base case: not found\n"
    new_body += f"{' ' * inner_indent}if ({left_param} > {right_param}) {{\n"
    new_body += f"{' ' * (inner_indent + 4)}return -1;\n"
    new_body += f"{' ' * inner_indent}}}\n\n"

    new_body += f"{' ' * inner_indent}// Find middle index\n"
    new_body += f"{' ' * inner_indent}int mid = {left_param} + ({right_param} - {left_param}) / 2;\n\n"

    new_body += f"{' ' * inner_indent}// Check if target is present at mid\n"
    new_body += f"{' ' * inner_indent}if ({array_param}[mid] == {target_param}) {{\n"
    new_body += f"{' ' * (inner_indent + 4)}return mid;\n"
    new_body += f"{' ' * inner_indent}}}\n\n"

    new_body += f"{' ' * inner_indent}// If target is smaller, search left subarray\n"
    new_body += f"{' ' * inner_indent}if ({array_param}[mid] > {target_param}) {{\n"
    new_body += f"{' ' * (inner_indent + 4)}return {func_name}({array_param}, {target_param}, {left_param}, mid - 1);\n"
    new_body += f"{' ' * inner_indent}}}\n\n"

    new_body += f"{' ' * inner_indent}// If target is greater, search right subarray\n"
    new_body += f"{' ' * inner_indent}return {func_name}({array_param}, {target_param}, mid + 1, {right_param});\n"
    new_body += f"{' ' * base_indent}}}"

    return new_body


def convert_iterative_tree_traversal_to_recursive(node, code, base_indent, inner_indent):
    """
    将迭代树遍历函数转换为递归实现
    基于代码内容猜测是哪种遍历方式
    """
    body_text = ""
    for child in node.children:
        if child.type in ["compound_statement", "block"]:
            body_text = text(child)
            break

    # 通过代码中的关键词猜测遍历方式
    traversal_type = "inorder"  # 默认
    if "stack" in body_text:
        if "push" in body_text and "left" in body_text and "right" in body_text:
            if body_text.find("push") < body_text.find("left") < body_text.find("right"):
                traversal_type = "preorder"
            elif body_text.find("left") < body_text.find("right"):
                traversal_type = "inorder"
            else:
                traversal_type = "postorder"

    # 递归实现
    params = analyze_parameters(node)
    root_param = params[0]["name"]

    new_body = "{\n"
    new_body += f"{' ' * inner_indent}// Base case: empty tree\n"
    new_body += f"{' ' * inner_indent}if ({root_param} == NULL) {{\n"
    new_body += f"{' ' * (inner_indent + 4)}return;\n"
    new_body += f"{' ' * inner_indent}}}\n\n"

    if traversal_type == "preorder":
        new_body += f"{' ' * inner_indent}// Process current node\n"
        new_body += f"{' ' * inner_indent}printf(\"%d \", {root_param}->value); // Or other visit operation\n\n"

        new_body += f"{' ' * inner_indent}// Recursively process left subtree\n"
        new_body += f"{' ' * inner_indent}inorderTraversal({root_param}->left);\n\n"

        new_body += f"{' ' * inner_indent}// Recursively process right subtree\n"
        new_body += f"{' ' * inner_indent}inorderTraversal({root_param}->right);\n"
    elif traversal_type == "inorder":
        new_body += f"{' ' * inner_indent}// Recursively process left subtree\n"
        new_body += f"{' ' * inner_indent}inorderTraversal({root_param}->left);\n\n"

        new_body += f"{' ' * inner_indent}// Process current node\n"
        new_body += f"{' ' * inner_indent}printf(\"%d \", {root_param}->value); // Or other visit operation\n\n"

        new_body += f"{' ' * inner_indent}// Recursively process right subtree\n"
        new_body += f"{' ' * inner_indent}inorderTraversal({root_param}->right);\n"
    else:  # postorder
        new_body += f"{' ' * inner_indent}// Recursively process left subtree\n"
        new_body += f"{' ' * inner_indent}inorderTraversal({root_param}->left);\n\n"

        new_body += f"{' ' * inner_indent}// Recursively process right subtree\n"
        new_body += f"{' ' * inner_indent}inorderTraversal({root_param}->right);\n\n"

        new_body += f"{' ' * inner_indent}// Process current node\n"
        new_body += f"{' ' * inner_indent}printf(\"%d \", {root_param}->value); // Or other visit operation\n"

    new_body += f"{' ' * base_indent}}}"

    return new_body


def convert_iterative_quicksort_to_recursive(node, code, func_name, return_type, params, base_indent, inner_indent):
    """
    将迭代快速排序函数转换为递归实现
    """
    array_param = params[0]["name"]
    left_param = params[1]["name"] if len(params) > 1 else "left"
    right_param = params[2]["name"] if len(params) > 2 else "right"

    new_body = "{\n"
    new_body += f"{' ' * inner_indent}// Base case\n"
    new_body += f"{' ' * inner_indent}if ({left_param} >= {right_param}) {{\n"
    new_body += f"{' ' * (inner_indent + 4)}return;\n"
    new_body += f"{' ' * inner_indent}}}\n\n"

    new_body += f"{' ' * inner_indent}// Partition function\n"
    new_body += f"{' ' * inner_indent}int partition(int arr[], int low, int high) {{\n"
    new_body += f"{' ' * (inner_indent + 4)}int pivot = arr[high];\n"
    new_body += f"{' ' * (inner_indent + 4)}int i = (low - 1);\n\n"

    new_body += f"{' ' * (inner_indent + 4)}for (int j = low; j <= high - 1; j++) {{\n"
    new_body += f"{' ' * (inner_indent + 8)}if (arr[j] < pivot) {{\n"
    new_body += f"{' ' * (inner_indent + 12)}i++;\n"
    new_body += f"{' ' * (inner_indent + 12)}int temp = arr[i];\n"
    new_body += f"{' ' * (inner_indent + 12)}arr[i] = arr[j];\n"
    new_body += f"{' ' * (inner_indent + 12)}arr[j] = temp;\n"
    new_body += f"{' ' * (inner_indent + 8)}}}\n"
    new_body += f"{' ' * (inner_indent + 4)}}}\n\n"

    new_body += f"{' ' * (inner_indent + 4)}int temp = arr[i + 1];\n"
    new_body += f"{' ' * (inner_indent + 4)}arr[i + 1] = arr[high];\n"
    new_body += f"{' ' * (inner_indent + 4)}arr[high] = temp;\n"
    new_body += f"{' ' * (inner_indent + 4)}return (i + 1);\n"
    new_body += f"{' ' * inner_indent}}}\n\n"

    new_body += f"{' ' * inner_indent}// Partition the array\n"
    new_body += f"{' ' * inner_indent}int pivotIndex = partition({array_param}, {left_param}, {right_param});\n\n"

    new_body += f"{' ' * inner_indent}// Recursively sort elements before and after partition\n"
    new_body += f"{' ' * inner_indent}{func_name}({array_param}, {left_param}, pivotIndex - 1);\n"
    new_body += f"{' ' * inner_indent}{func_name}({array_param}, pivotIndex + 1, {right_param});\n"
    new_body += f"{' ' * base_indent}}}"

    return new_body


def convert_iterative_merge_sort_to_recursive(node, code, func_name, return_type, params, base_indent, inner_indent):
    """
    将迭代归并排序函数转换为递归实现
    """
    array_param = params[0]["name"]
    left_param = params[1]["name"] if len(params) > 1 else "left"
    right_param = params[2]["name"] if len(params) > 2 else "right"

    new_body = "{\n"
    new_body += f"{' ' * inner_indent}// Base case\n"
    new_body += f"{' ' * inner_indent}if ({left_param} >= {right_param}) {{\n"
    new_body += f"{' ' * (inner_indent + 4)}return;\n"
    new_body += f"{' ' * inner_indent}}}\n\n"

    new_body += f"{' ' * inner_indent}// Middle point\n"
    new_body += f"{' ' * inner_indent}int mid = {left_param} + ({right_param} - {left_param}) / 2;\n\n"

    new_body += f"{' ' * inner_indent}// Recursively sort first and second halves\n"
    new_body += f"{' ' * inner_indent}{func_name}({array_param}, {left_param}, mid);\n"
    new_body += f"{' ' * inner_indent}{func_name}({array_param}, mid + 1, {right_param});\n\n"

    new_body += f"{' ' * inner_indent}// Merge the sorted halves\n"
    new_body += f"{' ' * inner_indent}void merge(int arr[], int l, int m, int r) {{\n"
    new_body += f"{' ' * (inner_indent + 4)}int i, j, k;\n"
    new_body += f"{' ' * (inner_indent + 4)}int n1 = m - l + 1;\n"
    new_body += f"{' ' * (inner_indent + 4)}int n2 = r - m;\n\n"

    new_body += f"{' ' * (inner_indent + 4)}// Create temp arrays\n"
    new_body += f"{' ' * (inner_indent + 4)}int L[n1], R[n2];\n\n"

    new_body += f"{' ' * (inner_indent + 4)}// Copy data to temp arrays L[] and R[]\n"
    new_body += f"{' ' * (inner_indent + 4)}for (i = 0; i < n1; i++)\n"
    new_body += f"{' ' * (inner_indent + 8)}L[i] = arr[l + i];\n"
    new_body += f"{' ' * (inner_indent + 4)}for (j = 0; j < n2; j++)\n"
    new_body += f"{' ' * (inner_indent + 8)}R[j] = arr[m + 1 + j];\n\n"

    new_body += f"{' ' * (inner_indent + 4)}// Merge the temp arrays back into arr[l..r]\n"
    new_body += f"{' ' * (inner_indent + 4)}i = 0;\n"
    new_body += f"{' ' * (inner_indent + 4)}j = 0;\n"
    new_body += f"{' ' * (inner_indent + 4)}k = l;\n"
    new_body += f"{' ' * (inner_indent + 4)}while (i < n1 && j < n2) {{\n"
    new_body += f"{' ' * (inner_indent + 8)}if (L[i] <= R[j]) {{\n"
    new_body += f"{' ' * (inner_indent + 12)}arr[k] = L[i];\n"
    new_body += f"{' ' * (inner_indent + 12)}i++;\n"
    new_body += f"{' ' * (inner_indent + 8)}}} else {{\n"
    new_body += f"{' ' * (inner_indent + 12)}arr[k] = R[j];\n"
    new_body += f"{' ' * (inner_indent + 12)}j++;\n"
    new_body += f"{' ' * (inner_indent + 8)}}}\n"
    new_body += f"{' ' * (inner_indent + 8)}k++;\n"
    new_body += f"{' ' * (inner_indent + 4)}}}\n\n"

    new_body += f"{' ' * (inner_indent + 4)}// Copy the remaining elements of L[]\n"
    new_body += f"{' ' * (inner_indent + 4)}while (i < n1) {{\n"
    new_body += f"{' ' * (inner_indent + 8)}arr[k] = L[i];\n"
    new_body += f"{' ' * (inner_indent + 8)}i++;\n"
    new_body += f"{' ' * (inner_indent + 8)}k++;\n"
    new_body += f"{' ' * (inner_indent + 4)}}}\n\n"

    new_body += f"{' ' * (inner_indent + 4)}// Copy the remaining elements of R[]\n"
    new_body += f"{' ' * (inner_indent + 4)}while (j < n2) {{\n"
    new_body += f"{' ' * (inner_indent + 8)}arr[k] = R[j];\n"
    new_body += f"{' ' * (inner_indent + 8)}j++;\n"
    new_body += f"{' ' * (inner_indent + 8)}k++;\n"
    new_body += f"{' ' * (inner_indent + 4)}}}\n"
    new_body += f"{' ' * inner_indent}}}\n\n"

    new_body += f"{' ' * inner_indent}merge({array_param}, {left_param}, mid, {right_param});\n"
    new_body += f"{' ' * base_indent}}}"

    return new_body


def convert_iterative_to_recursive(node, code):
    # 获取函数名和返回类型 - 使用新的函数
    func_name, return_type = extract_function_info(node)

    if not func_name or not return_type:
        return None

    # 添加语言检测
    lang = get_lang()

    # 修改：根据语言查找函数体
    body = None
    if lang == "c":
        for child in node.children:
            if child.type == "compound_statement":
                body = child
                break
    else:  # Java/C#
        body = node.child_by_field_name("body")
        if not body:
            for child in node.children:
                if child.type == "block":
                    body = child
                    break

    if not body:
        return None

    body_text = text(body)

    # 分析参数 - 使用新的函数
    params = analyze_parameters(node)

    # 添加参数检查
    if not params:
        return None

    # 构建参数字符串
    param_str = ", ".join([f"{p['type']} {p['name']}" for p in params])

    # 获取基本缩进
    base_indent = get_indent(node.start_byte, code)
    inner_indent = base_indent + 4

    # 猜测迭代函数的模式
    pattern = RECURSIVE_PATTERN_UNKNOWN

    if "factorial" in func_name.lower() or ("*=" in body_text and "for" in body_text):
        pattern = RECURSIVE_PATTERN_FACTORIAL
    elif "fibonacci" in func_name.lower() or ("fib" in func_name.lower() and "+" in body_text):
        pattern = RECURSIVE_PATTERN_FIBONACCI
    elif "sum" in func_name.lower() or ("sum" in body_text and "+=" in body_text):
        pattern = RECURSIVE_PATTERN_SUM
    elif "power" in func_name.lower() or "pow" in func_name.lower():
        pattern = RECURSIVE_PATTERN_POWER
    elif "gcd" in func_name.lower() or ("%" in body_text and "while" in body_text):
        pattern = RECURSIVE_PATTERN_GCD
    elif ("binary" in func_name.lower() and "search" in func_name.lower()) or ("mid" in body_text and "=" in body_text):
        pattern = RECURSIVE_PATTERN_BINARY_SEARCH
    elif "tree" in body_text or "traverse" in func_name.lower():
        pattern = RECURSIVE_PATTERN_TREE_TRAVERSAL
    elif "quicksort" in func_name.lower() or ("pivot" in body_text and "partition" in body_text):
        pattern = RECURSIVE_PATTERN_QUICK_SORT
    elif "mergesort" in func_name.lower() or ("merge" in body_text):
        pattern = RECURSIVE_PATTERN_MERGE_SORT

    # 根据模式选择转换策略
    new_body = None

    if pattern == RECURSIVE_PATTERN_FACTORIAL:
        new_body = convert_iterative_factorial_to_recursive(
            node, code, func_name, return_type, params, base_indent, inner_indent
        )
    elif pattern == RECURSIVE_PATTERN_FIBONACCI:
        new_body = convert_iterative_fibonacci_to_recursive(
            node, code, func_name, return_type, params, base_indent, inner_indent
        )
    elif pattern == RECURSIVE_PATTERN_SUM:
        new_body = convert_iterative_sum_to_recursive(
            node, code, func_name, return_type, params, base_indent, inner_indent
        )
    elif pattern == RECURSIVE_PATTERN_POWER and len(params) > 1:
        new_body = convert_iterative_power_to_recursive(
            node, code, func_name, return_type, params, base_indent, inner_indent
        )
    elif pattern == RECURSIVE_PATTERN_GCD and len(params) > 1:
        new_body = convert_iterative_gcd_to_recursive(
            node, code, func_name, return_type, params, base_indent, inner_indent
        )
    elif pattern == RECURSIVE_PATTERN_BINARY_SEARCH:
        new_body = convert_iterative_binary_search_to_recursive(
            node, code, func_name, return_type, params, base_indent, inner_indent
        )
    elif pattern == RECURSIVE_PATTERN_TREE_TRAVERSAL:
        new_body = convert_iterative_tree_traversal_to_recursive(
            node, code, base_indent, inner_indent
        )
    elif pattern == RECURSIVE_PATTERN_QUICK_SORT:
        new_body = convert_iterative_quicksort_to_recursive(
            node, code, func_name, return_type, params, base_indent, inner_indent
        )
    elif pattern == RECURSIVE_PATTERN_MERGE_SORT:
        new_body = convert_iterative_merge_sort_to_recursive(
            node, code, func_name, return_type, params, base_indent, inner_indent
        )
    else:
        # 尝试创建通用的递归版本
        new_body = "{\n"
        new_body += f"{' ' * inner_indent}// TODO: Implement recursive version of this function\n"
        new_body += f"{' ' * inner_indent}// This function's iterative pattern couldn't be automatically recognized\n"
        new_body += f"{' ' * inner_indent}// Consider implementing a helper function with accumulator parameters\n\n"

        if "sum" in func_name.lower() or "+" in body_text or "+=" in body_text:
            new_body += f"{' ' * inner_indent}// Suggestion: Use recursive accumulator pattern\n"
            new_body += f"{' ' * inner_indent}// Example:\n"
            new_body += f"{' ' * inner_indent}// Helper function: {return_type} {func_name}_recursive({param_str}, int acc) {{\n"
            new_body += f"{' ' * inner_indent}//     if (base_case) return acc;\n"
            new_body += f"{' ' * inner_indent}//     return {func_name}_recursive(updated_params, updated_acc);\n"
            new_body += f"{' ' * inner_indent}// }}\n\n"

            new_body += f"{' ' * inner_indent}// Call helper with initial accumulator value\n"
            new_body += f"{' ' * inner_indent}// return {func_name}_recursive({', '.join([p['name'] for p in params])}, initial_value);\n"

        new_body += f"{' ' * base_indent}}}"

    if new_body:
        # 修改：根据语言构造新函数
        if lang == "c":
            new_function = f"{return_type} {func_name}({param_str}) {new_body}"
        else:  # Java/C#
            # 保留方法的修饰符
            modifiers = ""
            for child in node.children:
                if child.type == "modifiers":
                    modifiers = text(child) + " "
                    break

            new_function = f"{modifiers}{return_type} {func_name}({param_str}) {new_body}"

        return [(node.end_byte, node.start_byte), (node.start_byte, new_function)]

    return None



def find_method_identifier_recursive(node):
    """递归查找复杂方法结构中的标识符"""
    if node.type == "identifier":
        return text(node)

    if hasattr(node, "children"):
        for child in node.children:
            result = find_method_identifier_recursive(child)
            if result:
                return result

    return None


def count_recursive_functions(root):
    """
    Count the number of recursive functions in the AST
    """
    nodes = match_recursive_functions(root)
    return len(nodes)

def count_iterative_functions(root):
    """
    Count the number of iterative functions in the AST
    """
    nodes = match_iterative_functions(root)
    return len(nodes)


