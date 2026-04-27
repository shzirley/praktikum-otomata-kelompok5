# Laporan Praktikum Otomata 2

![](https://github.com/shzirley/praktikum-otomata-kelompok5/blob/cf43e1384e26ad46f09c7040d90b4a50a3290f60/Visual/Screenshot%202026-04-27%20203916.png)

### Tugas
Buatlah program komputer untuk mengotomasi FSM di bawah, yaitu sebuah mesin yang dapat menentukan apakah sebuah string merupakan anggota dari himpunan bahasa $$L = { x ∈ (0 + 1)^+ }$$ dengan karakter terakhir pada string x adalah 1 dan x tidak memiliki substring 00 }. Rancanglah user interface sedemikian hingga pengguna dapat mudah menginputkan string yang akan didentifikasi keanggotaannya.
Komponen penilaian dari tugas ini adalah:
1. Kebenaran algoritma dan output
2. Fitur yang memudahkan pengguna & meningkatkan fleksibilitas program
3. Tidak terindikasi plagiarisme dengan kelompok lain

### Penjelasan 
FSM (Finite State Machine) adalah model komputasi yang berpindah dari satu state ke state lain berdasarkan simbol input. Pada tugas ini, mesin digunakan untuk mengecek keanggotaan string biner terhadap bahasa:

$$L = \{x \in (0+1)^+ \mid \text{karakter terakhir } x \text{ adalah } 1 \text{ dan } x \text{ tidak memiliki substring } 00\}$$

Contoh string yang diterima:

$$L = \{1, 01, 101, 0101, 110101, \dots\}$$

Contoh string yang ditolak:

- `0` (karakter terakhir bukan `1`)
- `10` (karakter terakhir bukan `1`)
- `1001` (mengandung substring `00`)

### Desain State FSM

Program `fsm_visual_gui.py` menggunakan 4 state:

- `S` : start state (belum membaca karakter)
- `A` : karakter terakhir `0` dan belum menemukan `00`
- `B` : karakter terakhir `1` (accept state)
- `C` : dead/trap state (sudah menemukan `00`)

Fungsi transisi yang digunakan:

- `S --0--> A`, `S --1--> B`
- `A --0--> C`, `A --1--> B`
- `B --0--> A`, `B --1--> B`
- `C --0--> C`, `C --1--> C`

String diterima jika dan hanya jika state akhir berada di `B`.

### Implementasi Program (`fsm_visual_gui.py`)

Program dibuat dengan Python dan Tkinter, terdiri dari dua bagian utama:

1. **Logika FSM (`simulate_path`)**
   - Memvalidasi input agar hanya berisi `0` dan `1`.
   - Menjalankan transisi per karakter.
   - Menyimpan jejak langkah (`from_state`, `to_state`, simbol input).
   - Menentukan hasil akhir `accepted` atau `rejected`.

2. **GUI Visual Interaktif (`FSMVisualizerApp`)**
   - Menampilkan diagram FSM dalam canvas (node, panah transisi, self-loop).
   - Menyediakan input string dan tombol simulasi.
   - Menyediakan kontrol animasi `Play/Pause`, `Next`, `Prev`, `Reset`.
   - Menampilkan badge hasil akhir: `DITERIMA` (hijau) atau `DITOLAK` (merah).
   - Menampilkan jejak transisi langkah demi langkah agar proses mudah dipahami.

### Cara Menjalankan

Masuk ke folder `kode`, lalu jalankan:

```bash
python fsm_visual_gui.py
```

Jika Python di Windows terbaca sebagai `py`, bisa gunakan:

```bash
py fsm_visual_gui.py
```

### Hasil Pengujian Singkat

- Input `110101` -> **DITERIMA** (akhir `1` dan tidak ada `00`)
- Input `1001` -> **DITOLAK** (mengandung `00`)
- Input `10` -> **DITOLAK** (akhir `0`)
- Input `1` -> **DITERIMA**

### Kesimpulan

Program `fsm_visual_gui.py` sudah memenuhi kebutuhan tugas praktikum 2 karena:

1. Algoritma FSM sesuai definisi bahasa `L`.
2. Output hasil valid (accept/reject) beserta alasan dan jejak transisi.
3. Antarmuka GUI mempermudah pengguna memahami proses identifikasi keanggotaan string secara visual.









