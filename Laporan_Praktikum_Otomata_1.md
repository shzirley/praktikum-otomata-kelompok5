# Kode

```python
import re
import tkinter as tk
import customtkinter as ctk

# ==========================================================
# LOGIKA ORIGINAL KAMU (TIDAK DISENTUH SAMA SEKALI)
# ==========================================================
RESERVED_WORDS = {
    "if", "else", "for", "while", "do", "switch", "case", "break", 
    "continue", "return", "int", "float", "double", "char", "bool", 
    "void", "string", "class", "public", "private", "protected", 
    "static", "import", "from", "def", "print", "function", "var", 
    "let", "const", "true", "false", "null",
}

SYMBOL_PATTERN = re.compile(
    r"(==|!=|<=|>=|\+\+|--|\+=|-=|\*=|/=|&&|\|\||//|\*\*|[+\-*/%=<>{}()[\];:,.])"
)
IDENTIFIER_PATTERN = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")
MATH_EXPRESSION_PATTERN = re.compile(
    r"^\s*(?:(int|float|double|char|bool|string|long|short)\s+)?([A-Za-z_][A-Za-z0-9_]*)(\([^)]*\))?\s*=\s*([A-Za-z0-9_().+\-*/%^,<>=!\s]+?)\s*;?\s*$"
)
CONDITION_STATEMENT_PATTERN = re.compile(r"^\s*(if|while)\s*\((.+)\)\s*[{;]?\s*$")
RELATIONAL_OPERATOR_PATTERN = re.compile(r"(==|!=|<=|>=|<|>)")
COMPARISON_EXPRESSION_PATTERN = re.compile(
    r"^\s*([A-Za-z_][A-Za-z0-9_]*|\d+(?:\.\d+)?)\s*(==|!=|<=|>=|<|>)\s*([A-Za-z_][A-Za-z0-9_]*|\d+(?:\.\d+)?)\s*;?\s*$"
)

def tokenize_source(source_text: str):
    cleaned_lines = []
    for line in source_text.splitlines():
        line = re.sub(r"//.*$", "", line)
        line = re.sub(r"#.*$", "", line)
        cleaned_lines.append(line)
    cleaned_text = "\n".join(cleaned_lines)

    tokens = re.findall(
        r"==|!=|<=|>=|\+\+|--|\+=|-=|\*=|/=|&&|\|\||//|\*\*|[A-Za-z_][A-Za-z0-9_]*|\d+(?:\.\d+)?|[+\-*/%=<>{}()[\];:,.]",
        cleaned_text,
    )
    return tokens

def classify_tokens(source_text: str):
    tokens = tokenize_source(source_text)
    reserved, symbols, variables = [], [], []
    variables_seen = set()
    expressions, expressions_seen = [], set()

    for token in tokens:
        if token in RESERVED_WORDS:
            reserved.append(token)
        elif SYMBOL_PATTERN.match(token):
            symbols.append(token)
        elif IDENTIFIER_PATTERN.match(token):
            if token not in RESERVED_WORDS and token not in variables_seen:
                variables.append(token)
                variables_seen.add(token)

    for line in source_text.splitlines():
        stripped = line.strip()
        if not stripped: continue
        
        expression_match = MATH_EXPRESSION_PATTERN.match(stripped)
        if expression_match:
            declared_type = expression_match.group(1)
            lhs_name = expression_match.group(2)
            function_part = expression_match.group(3) or ""
            rhs_expression = expression_match.group(4).strip()
            if declared_type is None and lhs_name in RESERVED_WORDS: continue
            normalized_expression = f"{lhs_name}{function_part} = {rhs_expression}"
            if normalized_expression not in expressions_seen:
                expressions.append(normalized_expression)
                expressions_seen.add(normalized_expression)
            continue

        condition_match = CONDITION_STATEMENT_PATTERN.match(stripped)
        if condition_match:
            condition_expression = condition_match.group(2).strip()
            if RELATIONAL_OPERATOR_PATTERN.search(condition_expression):
                if condition_expression not in expressions_seen:
                    expressions.append(condition_expression)
                    expressions_seen.add(condition_expression)
            continue

        comparison_match = COMPARISON_EXPRESSION_PATTERN.match(stripped)
        if comparison_match:
            left_part = comparison_match.group(1)
            operator_part = comparison_match.group(2)
            right_part = comparison_match.group(3)
            normalized_comparison = f"{left_part} {operator_part} {right_part}"
            if normalized_comparison not in expressions_seen:
                expressions.append(normalized_comparison)
                expressions_seen.add(normalized_comparison)

    return {
        "reserved": reserved, "symbols": symbols, "variables": variables,
        "expressions": expressions, "all_tokens": tokens,
    }

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

class ModernTokenizerApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Praktikum 1 - Program Tokenizer (Modern UI)")
        self.geometry("1100x750")

        # Layout Configuration
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        # Header
        self.header_label = ctk.CTkLabel(
            self, text="TOKEN CLASSIFIER PRO", 
            font=ctk.CTkFont(size=22, weight="bold")
        )
        self.header_label.grid(row=0, column=0, pady=(20, 10))

        # Main Split Container
        self.pane = ctk.CTkFrame(self, fg_color="transparent")
        self.pane.grid(row=1, column=0, sticky="nsew", padx=20, pady=10)
        self.pane.grid_columnconfigure(0, weight=1)
        self.pane.grid_columnconfigure(1, weight=1)
        self.pane.grid_rowconfigure(1, weight=1)

        # --- Input Section ---
        ctk.CTkLabel(self.pane, text="Input Program:", font=ctk.CTkFont(weight="bold")).grid(row=0, column=0, sticky="w", pady=(0,5))
        self.input_text = ctk.CTkTextbox(self.pane, font=("Consolas", 13))
        self.input_text.grid(row=1, column=0, sticky="nsew", padx=(0, 10))

        # --- Output Section ---
        ctk.CTkLabel(self.pane, text="Hasil Klasifikasi:", font=ctk.CTkFont(weight="bold")).grid(row=0, column=1, sticky="w", pady=(0,5))
        self.output_text = ctk.CTkTextbox(self.pane, font=("Consolas", 13), fg_color="#1E1E1E")
        self.output_text.grid(row=1, column=1, sticky="nsew")

        # Button Group
        self.button_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.button_frame.grid(row=2, column=0, pady=20)

        self.btn_analyze = ctk.CTkButton(self.button_frame, text="ANALYZE TOKENS", command=self.analyze, width=160, height=40, font=ctk.CTkFont(weight="bold"))
        self.btn_analyze.pack(side="left", padx=10)

        self.btn_sample = ctk.CTkButton(self.button_frame, text="LOAD SAMPLE", command=self.load_sample, width=160, height=40, fg_color="gray")
        self.btn_sample.pack(side="left", padx=10)

        self.btn_clear = ctk.CTkButton(self.button_frame, text="CLEAR", command=self.clear_all, width=160, height=40, fg_color="#D32F2F", hover_color="#B71C1C")
        self.btn_clear.pack(side="left", padx=10)

    def analyze(self):
        source = self.input_text.get("1.0", "end").strip()
        if not source:
            self.update_output("Masukkan program terlebih dahulu.")
            return

        result = classify_tokens(source)
        self.output_text.delete("1.0", "end")

        # Menampilkan hasil sesuai kategori tugas 
        self._append_section("1) Reserve Words", result["reserved"])
        self._append_section("2) Simbol & Tanda Baca", result["symbols"])
        self._append_section("3) Variabel (Identifier)", result["variables"])
        self._append_section("4) Kalimat Matematika", result["expressions"])
        self._append_section("--- Semua Token Terbaca ---", result["all_tokens"])

    def _append_section(self, title, data):
        self.output_text.insert("end", f"{title}\n", "header")
        if data:
            for idx, item in enumerate(data, start=1):
                self.output_text.insert("end", f"  {idx}. {item}\n")
        else:
            self.output_text.insert("end", "  (Kosong)\n")
        self.output_text.insert("end", "\n")

    def update_output(self, message):
        self.output_text.delete("1.0", "end")
        self.output_text.insert("1.0", message)

    def clear_all(self):
        self.input_text.delete("1.0", "end")
        self.output_text.delete("1.0", "end")

    def load_sample(self):
        sample_program = """int total = a + b * 3;
if (total > 10) {
    print(total);
}
f(x) = x^2 + 2*x + 1"""
        self.input_text.delete("1.0", "end")
        self.input_text.insert("1.0", sample_program)
        self.analyze()

if __name__ == "__main__":
    app = ModernTokenizerApp()
    app.mainloop()
```
