# Environment

```
sudo apt-get install git graphviz graphviz-doc
pip install -r requirements.txt
```

## for windows

Need to download [Visual Studio Build Tools](https://visualstudio.microsoft.com/zh-hans/visual-cpp-build-tools/)

# Introduction

IST is the abbreviation for **S**tyle **C**hange by **T**ree **S**itter, this tool aims to change a program to a specific style through tree-sitter.
Up till now, it can change C/C++/python with 148 rules, and it can also show the visual AST tree with graphviz and tokenize the code.
It will be continuous updated...

# How to use

This code is to define a class IST, the parametre is the language of the codes.

```
ist = IST('c')
```

After that, you can change the single file's style using code below, where the first parametre is the target style, this function will return the changed code and whether the original code is changed successfully.

```
new_code, succ = ist.change_file_style([8.11], code)
```

You can also change the style of a directory which contains many code files with the same language, the parametres respectively represent target style list, original directory path, output directory path and output choice:

- -1: do not output
- 0: output only files changed successfully
- 1: output all files splited by succ and fail
- 2: output all files merged

```
ist.change_dir_style([style_choice], 'dataset/gcjpy_format', f'change/{style_choice}', output_choice=-1)
```

You can get the popularity of the single file's/directory's original styles by:

```
ist.get_file_popularity(5.1, code)
ist.get_dir_popularity(5.1, 'dataset/ProgramData/2')
```

**You can see the style's information** in {language}/transform\*.py's cvt\_\* function's comments.

If you want to get AST's pdf, you can use:

```
ist.see_tree(code)
```

![AST](https://github.com/user-attachments/assets/870462d9-2d37-47a3-b81c-058f1d36562d)


If you want to get code's tokens, you can use:

```
ist.tokenize(code)
```

If you want to generate CFG of C program, you can run CFG.py

```
python CFG.py
```

![捕获](https://github.com/rebibabo/SCTS/assets/80667434/ef06409b-4cb9-45ed-be69-4b28760546ce)
