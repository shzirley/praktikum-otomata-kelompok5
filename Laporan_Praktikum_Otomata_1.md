# Laporan Praktikum #1

## Soal
Buatlah program computer yang dapat membaca inputan berupa program computer lain, dan dapat menghasilkan output berupa token-token (string-string yang terbaca) dan mengelompokkannya sesuai dengan sifat string tersebut:
**- Reserve words
- Simbol dan tanda baca
- Variabel
- Kalimat matematika (persamaan, fungsi, dsb)**

Rancanglah user interface sedemikian hingga pengguna dapat mudah menginputkan sebuah programyang akan dicari token2nya.


## Penjelasan Kode

```python
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
```
Bagian ini mendefinisikan aturan-aturan dasar menggunakan Regular Expressions (Regex) untuk mengenali kategori token sesuai dengan teori otomata dan grammar.

| Variabel / Pola | Penjelasan | Dasar Teori Grammar |
| :--- | :--- | :--- |
| **`RESERVED_WORDS`** | Himpunan kata kunci tetap yang memiliki fungsi khusus (seperti `if`, `int`, `print`). | Merupakan bagian dari himpunan simbol terminal ($V_T$). |
| **`SYMBOL_PATTERN`** | Mendeteksi operator aritmatika, logika, dan tanda baca seperti `==`, `+`, atau `;`. | Simbol terminal yang mendefinisikan struktur sintaksis. |
| **`IDENTIFIER_PATTERN`**| Aturan penamaan variabel: dimulai dengan huruf/garis bawah, diikuti alfanumerik. | Mengikuti aturan derivasi identifier $I \rightarrow L \| IL \| ID$. |
| **`MATH_EXPRESSION_PATTERN`** | Mendeteksi satu baris persamaan utuh (LHS = RHS) termasuk penugasan nilai. | Implementasi aturan produksi $E, T, F$ untuk ekspresi matematis. |
| **`CONDITION_STATEMENT_PATTERN`** | Mengenali struktur kontrol aliran program seperti `if` dan `while`. | Bagian dari aturan pembentukan kalimat dalam grammar. |
| **`COMPARISON_EXPRESSION`** | Mendeteksi operasi perbandingan logika antara dua operand (seperti `a > b`). | Penggunaan operator relasional dalam evaluasi logika. |

Blok kode ini berfungsi sebagai "penerjemah" aturan grammar formal ke dalam logika program. Hal ini memungkinkan sistem untuk membedakan antara **token tunggal** (seperti variabel) dan **kalimat utuh** (seperti persamaan matematika) guna memenuhi kriteria penilaian kebenaran algoritma.

---

```python
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
```
Function ini berfungsi untuk:
- **Pembersihan**: Menghapus komentar (// atau #) dari setiap baris agar tidak diproses sebagai kode.
- **Ekstraksi**: Memecah teks menjadi unit-unit kecil (token) seperti variabel, angka, dan operator menggunakan pola Regex.
- **Prioritas**: Mencari operator panjang (seperti == atau !=) terlebih dahulu sebelum simbol tunggal agar pemotongan karakter akurat.
- **Output**: Mengembalikan daftar string token yang siap dikelompokkan ke kategori Reserve Words, Variables, atau Math Expressions.

---

```python
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
```

Fungsi ini merupakan pusat logika yang mengorganisir hasil pindaian teks ke dalam kategori-kategori bermakna sesuai dengan tujuan praktikum. Berikut adalah penjelasan alur kerja:

- Fungsi pertama kali memanggil `tokenize_source(source_text)` untuk memecah teks input menjadi daftar token mentah yang siap untuk diolah lebih lanjut.
- Menyiapkan wadah berupa *list* untuk menampung hasil kategori *reserved*, *symbols*, *variables*, dan *expressions*, serta menggunakan *set* untuk memastikan tidak ada data duplikat dalam hasil akhir.
- Melakukan pengecekan pada setiap token untuk menentukan apakah termasuk dalam `RESERVED_WORDS`, yang merupakan kata-kata kunci tetap yang memiliki fungsi khusus dalam bahasa pemrograman.
- Mencocokkan setiap token dengan `SYMBOL_PATTERN` untuk mengidentifikasi operator aritmatika, operator logika, dan tanda baca seperti titik koma atau tanda kurung.
- Memvalidasi token sebagai variabel menggunakan `IDENTIFIER_PATTERN` dengan memastikan token tersebut bukan merupakan kata kunci dan belum pernah terdeteksi sebelumnya.
- Menyisir kembali kode sumber baris demi baris menggunakan `MATH_EXPRESSION_PATTERN` untuk mendeteksi kalimat matematika atau persamaan utuh.
- Mendeteksi pernyataan kondisi menggunakan `CONDITION_STATEMENT_PATTERN` guna mengenali struktur logika yang terdapat di dalam perintah kontrol aliran seperti `if` atau `while`.
- Mengidentifikasi ekspresi perbandingan melalui `COMPARISON_EXPRESSION_PATTERN` untuk membedah hubungan antara dua operand yang dihubungkan oleh operator relasional.
- Melakukan normalisasi pada setiap ekspresi yang ditemukan agar format penulisannya seragam dan konsisten sebelum disimpan ke dalam daftar hasil.
- Mengembalikan seluruh data yang telah terklasifikasi dalam bentuk *dictionary*, sehingga memudahkan bagian antarmuka (UI) untuk menampilkan setiap kelompok token secara terorganisir.

---

```python
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

class ModernTokenizerApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Praktikum 1 - Program Tokenizer (Modern UI)")
        self.geometry("1100x750")

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        self.header_label = ctk.CTkLabel(
            self, text="TOKEN CLASSIFIER PRO", 
            font=ctk.CTkFont(size=22, weight="bold")
        )
        self.header_label.grid(row=0, column=0, pady=(20, 10))

        self.pane = ctk.CTkFrame(self, fg_color="transparent")
        self.pane.grid(row=1, column=0, sticky="nsew", padx=20, pady=10)
        self.pane.grid_columnconfigure(0, weight=1)
        self.pane.grid_columnconfigure(1, weight=1)
        self.pane.grid_rowconfigure(1, weight=1)

        ctk.CTkLabel(self.pane, text="Input Program:", font=ctk.CTkFont(weight="bold")).grid(row=0, column=0, sticky="w", pady=(0,5))
        self.input_text = ctk.CTkTextbox(self.pane, font=("Consolas", 13))
        self.input_text.grid(row=1, column=0, sticky="nsew", padx=(0, 10))

        ctk.CTkLabel(self.pane, text="Hasil Klasifikasi:", font=ctk.CTkFont(weight="bold")).grid(row=0, column=1, sticky="w", pady=(0,5))
        self.output_text = ctk.CTkTextbox(self.pane, font=("Consolas", 13), fg_color="#1E1E1E")
        self.output_text.grid(row=1, column=1, sticky="nsew")

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
        sample_program = """
        int total = a + b * 3;
if (total > 10) {
    print(total);
}
f(x) = x^2 + 2*x + 1
"""
        self.input_text.delete("1.0", "end")
        self.input_text.insert("1.0", sample_program)
        self.analyze()
```

Blok kode ini berfungsi untuk membangun antarmuka pengguna (GUI) modern menggunakan library `customtkinter`. Di dalamnya diatur tata letak kotak input untuk kode sumber, area tampilan hasil klasifikasi, serta tombol interaktif untuk menjalankan proses analisis dan manajemen data token secara praktis.
