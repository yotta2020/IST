import os
import sys
import argparse
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import json
import logging
import pandas as pd
from typing import List, Dict
from datetime import datetime
from datasets import Dataset, Features, Value

from transfer import IST  

class CodeTransformerGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Code Transformer")
        self.root.geometry("800x600")
        self.language = "c"
        self.dataset_file = ""
        self.transformations = []
        self.output_path = ""
        self.code_field = "func"
        self.fields = []
        self.selected_fields = []
        self.verbose_logging = False
        self.output_format = "jsonl"  # Default output format
        self.ist = IST(self.language)
        # Supported transformation styles (mock list, adjust based on IST)
        self.supported_styles = [
    "-3.1", "-2.1", "-2.2", "-2.3", "-2.4",
    "-1.1", "-1.2", "-1.3",
    "0.0", "0.1", "0.2", "0.3", "0.4", "0.5", "0.6",
    "1.1", "1.2", "2.1", "2.2",
    "3.1", "3.2", "3.3", "3.4",
    "4.1", "4.2", "4.3", "4.4",
    "5.1", "5.2", "6.1", "6.2",
    "7.1", "7.2", "8.1", "8.2",
    "9.1", "9.2", "10.0", "10.1", "10.2", "10.3", "10.4", "10.5", "10.6", "10.7",
    "11.1", "11.2", "11.3", "11.4",
    "12.1", "12.2", "12.3", "12.4",
    "13.1", "13.2",
    "14.1", "14.2",
    "15.1", "15.2",
    "16.1", "16.2",
    "17.1", "17.2",
    "18.1", "18.2",
    "19.1", "19.2",
    "20.1", "20.2",
    "21.1", "21.2"
]

        # Setup logging
        logging.basicConfig(
            filename="transform.log",
            level=logging.INFO,
            format="%(asctime)s - %(levelname)s - %(message)s"
        )
        self.logger = logging.getLogger()

        # GUI Layout
        self._setup_gui()

    def _setup_gui(self):
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # Language Selection
        ttk.Label(main_frame, text="Language:", font=("Arial", 12)).grid(row=0, column=0, sticky="w", pady=5)
        self.language_var = tk.StringVar(value=self.language)
        languages = ["c", "java", "python", "c_sharp"]
        ttk.OptionMenu(main_frame, self.language_var, self.language, *languages, command=self._update_language).grid(row=0, column=1, sticky="w", pady=5)

        # Dataset File Selection
        ttk.Label(main_frame, text="Dataset File:", font=("Arial", 12)).grid(row=1, column=0, sticky="w", pady=5)
        self.file_entry = ttk.Entry(main_frame, width=50)
        self.file_entry.grid(row=1, column=1, pady=5)
        ttk.Button(main_frame, text="Browse", command=self._browse_dataset).grid(row=1, column=2, padx=5, pady=5)

        # Code Field Selection
        ttk.Label(main_frame, text="Code Field:", font=("Arial", 12)).grid(row=2, column=0, sticky="w", pady=5)
        self.code_field_entry = ttk.Entry(main_frame, width=20)
        self.code_field_entry.insert(0, self.code_field)
        self.code_field_entry.grid(row=2, column=1, sticky="w", pady=5)

        # Fields Selection
        ttk.Label(main_frame, text="Select Fields:", font=("Arial", 12)).grid(row=3, column=0, sticky="w", pady=5)
        self.fields_frame = ttk.Frame(main_frame)
        self.fields_frame.grid(row=3, column=1, sticky="w", pady=5)
        self.field_vars = {}

        # Transformations
        ttk.Label(main_frame, text="Transformations:", font=("Arial", 12)).grid(row=4, column=0, sticky="w", pady=5)
        self.transform_listbox = tk.Listbox(main_frame, height=8, width=50)
        self.transform_listbox.grid(row=4, column=1, pady=5)

        # Transformation Controls
        trans_frame = ttk.Frame(main_frame)
        trans_frame.grid(row=5, column=1, pady=5)
        ttk.Label(trans_frame, text="Add Style:").pack(side=tk.LEFT)
        self.style_var = tk.StringVar()
        ttk.OptionMenu(trans_frame, self.style_var, self.supported_styles[0], *self.supported_styles).pack(side=tk.LEFT, padx=5)
        ttk.Button(trans_frame, text="Add", command=self._add_transformation).pack(side=tk.LEFT, padx=5)
        ttk.Button(trans_frame, text="Delete", command=self._delete_transformation).pack(side=tk.LEFT, padx=5)

        # Output Path
        ttk.Label(main_frame, text="Output Path:", font=("Arial", 12)).grid(row=6, column=0, sticky="w", pady=5)
        self.output_entry = ttk.Entry(main_frame, width=50)
        self.output_entry.grid(row=6, column=1, pady=5)
        ttk.Button(main_frame, text="Browse", command=self._browse_output).grid(row=6, column=2, padx=5, pady=5)

        # Output Format
        ttk.Label(main_frame, text="Output Format:", font=("Arial", 12)).grid(row=7, column=0, sticky="w", pady=5)
        self.format_var = tk.StringVar(value=self.output_format)
        formats = ["jsonl", "csv", "dataset"]
        ttk.OptionMenu(main_frame, self.format_var, self.output_format, *formats).grid(row=7, column=1, sticky="w", pady=5)

        # Verbose Logging
        self.verbose_var = tk.BooleanVar(value=self.verbose_logging)
        ttk.Checkbutton(main_frame, text="Verbose Logging", variable=self.verbose_var, command=self._toggle_verbose).grid(row=8, column=1, sticky="w", pady=5)

        # Run Button
        ttk.Button(main_frame, text="Run Transformation", command=self._run_transformation).grid(row=9, column=1, pady=20)

    def _update_language(self, value):
        self.language = value
        self.ist = IST(self.language)

    def _toggle_verbose(self):
        self.verbose_logging = self.verbose_var.get()
        self.logger.setLevel(logging.DEBUG if self.verbose_logging else logging.INFO)

    def _browse_dataset(self):
        self.dataset_file = filedialog.askopenfilename(title="Select JSONL File", filetypes=[("JSONL Files", "*.jsonl")])
        if self.dataset_file:
            self.file_entry.delete(0, tk.END)
            self.file_entry.insert(0, self.dataset_file)
            base_name = os.path.basename(self.dataset_file)
            name, ext = os.path.splitext(base_name)
            default_output = os.path.join("dataset", "processed_data", f"{name}_processed{ext}")
            self.output_entry.delete(0, tk.END)
            self.output_entry.insert(0, default_output)
            self._detect_fields()

    def _detect_fields(self):
        self.fields = []
        try:
            with open(self.dataset_file, "r", encoding="utf-8") as f:
                first_line = f.readline().strip()
                if first_line:
                    data = json.loads(first_line)
                    self.fields = list(data.keys())
                    self.selected_fields = self.fields.copy()
        except Exception as e:
            messagebox.showwarning("Warning", f"Could not detect fields: {str(e)}")
            return

        for widget in self.fields_frame.winfo_children():
            widget.destroy()
        self.field_vars.clear()

        for field in self.fields:
            var = tk.BooleanVar(value=True)
            self.field_vars[field] = var
            ttk.Checkbutton(self.fields_frame, text=field, variable=var).pack(anchor="w")

    def _browse_output(self):
        output_file = filedialog.asksaveasfilename(
            title="Select Output File",
            defaultextension=f".{self.format_var.get()}",
            filetypes=[(f"{self.format_var.get().upper()} Files", f"*.{self.format_var.get()}")]
        )
        if output_file:
            self.output_entry.delete(0, tk.END)
            self.output_entry.insert(0, output_file)
            self.output_path = output_file

    def _add_transformation(self):
        style = self.style_var.get()
        if style:
            self.transformations.append(style)
            self.transform_listbox.insert(tk.END, style)
            self.style_var.set(self.supported_styles[0])  # Reset dropdown
        else:
            messagebox.showwarning("Input Error", "Please select a transformation style.")

    def _delete_transformation(self):
        selection = self.transform_listbox.curselection()
        if selection:
            idx = selection[0]
            self.transform_listbox.delete(idx)
            self.transformations.pop(idx)
        else:
            messagebox.showwarning("Selection Error", "Please select a transformation to delete.")

    def _fetch_codexglue_jsonl_dataset(self, dataset_file: str, code_field: str) -> List[dict]:
        if not os.path.exists(dataset_file):
            raise FileNotFoundError(f"Dataset file '{dataset_file}' does not exist.")
        
        code_snippets = []
        with open(dataset_file, "r", encoding="utf-8") as f:
            for line in f:
                try:
                    data = json.loads(line.strip())
                    if code_field in data and data[code_field].strip():
                        code_snippets.append(data)
                except json.JSONDecodeError:
                    self.logger.warning(f"Skipping invalid JSONL line in {dataset_file}")
        self.logger.info(f"Loaded {len(code_snippets)} functions from '{dataset_file}'.")
        print(f"Loaded {len(code_snippets)} functions.")
        return code_snippets

    def _transform_dataset(self, code_snippets: List[dict], transformations: List[str], code_field: str) -> List[dict]:
        transformed_snippets = code_snippets.copy()
        total_converted = 0
        conversions_per_style = {style: 0 for style in transformations}

        for style in transformations:
            current_snippets = []
            converted_count = 0

            for item in transformed_snippets:
                code = item[code_field]
                if not code.strip():
                    current_snippets.append(item)
                    continue
                style_count = self.ist.get_style(code=code, styles=[style]).get(style, 0)
                if style_count > 0:
                    new_code, success = self.ist.transfer(styles=[style], code=code)
                    if success:
                        new_item = item.copy()
                        new_item[code_field] = new_code
                        current_snippets.append(new_item)
                        converted_count += 1
                        if self.verbose_logging:
                            self.logger.debug(f"Function (idx: {item.get('idx', 'N/A')}): Applied {style} successfully")
                    else:
                        current_snippets.append(item)
                        if self.verbose_logging:
                            self.logger.debug(f"Function (idx: {item.get('idx', 'N/A')}): Failed to apply {style}")
                else:
                    current_snippets.append(item)
                    if self.verbose_logging:
                        self.logger.debug(f"Function (idx: {item.get('idx', 'N/A')}): No {style} found")

            transformed_snippets = current_snippets
            conversions_per_style[style] = converted_count
            total_converted += converted_count

        final_snippets = []
        for item in transformed_snippets:
            new_item = {k: item[k] for k in self.selected_fields if k in item}
            final_snippets.append(new_item)

        log_info = (
            f"Input file: {os.path.basename(self.dataset_file)}\n"
            f"Output file: {os.path.basename(self.output_path)}\n"
            f"Language: {self.language}\n"
            f"Total functions converted: {total_converted}\n"
            f"Transformations applied: {', '.join(transformations)}\n"
            f"Conversions per type: {conversions_per_style}\n"
            f"Selected fields: {', '.join(self.selected_fields)}"
        )
        self.logger.info(log_info)

        print(f"Dataset saved to: {self.output_path}")
        print(f"Total functions converted: {total_converted}")
        print(f"Transformation types applied: {', '.join(transformations)}")
        print(f"Processed {len(final_snippets)} functions.")
        return final_snippets

    def _process_for_training(self, transformed_snippets: List[dict], output_path: str, output_format: str):
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        if output_format == "jsonl":
            with open(output_path, "w", encoding="utf-8") as f:
                for item in transformed_snippets:
                    f.write(json.dumps(item) + "\n")
        elif output_format == "csv":
            df = pd.DataFrame(transformed_snippets)
            df.to_csv(output_path, index=False)
        elif output_format == "dataset":
            features_dict = {
                k: Value("string") for k in transformed_snippets[0].keys()
            }
            # Adjust types for known fields
            if "target" in features_dict:
                features_dict["target"] = Value("int32")
            if "idx" in features_dict:
                features_dict["idx"] = Value("int32")
            dataset = Dataset.from_list(transformed_snippets, features=Features(features_dict))
            dataset.save_to_disk(output_path)
        self.logger.info(f"Processed dataset saved to '{output_path}' with {len(transformed_snippets)} samples in {output_format} format.")

    def _run_transformation(self):
        if not self.dataset_file:
            messagebox.showerror("Error", "Please select a dataset file.")
            return
        if not self.transformations:
            messagebox.showerror("Error", "Please add at least one transformation.")
            return
        if not self.output_entry.get():
            messagebox.showerror("Error", "Please specify an output path.")
            return

        try:
            self.output_path = self.output_entry.get()
            self.code_field = self.code_field_entry.get().strip() or "func"
            self.output_format = self.format_var.get()
            self.selected_fields = [field for field, var in self.field_vars.items() if var.get()]
            if not self.selected_fields:
                messagebox.showerror("Error", "Please select at least one field.")
                return
            if self.code_field not in self.selected_fields:
                self.selected_fields.append(self.code_field)
            self.ist = IST(self.language)
            code_snippets = self._fetch_codexglue_jsonl_dataset(self.dataset_file, self.code_field)
            transformed_snippets = self._transform_dataset(code_snippets, self.transformations, self.code_field)
            self._process_for_training(transformed_snippets, self.output_path, self.output_format)
            messagebox.showinfo("Success", "Transformation completed successfully!")
        except Exception as e:
            messagebox.showerror("Error", f"Transformation failed: {str(e)}")
            self.logger.error(f"Transformation failed: {str(e)}")

