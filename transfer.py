import sys, os

sys.path.insert(0, os.path.dirname(__file__))
import json
import random
import argparse
import subprocess
from ist_utils import *
from tqdm import tqdm
from tree_sitter import Parser, Language


class IST:
    def __init__(self, language, expand=0):
        self.language = language
        parent_dir = os.path.dirname(__file__)
        languages_so_path = os.path.join(
            parent_dir, "build", f"{language}-languages.so"
        )
        tree_sitter_path = os.path.join(parent_dir, f"tree-sitter-{language}")

        if not os.path.exists(languages_so_path):
            if not os.path.exists(tree_sitter_path):
                process = subprocess.Popen(
                    [
                        "git",
                        "clone",
                        f"https://github.com/tree-sitter/tree-sitter-{language}",
                    ],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                )
                process.wait()
                if process.returncode == 0:
                    print(f"Download of tree-sitter-{language} successful.")
                else:
                    print(
                        f"Poor internet connection, please download https://github.com/tree-sitter/tree-sitter-{language} manually."
                    )
                    exit(0)

            Language.build_library(languages_so_path, [tree_sitter_path])
            # os.system(f'rm -rf ./tree-sitter-{language}')

        parser = Parser()
        parser.set_language(Language(languages_so_path, language))
        self.parser = parser

        from transform.config import transformation_operators as op
        from transform.lang import set_lang, set_expand

        set_lang(language)
        set_expand(expand)

        self.op = op

        self.style_group = {"0": ["0.1", "0.2", "0.3", "0.4", "0.5", "0.6"]}

        self.style_desc = {
            "0.1": ("aabb", "aaBb"),
            "0.2": ("aabb", "AaBb"),
            "0.3": ("aabb", "aa_bb"),
            "0.4": ("aabb", "typeAabb"),
            "0.5": ("aabb", "_aabb"),
            "0.6": ("aabb", "$aabb"),
            "1.1": ("if/for/while {...}", "if/for/while ..."),
            "1.2": ("if/for/while ...", "if/for/while {...}"),
        }

        self.style_dict = {
            "-3.1": ("tokensub", "sh"),
            "-2.1": ("invichar", "ZWSP"),
            "-2.2": ("invichar", "ZWNJ"),
            "-2.3": ("invichar", "LRO"),
            "-2.4": ("invichar", "BKSP"),
            "-1.1": ("deadcode", "deadcode1"),
            "-1.2": ("deadcode", "deadcode2"),
            "-1.3": ("deadcode", "deadcode_cs"),
            "0.0": ("clean", "clean"),
            "0.1": ("identifier_name", "camel"),
            "0.2": ("identifier_name", "pascal"),
            "0.3": ("identifier_name", "snake"),
            "0.4": ("identifier_name", "hungarian"),
            "0.5": ("identifier_name", "init_underscore"),
            "0.6": ("identifier_name", "init_dollar"),
            "1.1": ("bracket", "del_bracket"),
            "1.2": ("bracket", "add_bracket"),
            "2.1": ("augmented_assignment", "non_augmented"),
            "2.2": ("augmented_assignment", "augmented"),
            "3.1": ("cmp", "smaller"),
            "3.2": ("cmp", "bigger"),
            "3.3": ("cmp", "equal"),
            "3.4": ("cmp", "not_equal"),
            "4.1": ("for_update", "left"),
            "4.2": ("for_update", "right"),
            "4.3": ("for_update", "augment"),
            "4.4": ("for_update", "assignment"),
            "5.1": ("array_definition", "dyn_mem"),
            "5.2": ("array_definition", "static_mem"),
            "6.1": ("array_access", "pointer"),
            "6.2": ("array_access", "array"),
            "7.1": ("declare_lines", "split"),
            "7.2": ("declare_lines", "merge"),
            "8.1": ("declare_position", "first"),
            "8.2": ("declare_position", "temp"),
            "9.1": ("declare_assign", "split"),
            "9.2": ("declare_assign", "merge"),
            "10.0": ("for_format", "abc"),
            "10.1": ("for_format", "obc"),
            "10.2": ("for_format", "aoc"),
            "10.3": ("for_format", "abo"),
            "10.4": ("for_format", "aoo"),
            "10.5": ("for_format", "obo"),
            "10.6": ("for_format", "ooc"),
            "10.7": ("for_format", "ooo"),
            "11.1": ("for_while", "for"),
            "11.2": ("for_while", "while"),
            "11.3": ("for_while", "do_while"),
            "11.4": ("loop_infinite", "infinite_while"),
            "12.1": ("loop_infinite", "finite_for"),
            "12.2": ("loop_infinite", "infinite_for"),
            "12.3": ("loop_infinite", "finite_while"),
            "12.4": ("loop_infinite", "infinite_while"),
            "13.1": ("break_goto", "goto"),
            "13.2": ("break_goto", "break"),
            "14.1": ("if_exclamation", "not_exclamation"),
            "14.2": ("if_exclamation", "exclamation"),
            "15.1": ("if_return", "not_return"),
            "15.2": ("if_return", "return"),
            "16.1": ("if_switch", "switch"),
            "16.2": ("if_switch", "if"),
            "17.1": ("if_nested", "not_nested"),
            "17.2": ("if_nested", "nested"),
            "18.1": ("if_else", "not_else"),
            "18.2": ("if_else", "else"),
        }

        self.need_bracket = ["10", "11", "12", "17"]
        self.exclude = {"java": ["5", "6"], "c": [], "c_sharp": [], "python": []}

    def transfer(self, styles=[], code=""):
        orig_code = code
        if not isinstance(styles, list):
            styles = [styles]
        if len(styles) == 0:
            return code, 0
        succs = []
        # print(styles)
        for style in styles:
            if style == "8.1":
                if self.get_style(code=code, styles=["8.1"])["8.1"] > 0:
                    succs.append(int(1))
                    continue
            raw_code = code
            # if self.get_style(code, style)[style] > 0: return code, 1
            if style in self.exclude[self.language]:
                continue
            if style in self.need_bracket:
                code, _ = self.transfer(["1.2"], code)
            if style.split(".")[0] == "10":
                code, _ = self.transfer(["11.1"], code)
            # if style == "-3.1":
            #     sys.path.append(
            #         "/home/nfs/share/backdoor2023/backdoor/Authorship-Attribution/dataset"
            #     )
            #     from tokensub import substitude_token

            #     code, succ = substitude_token(
            #         code, ["sh"], self.language, position=["l"]
            #     )
            #     succs.append(int(succ))
            #     continue
            AST = self.parser.parse(bytes(code, encoding="utf-8"))
            (style_type, style_subtype) = self.style_dict[style]
            (match_func, convert_func, _) = self.op[style_type][style_subtype]
            operations = []
            match_nodes = match_func(AST.root_node)
            if len(match_nodes) == 0:
                return code, style == "0.0"
            for node in match_nodes:
                if get_parameter_count(convert_func) == 1:
                    op = convert_func(node)
                else:
                    op = convert_func(node, code)
                if op is not None:
                    operations.extend(op)

            code = replace_from_blob(operations, code)
            succ = raw_code.replace(" ", "").replace("\n", "").replace(
                "\t", ""
            ) != code.replace(" ", "").replace("\n", "").replace("\t", "")
            # if succ and len(code.replace(" ", "")) <= 400:
            #     print(code)
            succs.append(int(succ))
        # print(succs)
        return code, 0 not in succs
        # return code, 1 in succs

    def get_style(self, code="", styles=[]):
        if not isinstance(styles, list):
            styles = [styles]
        res = {}
        if len(styles) == 0:
            styles = list(self.style_dict[self.language].keys())
        for style in styles:
            AST = self.parser.parse(bytes(code, encoding="utf-8"))
            (style_type, style_subtype) = self.style_dict[style]
            (_, _, count_func) = self.op[style_type][style_subtype]
            if style in res:
                res[style] += count_func(AST.root_node)
            else:
                res[style] = count_func(AST.root_node)
        return res

    def tokenize(self, code):
        tree = self.parser.parse(bytes(code, "utf8"))
        root_node = tree.root_node
        tokens = []
        tokenize_help(root_node, tokens)
        return tokens

    def check_syntax(self, code):
        AST = self.parser.parse(bytes(code, encoding="utf-8"))
        return not AST.root_node.has_error


if __name__ == "__main__":
    with open("./test_code/test.c", "r") as f:
        code = f.read()

    ist = IST("c")
    # ? -3.1 -1.1 0.5 7.2 8.1 9.1 11.3 3.4 4.4 10.7
    style = "10.7"

    pcode, succ = ist.transfer(code=code, styles=[style])
    print(f"succ = {succ}")
    print(pcode)

    print(
        f"{ist.get_style(code=code, styles=[style])[style]} -> {ist.get_style(code=pcode, styles=[style])[style]}"
    )

    exit(0)
