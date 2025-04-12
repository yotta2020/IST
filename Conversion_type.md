
---

# Code Equivalence Transformations

Here we summarize the code equivalence, covering variable naming, code structure, control flow, assignments, arrays, functions, and more. Below is a comprehensive list of transformation types, organized by category, with their IDs as defined in the `style_dict` of the `IST` class.

---

## 1. Variable Naming (`identifier_name`)
| ID   | Type               | Description                                   |
|------|--------------------|-----------------------------------------------|
| 0.1  | `camel`            | Convert variable names to camelCase (e.g., `myVar`) |
| 0.2  | `pascal`           | Convert variable names to PascalCase (e.g., `MyVar`) |
| 0.3  | `snake`            | Convert variable names to snake_case (e.g., `my_var`) |
| 0.4  | `hungarian`        | Convert variable names to Hungarian notation (e.g., `strMyVar`) |
| 0.5  | `init_underscore`  | Add an underscore prefix to variable names (e.g., `_myVar`) |
| 0.6  | `init_dollar`      | Add a dollar sign prefix to variable names (e.g., `$myVar`) |
| 0.7  | `upper`            | Convert variable names to UPPERCASE (e.g., `MYVAR`) |
| 0.8  | `lower`            | Convert variable names to lowercase (e.g., `myvar`) |

---

## 2. Token Substitution (`tokensub`)
| ID   | Type | Description                                   |
|------|------|-----------------------------------------------|
| -3.1 | `sh` | Substitute tokens with shell-script-like style |
| -3.2 | `rb` | Substitute tokens with Ruby-like style        |

---

## 3. Invisible Character Insertion (`invichar`)
| ID   | Type    | Description                                      |
|------|---------|--------------------------------------------------|
| -2.1 | `ZWSP`  | Insert Zero-Width Space characters              |
| -2.2 | `ZWNJ`  | Insert Zero-Width Non-Joiner characters         |
| -2.3 | `LRO`   | Insert Left-to-Right Override characters        |
| -2.4 | `BKSP`  | Insert Backspace-like invisible characters      |

---

## 4. Dead Code Insertion (`deadcode`)
| ID   | Type        | Description                                   |
|------|-------------|-----------------------------------------------|
| -1.1 | `deadcode1` | Insert type 1 dead (unreachable) code         |
| -1.2 | `deadcode2` | Insert type 2 dead (unreachable) code         |

---

## 5. Code Cleaning (`clean`)
| ID   | Type    | Description                                   |
|------|---------|-----------------------------------------------|
| 0.0  | `clean` | Perform a no-op cleaning operation (placeholder) |

---

## 6. Bracket Handling (`bracket`)
| ID   | Type           | Description                                      |
|------|----------------|--------------------------------------------------|
| 1.1  | `del_bracket`  | Remove brackets from `if`/`for`/`while` statements |
| 1.2  | `add_bracket`  | Add brackets to `if`/`for`/`while` statements    |

---

## 7. Assignment Adjustments (`augmented_assignment`)
| ID   | Type               | Description                                      |
|------|--------------------|--------------------------------------------------|
| 2.1  | `non_augmented`    | Convert compound assignments to standard (e.g., `x = x + 1`) |
| 2.2  | `augmented`        | Convert standard assignments to compound (e.g., `x += 1`)    |

---

## 8. Comparison Operator Transformation (`cmp`)
| ID   | Type         | Description                                   |
|------|--------------|-----------------------------------------------|
| 3.1  | `smaller`    | Standardize comparisons to use `<`            |
| 3.2  | `bigger`     | Standardize comparisons to use `>`            |
| 3.3  | `equal`      | Standardize comparisons to use `==`           |
| 3.4  | `not_equal`  | Standardize comparisons to use `!=`           |

---

## 9. `for` Loop Updates (`for_update`)
| ID   | Type          | Description                                   |
|------|---------------|-----------------------------------------------|
| 4.1  | `left`        | Use left decrement (e.g., `i--`) in `for` loops |
| 4.2  | `right`       | Use right increment (e.g., `i++`) in `for` loops |
| 4.3  | `augment`     | Use augmented assignment (e.g., `i += 1`)    |
| 4.4  | `assignment`  | Use standard assignment (e.g., `i = i + 1`)  |

---

## 10. Array-Related Transformations
### 10.1 Array Definition (`array_definition`)
| ID   | Type         | Description                                      |
|------|--------------|--------------------------------------------------|
| 5.1  | `dyn_mem`    | Convert static arrays to dynamic memory (e.g., `malloc`) |
| 5.2  | `static_mem` | Convert dynamic arrays to static memory          |

