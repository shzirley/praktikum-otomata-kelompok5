# Laporan Praktikum Otomata 2

![](https://github.com/shzirley/praktikum-otomata-kelompok5/blob/cf43e1384e26ad46f09c7040d90b4a50a3290f60/Visual/Screenshot%202026-04-27%20203916.png)

### Tugas
Buatlah program komputer untuk mengotomasi FSM di bawah, yaitu sebuah mesin yang dapat menentukan apakah sebuah string merupakan anggota dari himpunan bahasa $$L = { x ∈ (0 + 1)^+ }$$ dengan karakter terakhir pada string x adalah 1 dan x tidak memiliki substring 00 }. Rancanglah user interface sedemikian hingga pengguna dapat mudah menginputkan string yang akan didentifikasi keanggotaannya.
Komponen penilaian dari tugas ini adalah:
1. Kebenaran algoritma dan output
2. Fitur yang memudahkan pengguna & meningkatkan fleksibilitas program
3. Tidak terindikasi plagiarisme dengan kelompok lain

### Penjelasan 
FSM (Finite State Machine) adalah sebuah model matematika abstrak yang digunakan untuk merancang logika komputer atau program. Model ini hanya bisa berada di satu keadaan (state) pada satu waktu, dan dia akan berpindah ke keadaan lain jika menerima input (masukan) tertentu. 
Syarat yang ada pada soal yaitu 
$$L = { x ∈ (0 + 1)^+}$$ dan tidak memiliki substring 00. maka himpunan yang memenuhi L yaitu :

L = { 1, 01, 101, 0101, 010101, ...}
tidak diakhiri 0 dan tidak ada substring 00 pada himpunan. 