def run_gui():
    root = tk.Tk()
    app = CodeTransformerGUI(root)
    root.mainloop()

def run_command_line():
    parser = argparse.ArgumentParser(
        description="Transform JSONL dataset with code transformations.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Usage examples:
  python code_transformer_gui.py --dpath train.jsonl --trans 11.1 9.2
  python code_transformer_gui.py --dpath train.jsonl --trans 11.1 --lang java --fields func,target --output_format csv --verbose

See 'user_manual.md' for detailed instructions.
"""
    )
    parser.add_argument("--dpath", type=str, required=True, help="Path to JSONL dataset file")
    parser.add_argument("--trans", type=str, nargs="+", required=True,
                        help="List of transformation styles (e.g., '11.1 9.2')")
    parser.add_argument("--opath", type=str, help="Path to save processed dataset")
    parser.add_argument("--code_field", type=str, default="func",
                        help="Field containing code (e.g., 'func' or 'code')")
    parser.add_argument("--fields", type=str, nargs="+",
                        help="Fields to retain in output (e.g., 'func target idx')")
    parser.add_argument("--lang", type=str, default="c", choices=["c", "java", "python", "c_sharp"],
                        help="Programming language (default: c)")
    parser.add_argument("--output_format", type=str, default="jsonl", choices=["jsonl", "csv", "dataset"],
                        help="Output format (jsonl, csv, dataset; default: jsonl)")
    parser.add_argument("--verbose", action="store_true",
                        help="Enable verbose logging")
    args = parser.parse_args()

    transformer = CodeTransformerGUI(tk.Tk())
    transformer.dataset_file = args.dpath
    transformer.transformations = args.trans
    transformer.code_field = args.code_field
    transformer.language = args.lang
    transformer.verbose_logging = args.verbose
    transformer.output_format = args.output_format
    transformer.logger.setLevel(logging.DEBUG if args.verbose else logging.INFO)

    # Validate transformations
    supported_styles = transformer.supported_styles
    invalid_styles = [t for t in args.trans if t not in supported_styles]
    if invalid_styles:
        parser.error(f"Invalid transformation styles: {', '.join(invalid_styles)}. Supported: {', '.join(supported_styles)}")

    # Set output path
    if args.opath:
        transformer.output_path = args.opath
    else:
        base_name = os.path.basename(args.dpath)
        name, ext = os.path.splitext(base_name)
        ext = ".jsonl" if args.output_format == "jsonl" else ".csv" if args.output_format == "csv" else ""
        transformer.output_path = os.path.join("dataset", "processed_data", f"{name}_processed{ext}")

    # Set fields
    transformer.fields = []
    with open(args.dpath, "r", encoding="utf-8") as f:
        first_line = f.readline().strip()
        if first_line:
            data = json.loads(first_line)
            transformer.fields = list(data.keys())
    transformer.selected_fields = args.fields if args.fields else transformer.fields
    if transformer.code_field not in transformer.selected_fields:
        transformer.selected_fields.append(transformer.code_field)

    transformer.ist = IST(args.lang)
    code_snippets = transformer._fetch_codexglue_jsonl_dataset(args.dpath, args.code_field)
    transformed_snippets = transformer._transform_dataset(code_snippets, args.trans, args.code_field)
    transformer._process_for_training(transformed_snippets, transformer.output_path, args.output_format)

if __name__ == "__main__":
    if len(sys.argv) > 1:
        run_command_line()
    else:
        run_gui()