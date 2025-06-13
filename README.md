# Discord Bot + Local API Integration

Bot Discord dengan GTP4ALL

---

## 📦 Fitur

- Command prefix `!` (contoh: `!ping`, `!tanya`)
- Slash command (contoh: `/ping`, `/tanya`)
- Mendukung API lokal berbasis GPT4ALL.
- Menggunakan file `token.txt` untuk menyimpan token Discord.

---

## 📂 Struktur File

```bash
.
├── bot.py          # File utama bot
├── token.txt       # File berisi token bot Discord (hanya token, tanpa spasi)
├── README.md       # Dokumentasi proyek
````

---

## ⚙️ Persyaratan

* Python 3.8+
* Dependensi:

  * `discord.py`
  * `aiohttp`

### Install Dependensi

```bash
pip install discord.py aiohttp
```

---

## 🚀 Cara Menjalankan

1️⃣ Siapkan file `token.txt`
Isi dengan token bot Discord kamu. Contoh isi file:

```
MTEyMzQ1Njc4OTAxMjM0NTY3ODkw.YXcD0A.AbcdEfghIjklMnopQrstUvwxYz
```

2️⃣ Pastikan API lokal sudah berjalan di `http://localhost:4891/v1/chat/completions`.

3️⃣ Jalankan bot:

```bash
python bot.py
```

---

## 💬 Perintah Bot

### Command Prefix (`!`)

* `!ping` — Menguji koneksi ke API lokal.
* `!tanya <pertanyaan>` — Mengirim pertanyaan ke API lokal.

### Slash Command

* `/ping` — Menguji koneksi ke API lokal.
* `/tanya <pertanyaan>` — Mengirim pertanyaan ke API lokal.
