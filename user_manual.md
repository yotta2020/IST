# Code Transformer User Manual

## Overview

The `Code Transformer` tool transforms code in JSONL datasets, applying specified transformations (e.g., converting `while` to `for` loops). It supports GUI and command-line interfaces, allowing users to select a dataset file, choose transformations, specify the code field, retain desired fields, and set the programming language.

## Installation

1. Install dependencies:
   ```bash
   pip install tkinter
   ```

## Usage

### GUI Mode

Run:

```bash
python BatchSample_Generator.py
```
**Steps**:

1. **Select Dataset File**: Click "Browse" to choose a .jsonl file (e.g., train.jsonl).
2. **Choose Language**: Select a language (c, java, python, c_sharp) from the dropdown (default: c).
3. **Specify Code Field**: Enter the field containing code (e.g., func or code, default: func).
4. **Select Fields**: Checkboxes show detected fields (e.g., func, target, idx). Select fields to retain in the output.
5. **Add Transformations**: Enter a style (e.g., 11.1 for while->for), click "Add". Add multiple transformations for sequential application. Delete unwanted ones with "Delete".
6. **Set Output Path**: Defaults to dataset/processed_data/<input_name>_processed.jsonl. Modify via "Browse" or text entry.
7. **Verbose Logging**: Check "Verbose Logging" for detailed logs (default: off).
8. **Run**: Click "Run Transformation" to process the dataset.

**Output**:

- Transformed dataset saved as JSONL.
- Console shows loaded functions, output path, total conversions, and transformation types.
- Logs written to transform.log.

### Command-Line Mode

Run:

```bash
python BatchSample_Generator.py --dpath <input.jsonl> --trans <styles> [options]`
```
**Arguments**:

- --dpath: Path to input JSONL file (required).
- --trans: Transformation styles (e.g., 11.1 9.2) (required).
- --opath: Output JSONL file path (optional, default: dataset/processed_data/<input_name>_processed.jsonl).
- --code_field: Field containing code (default: func).
- --fields: Fields to retain (e.g., func target idx, optional, default: all fields).
- --lang: Programming language (c, java, python, c_sharp, default: c).
- --verbose: Enable detailed logging (default: off).

**Examples**:

```bash
#Basic usage
python BatchSample_Generator.py --dpath train.jsonl --trans 11.1 9.2
#Specify language and fields
python BatchSample_Generator.py --dpath train.jsonl --trans 11.1 --lang java --fields func target 
# Verbose logging 
python BatchSample_Generator.py --dpath train.jsonl --trans 11.1 9.2 --verbose`
```
**Output**:

- Console: Loaded functions, output path, total conversions, transformation types, processed functions.
- Log file (transform.log): Basic info (or detailed with --verbose).

## Log File

- **Location**: transform.log
- **Content** (basic):
    - Input/output filenames
    - Language
    - Total conversions
    - Transformation types and counts
    - Selected fields
- **Content** (verbose):
    - Adds per-function transformation details

**Example**:

```text
2025-04-12 10:00:00,123 - INFO - Input file: train.jsonl
Output file: train_processed.jsonl Language: c
Total functions converted: 140 
Transformations applied: 11.1, 9.2 
Conversions per type: {'11.1': 80, '9.2': 60}
Selected fields: func, target, idx`
```
## Notes

- Ensure the JSONL file has valid code in the specified code_field.
- Transformations (e.g., 11.1) depend on the IST class implementation.
- Output retains selected fields, ensuring flexibility for datasets like CodeXGLUE.

## Troubleshooting

- **File not found**: Verify --dpath points to a valid .jsonl file.
- **Invalid JSONL**: Check file format; each line must be a valid JSON object.
- **Transformation failure**: Ensure IST supports the specified styles and language.

For further assistance, check transform.log or contact us.
