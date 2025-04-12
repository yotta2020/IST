import os
import sys
import argparse
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import json
import logging
from typing import List
from datasets import Dataset, Features, Value
from transfer import IST  # Assuming IST is your conversion class in transfer.py

class CodeTransformerGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Code Transformer")
        self.root.geometry("700x500")
        self.language = "c"
        self.ist = IST(self.language)
        self.dataset_path = ""
        self.transformations = []
        self.output_path = "processed_dataset"

        # Setup logging for command-line mode
        logging.basicConfig(
            filename="transform.log",
            level=logging.INFO,
            format="%(asctime)s - %(levelname)s - %(message)s"
        )
        self.logger = logging.getLogger()

        # GUI Layout
        self._setup_gui()

    def _setup_gui(self):
        tk.Label(self.root, text="Dataset Path:", font=("Arial", 12)).grid(row=0, column=0, padx=10, pady=10, sticky="w")
        self.path_entry = tk.Entry(self.root, width=60)
        self.path_entry.grid(row=0, column=1, padx=10, pady=10)
        tk.Button(self.root, text="Browse", command=self._browse_dataset).grid(row=0, column=2, padx=10, pady=10)

        tk.Label(self.root, text="Transformations (e.g., 11.1 for while->for):", font=("Arial", 12)).grid(row=1, column=0, padx=10, pady=10, sticky="w")
        self.transform_listbox = tk.Listbox(self.root, height=10, width=60)
        self.transform_listbox.grid(row=1, column=1, padx=10, pady=10)

        frame = tk.Frame(self.root)
        frame.grid(row=2, column=1, padx=10, pady=5)
        tk.Label(frame, text="Add Style:").pack(side=tk.LEFT)
        self.style_entry = tk.Entry(frame, width=20)
        self.style_entry.pack(side=tk.LEFT, padx=5)
        tk.Button(frame, text="Add", command=self._add_transformation).pack(side=tk.LEFT, padx=5)
        tk.Button(frame, text="Delete", command=self._delete_transformation).pack(side=tk.LEFT, padx=5)

        tk.Label(self.root, text="Output Path:", font=("Arial", 12)).grid(row=3, column=0, padx=10, pady=10, sticky="w")
        self.output_entry = tk.Entry(self.root, width=60)
        self.output_entry.insert(0, self.output_path)
        self.output_entry.grid(row=3, column=1, padx=10, pady=10)
        tk.Button(self.root, text="Browse", command=self._browse_output).grid(row=3, column=2, padx=10, pady=10)

        tk.Button(self.root, text="Run Transformation", font=("Arial", 12), command=self._run_transformation).grid(row=4, column=1, padx=10, pady=20)

    def _browse_dataset(self):
        self.dataset_path = filedialog.askdirectory(title="Select Dataset Directory")
        if self.dataset_path:
            self.path_entry.delete(0, tk.END)
            self.path_entry.insert(0, self.dataset_path)

    def _browse_output(self):
        output_dir = filedialog.askdirectory(title="Select Output Directory")
        if output_dir:
            self.output_entry.delete(0, tk.END)
            self.output_entry.insert(0, output_dir)
            self.output_path = output_dir

    def _add_transformation(self):
        style = self.style_entry.get().strip()
        if style:
            self.transformations.append(style)
            self.transform_listbox.insert(tk.END, style)
            self.style_entry.delete(0, tk.END)
        else:
            messagebox.showwarning("Input Error", "Please enter a transformation style (e.g., 11.1).")

    def _delete_transformation(self):
        selection = self.transform_listbox.curselection()
        if selection:
            idx = selection[0]
            self.transform_listbox.delete(idx)
            self.transformations.pop(idx)
        else:
            messagebox.showwarning("Selection Error", "Please select a transformation to delete.")

    def _fetch_codexglue_jsonl_dataset(self, dataset_path: str) -> List[dict]:
        if not os.path.exists(dataset_path):
            raise FileNotFoundError(f"Dataset path '{dataset_path}' does not exist.")
        
        code_snippets = []
        for filename in os.listdir(dataset_path):
            if filename.endswith(".jsonl"):
                with open(os.path.join(dataset_path, filename), "r", encoding="utf-8") as f:
                    for line in f:
                        try:
                            data = json.loads(line.strip())
                            if "func" in data and data["func"].strip():
                                code_snippets.append(data)
                        except json.JSONDecodeError:
                            self.logger.warning(f"Skipping invalid JSONL line in {filename}")
        self.logger.info(f"Loaded {len(code_snippets)} functions from '{dataset_path}'.")
        print(f"Loaded {len(code_snippets)} functions.")
        return code_snippets

    def _transform_dataset(self, code_snippets: List[dict], transformations: List[str]) -> List[dict]:
        transformed_snippets = code_snippets.copy()
        total_converted = 0

        for style in transformations:
            current_snippets = []
            converted_count = 0

            for i, item in enumerate(transformed_snippets):
                code = item["func"]
                if not code.strip():
                    current_snippets.append(item)
                    continue
                style_count = self.ist.get_style(code=code, styles=[style]).get(style, 0)
                if style_count > 0:
                    new_code, success = self.ist.transfer(styles=[style], code=code)
                    if success:
                        new_item = item.copy()
                        new_item["func"] = new_code
                        current_snippets.append(new_item)
                        converted_count += 1
                        self.logger.info(f"Function {i + 1} (idx: {item['idx']}): Applied {style} successfully")
                    else:
                        current_snippets.append(item)
                        self.logger.warning(f"Function {i + 1} (idx: {item['idx']}): Failed to apply {style}")
                else:
                    current_snippets.append(item)
                    self.logger.info(f"Function {i + 1} (idx: {item['idx']}): No {style} found")

            transformed_snippets = current_snippets
            total_converted += converted_count

        print(f"Dataset saved to: {self.output_path}")
        print(f"Total functions converted: {total_converted}")
        print(f"Transformation types applied: {', '.join(transformations)}")
        
        return transformed_snippets

    def _process_for_training(self, transformed_snippets: List[dict], output_path: str) -> Dataset:
        features = Features({
            "project":Value("string"),
            "commit_id":Value("string"),
            "func": Value("string"),
            "target": Value("int32"),
            "idx": Value("int32")
        })
        dataset = Dataset.from_list(transformed_snippets, features=features)
        
        if not os.path.exists(output_path):
            os.makedirs(output_path)
        dataset.save_to_disk(output_path)
        self.logger.info(f"Processed dataset saved to '{output_path}' with {len(dataset)} samples.")
        return dataset

    def _run_transformation(self):
        if not self.dataset_path:
            messagebox.showerror("Error", "Please select a dataset path.")
            return
        if not self.transformations:
            messagebox.showerror("Error", "Please add at least one transformation.")
            return

        try:
            code_snippets = self._fetch_codexglue_jsonl_dataset(self.dataset_path)
            transformed_snippets = self._transform_dataset(code_snippets, self.transformations)
            self._process_for_training(transformed_snippets, self.output_path)
            messagebox.showinfo("Success", "Transformation completed successfully!")
            # print(transformed_snippets[0])
            # print(code_snippets[0])

        except Exception as e:
            messagebox.showerror("Error", f"Transformation failed: {str(e)}")
            self.logger.error(f"Transformation failed: {str(e)}")

def run_gui():
    root = tk.Tk()
    app = CodeTransformerGUI(root)
    root.mainloop()

def run_command_line():
    parser = argparse.ArgumentParser(description="Transform CodeXGLUE JSONL dataset via command line.")
    parser.add_argument("--dpath", type=str, required=True, help="Path to local JSONL dataset directory")
    parser.add_argument("--trans", type=str, nargs="+", required=True,
                        help="List of transformation styles (e.g., '11.1 9.2')")
    parser.add_argument("--opath", type=str, default="processed_dataset",
                        help="Path to save processed dataset (default: processed_dataset)")
    args = parser.parse_args()

    transformer = CodeTransformerGUI(tk.Tk())
    transformer.dataset_path = args.dpath
    transformer.output_path = args.opath
    transformer.transformations = args.trans

    code_snippets = transformer._fetch_codexglue_jsonl_dataset(args.dpath)
    transformed_snippets = transformer._transform_dataset(code_snippets, args.trans)
    transformer._process_for_training(transformed_snippets, args.opath)

if __name__ == "__main__":
    if len(sys.argv) > 1:
        run_command_line()
    else:
        run_gui()