### 10.2 Array Access (`array_access`)
| ID   | Type      | Description                                   |
|------|-----------|-----------------------------------------------|
| 6.1  | `pointer` | Convert array access to pointer access (e.g., `*p`) |
| 6.2  | `array`   | Convert pointer access to array access (e.g., `arr[i]`) |

---

## 11. Variable Declaration Transformations
### 11.1 Declaration Lines (`declare_lines`)
| ID   | Type     | Description                                      |
|------|----------|--------------------------------------------------|
| 7.1  | `split`  | Split merged variable declarations into multiple lines |
| 7.2  | `merge`  | Merge multiple variable declarations into one line |

### 11.2 Declaration Position (`declare_position`)
| ID   | Type     | Description                                      |
|------|----------|--------------------------------------------------|
| 8.1  | `first`  | Move variable declarations to function start    |
| 8.2  | `temp`   | Convert variables to temporary variables        |

### 11.3 Declaration and Assignment (`declare_assign`)
| ID   | Type     | Description                                      |
|------|----------|--------------------------------------------------|
| 9.1  | `split`  | Split declaration and assignment (e.g., `int x; x = 1;`) |
| 9.2  | `merge`  | Merge declaration and assignment (e.g., `int x = 1;`) |

---

## 12. `for` Loop Formatting (`for_format`)
| ID    | Type  | Description                                   |
|-------|-------|-----------------------------------------------|
| 10.0  | `abc` | Adjust `for` loop to `abc` format             |
| 10.1  | `obc` | Adjust `for` loop to `obc` format             |
| 10.2  | `aoc` | Adjust `for` loop to `aoc` format             |
| 10.3  | `abo` | Adjust `for` loop to `abo` format             |
| 10.4  | `aoo` | Adjust `for` loop to `aoo` format             |
| 10.5  | `obo` | Adjust `for` loop to `obo` format             |
| 10.6  | `ooc` | Adjust `for` loop to `ooc` format             |
| 10.7  | `ooo` | Adjust `for` loop to `ooo` format             |

---

## 13. Loop Type Conversion (`for_while`)
| ID    | Type         | Description                                   |
|-------|--------------|-----------------------------------------------|
| 11.1  | `for`        | Convert loops to `for` loops                  |
| 11.2  | `while`      | Convert loops to `while` loops                |
| 11.3  | `do_while`   | Convert loops to `do-while` loops             |

---

## 14. Infinite Loop Handling (`loop_infinite`)
| ID    | Type             | Description                                   |
|-------|------------------|-----------------------------------------------|
| 11.4  | `infinite_while` | Convert loops to infinite `while` loops       |
| 12.2  | `infinite_for`   | Convert loops to infinite `for` loops         |

---

## 15. Control Flow Adjustments
### 15.1 Break to Goto (`break_goto`)
| ID    | Type   | Description                                   |
|-------|--------|-----------------------------------------------|
| 13.1  | `goto` | Convert `break` statements to `goto`          |
| 13.2  | `break`| Convert `goto` statements to `break`          |

### 15.2 If Statement Transformations
| ID    | Type               | Description                                   |
|-------|--------------------|-----------------------------------------------|
| 14.1  | `not_exclamation`  | Convert `!` expressions to equivalent forms   |
| 14.2  | `exclamation`      | Convert conditions to use `!` expressions     |
| 15.1  | `not_return`       | Remove `return` from `if` statements          |
| 15.2  | `return`           | Add `return` to `if` statements               |
| 16.1  | `switch`           | Convert `if-else` to `switch`                 |
| 16.2  | `if`               | Convert `switch` to `if-else`                 |
| 17.1  | `not_nested`       | Flatten nested `if` statements                |
| 17.2  | `nested`           | Nest `if` statements                          |
| 18.1  | `not_else`         | Remove `else` clauses                         |
| 18.2  | `else`             | Add `else` clauses                            |

---

## 16. Ternary Operator Conversion (`ternary`)
| ID    | Type         | Description                                   |
|-------|--------------|-----------------------------------------------|
| 19.1  | `to_ternary` | Convert `if-else` to ternary operator         |
| 19.2  | `to_if`      | Convert ternary operator to `if-else`         |

---

## 17. Function Nesting (`func_nested`)
| ID    | Type          | Description                                   |
|-------|---------------|-----------------------------------------------|
| 20.1  | `nested`      | Nest functions within other functions         |
| 20.2  | `not_nested`  | Flatten nested functions                      |

---

## 18. Recursion and Iteration Conversion (`recursive_iterative`)
| ID    | Type            | Description                                   |
|-------|-----------------|-----------------------------------------------|
| 21.1  | `to_iterative`  | Convert recursive functions to iterative      |
| 21.2  | `to_recursive`  | Convert iterative functions to recursive      |

---

