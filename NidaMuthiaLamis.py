#!/usr/bin/env python3
# toko_sembako_simple.py — versi lengkap, non-persistent, ID produk, tambah ke keranjang pakai ID/nama, mendukung input singkat "ID qty"

import datetime
import os

# ---------------------------
# Data awal
# ---------------------------
produk_dict = {
    "P001": {"nama": "Beras Pandan Wangi", "merk": "Maknyus", "ukuran": "5 kg", "stok": 10, "harga": 75000},
    "P002": {"nama": "Minyak Goreng", "merk": "Bimoli", "ukuran": "1 liter", "stok": 15, "harga": 20000},
    "P003": {"nama": "Gula Pasir", "merk": "Gulaku", "ukuran": "1 kg", "stok": 12, "harga": 17000},
    "P004": {"nama": "Indomie Goreng", "merk": "Indofood", "ukuran": "1 bungkus", "stok": 50, "harga": 4000},
    "P005": {"nama": "Telur Ayam", "merk": "Segar", "ukuran": "1 kg", "stok": 8, "harga": 28000},
}

keranjang = {}        # { pid: {jumlah,total,nama,merk,ukuran,harga} }
retur_log = []        # list of dict {pid, qty, file}

# ---------------------------
# Utilitas
# ---------------------------
def format_rp(n):
    try:
        return "Rp " + f"{int(n):,}".replace(",", ".")
    except Exception:
        return f"Rp {n}"

def next_product_id():
    nums = [int(k[1:]) for k in produk_dict.keys() if k.startswith("P") and k[1:].isdigit()]
    return f"P{max(nums)+1:03d}" if nums else "P001"

def parse_selection_input(s, max_index):
    s = (s or "").strip().lower()
    if not s:
        return set()
    if s == "all":
        return set(range(1, max_index+1))
    parts = [p.strip() for p in s.split(",") if p.strip()]
    result = set()
    for p in parts:
        if "-" in p:
            try:
                a,b = p.split("-",1)
                i1 = int(a); i2 = int(b)
                if i1 > i2: i1, i2 = i2, i1
                for i in range(i1, i2+1):
                    if 1 <= i <= max_index:
                        result.add(i)
            except Exception:
                continue
        else:
            if p.isdigit():
                i = int(p)
                if 1 <= i <= max_index:
                    result.add(i)
    return result

# ---------------------------
# Pencarian: terima ID (P001) atau nama/partial
# ---------------------------
def cari_produk_by_input(prompt="Masukkan ID atau nama produk: "):
    teks = input(prompt).strip()
    if not teks:
        return None
    t_up = teks.upper()
    # cek langsung ID
    if t_up in produk_dict:
        return t_up
    # cek exact name (case-insensitive)
    for pid, info in produk_dict.items():
        if teks.lower() == info["nama"].lower():
            return pid
    # partial match pada nama
    q = teks.lower()
    matches = [(pid, info) for pid, info in produk_dict.items() if q in info["nama"].lower()]
    if not matches:
        print("Produk tidak ditemukan.")
        return None
    if len(matches) == 1:
        return matches[0][0]
    # banyak hasil -> tampilkan dan minta pilih
    print("Beberapa produk ditemukan:")
    for i, (pid, info) in enumerate(matches, start=1):
        print(f"{i}. {pid} | {info['nama']} | Merk: {info['merk']} | Ukuran: {info['ukuran']} | Stok: {info['stok']}")
    sel = input("Masukkan nomor pilihan (0 untuk batal): ").strip()
    if not sel:
        return None
    if sel.isdigit():
        si = int(sel)
        if si == 0:
            return None
        if 1 <= si <= len(matches):
            return matches[si-1][0]
    print("Pilihan tidak valid.")
    return None

# ---------------------------
# Tampilkan produk
# ---------------------------
def tampilkan_produk():
    print("\nDaftar Produk:")
    print("-" * 100)
    print(f"{'ID':<6} {'Nama':<30} {'Merk':<15} {'Ukuran':<12} {'Stok':<6} {'Harga':>15}")
    print("-" * 100)
    for pid, info in sorted(produk_dict.items()):
        print(f"{pid:<6} {info['nama']:<30} {info['merk']:<15} {info['ukuran']:<12} {info['stok']:<6} {format_rp(info['harga']):>15}")
    print("-" * 100)

# ---------------------------
# Tambah produk
# ---------------------------
def tambah_produk():
    nama = input("Nama produk: ").strip().title()
    if not nama:
        print("Nama tidak boleh kosong.")
        return
    merk = input("Merk: ").strip().title()
    ukuran = input("Ukuran: ").strip()
    try:
        stok = int(input("Stok: ").strip())
        harga = int(input("Harga (Rp): ").strip())
    except Exception:
        print("Stok dan harga harus angka.")
        return
    # cek duplikat exact (nama+merk+ukuran)
    for pid, info in produk_dict.items():
        if info["nama"].lower() == nama.lower() and info["merk"].lower() == merk.lower() and str(info["ukuran"]).lower() == ukuran.lower():
            produk_dict[pid]["stok"] += stok
            produk_dict[pid]["harga"] = harga
            print(f"Produk sama ditemukan ({pid}). Stok ditambah menjadi {produk_dict[pid]['stok']}.")
            return
    pid = next_product_id()
    produk_dict[pid] = {"nama": nama, "merk": merk, "ukuran": ukuran, "stok": stok, "harga": harga}
    print(f"Produk baru ditambahkan dengan ID {pid}.")

# ---------------------------
# Edit produk
# ---------------------------
def edit_produk():
    pid = cari_produk_by_input("Masukkan ID atau nama produk yang ingin diedit: ")
    if not pid:
        print("Produk tidak ditemukan.")
        return
    info = produk_dict[pid]
    print("Kosongkan input jika tidak ingin mengubah field tersebut.")
    nama = input(f"Nama [{info['nama']}]: ").strip().title()
    merk = input(f"Merk [{info['merk']}]: ").strip().title()
    ukuran = input(f"Ukuran [{info['ukuran']}]: ").strip()
    stok_in = input(f"Stok [{info['stok']}]: ").strip()
    harga_in = input(f"Harga [{info['harga']}]: ").strip()
    try:
        stok = int(stok_in) if stok_in else info['stok']
        harga = int(harga_in) if harga_in else info['harga']
    except Exception:
        print("Stok dan harga harus angka.")
        return
    if nama:
        produk_dict[pid]['nama'] = nama
    if merk:
        produk_dict[pid]['merk'] = merk
    if ukuran:
        produk_dict[pid]['ukuran'] = ukuran
    produk_dict[pid]['stok'] = stok
    produk_dict[pid]['harga'] = harga
    print(f"Produk {pid} berhasil diperbarui.")

# ---------------------------
# Tambah stok
# ---------------------------
def tambah_stok_produk():
    pid = cari_produk_by_input("Produk yang ingin ditambah stoknya: ")
    if not pid:
        return
    try:
        tambahan = int(input("Jumlah tambahan: ").strip())
    except Exception:
        print("Input tidak valid.")
        return
    if tambahan <= 0:
        print("Jumlah harus > 0.")
        return
    produk_dict[pid]['stok'] += tambahan
    print(f"Stok {pid} sekarang {produk_dict[pid]['stok']}.")

# ---------------------------
# Tambah ke keranjang (mendukung input singkat "ID qty")
# ---------------------------
def tambah_ke_keranjang():
    """
    Menambah item ke keranjang.
    Mendukung input singkat:
      - "P003 2"  (ID dan qty dipisah spasi)
      - "P003,2"  (ID,qty dipisah koma)
      - "P003:2"  (ID,qty dipisah titik dua)
    Jika user memasukkan hanya ID atau nama, akan ditanya qty secara interaktif.
    Jika partial name menghasilkan banyak hasil, akan diminta memilih.
    """
    raw = input("Masukkan ID atau nama produk (atau 'P003 2' untuk cepat): ").strip()
    if not raw:
        return

    pid_candidate = None
    qty_candidate = None

    # split berdasarkan pemisah umum
    if " " in raw:
        parts = raw.split()
    elif "," in raw:
        parts = raw.split(",")
    elif ":" in raw:
        parts = raw.split(":")
    else:
        parts = [raw]

    if len(parts) >= 2:
        maybe_id = parts[0].strip()
        maybe_qty = parts[1].strip()
        t_up = maybe_id.upper()
        if t_up in produk_dict:
            pid_candidate = t_up
        else:
            # cek exact name
            for pidk, info in produk_dict.items():
                if maybe_id.lower() == info['nama'].lower():
                    pid_candidate = pidk
                    break
            if pid_candidate is None:
                # partial match auto-resolve only if unique
                q = maybe_id.lower()
                matches = [(pidk, info) for pidk, info in produk_dict.items() if q in info['nama'].lower()]
                if len(matches) == 1:
                    pid_candidate = matches[0][0]
                else:
                    pid_candidate = None
        # parse qty
        try:
            qty_candidate = int(maybe_qty)
            if qty_candidate <= 0:
                print("Jumlah harus > 0.")
                return
        except Exception:
            qty_candidate = None

    # jika tidak berhasil parse singkat -> gunakan fungsi pencarian interaktif
    if not pid_candidate:
        pid = cari_produk_by_input("Masukkan ID atau nama produk yang ingin dibeli: ")
    else:
        pid = pid_candidate

    if not pid:
        return

    info = produk_dict[pid]

    # gunakan qty parsed jika ada, jika tidak tanyakan interaktif
    if qty_candidate is not None:
        qty = qty_candidate
    else:
        try:
            qty = int(input(f"Jumlah beli untuk {pid} - {info['nama']}: ").strip())
        except Exception:
            print("Jumlah harus berupa angka.")
            return

    if qty <= 0:
        print("Jumlah harus > 0.")
        return
    if qty > info['stok']:
        print(f"Stok tidak cukup. Tersedia: {info['stok']}")
        return

    subtotal = qty * info['harga']
    if pid in keranjang:
        keranjang[pid]['jumlah'] += qty
        keranjang[pid]['total'] += subtotal
    else:
        keranjang[pid] = {
            'jumlah': qty,
            'total': subtotal,
            'nama': info['nama'],
            'merk': info['merk'],
            'ukuran': info['ukuran'],
            'harga': info['harga'],
        }
    print(f"{qty} x {info['nama']} ({info['merk']}, {info['ukuran']}) ditambahkan ke keranjang. Subtotal {format_rp(subtotal)}.")

# ---------------------------
# Lihat & ubah keranjang
# ---------------------------
def tampilkan_keranjang():
    if not keranjang:
        print("Keranjang kosong.")
        return
    print("\nKeranjang:")
    print("-" * 110)
    print(f"{'ID':<6} {'Nama':<30} {'Merk':<15} {'Ukuran':<12} {'Jumlah':<8} {'Harga':>12} {'Subtotal':>15}")
    print("-" * 110)
    total = 0
    for pid, item in keranjang.items():
        print(f"{pid:<6} {item['nama']:<30} {item['merk']:<15} {item['ukuran']:<12} {item['jumlah']:<8} {format_rp(item['harga']):>12} {format_rp(item['total']):>15}")
        total += item['total']
    print("-" * 110)
    print(f"{'TOTAL':<94}{format_rp(total):>15}")
    print("-" * 110)

def hapus_item_keranjang():
    if not keranjang:
        print("Keranjang kosong.")
        return
    pid = cari_produk_by_input("Masukkan ID atau nama produk yang ingin dihapus dari keranjang: ")
    if not pid or pid not in keranjang:
        print("Produk tidak ada di keranjang.")
        return
    del keranjang[pid]
    print(f"Item {pid} dihapus dari keranjang.")

def ubah_jumlah_keranjang():
    if not keranjang:
        print("Keranjang kosong.")
        return
    pid = cari_produk_by_input("Masukkan ID atau nama produk yang ingin diubah jumlahnya: ")
    if not pid or pid not in keranjang:
        print("Produk tidak ada di keranjang.")
        return
    try:
        new_qty = int(input("Masukkan jumlah baru: ").strip())
    except Exception:
        print("Jumlah harus angka.")
        return
    if new_qty <= 0:
        print("Jumlah harus > 0.")
        return
    if new_qty > produk_dict[pid]['stok']:
        print(f"Stok tidak mencukupi. Tersedia: {produk_dict[pid]['stok']}")
        return
    keranjang[pid]['jumlah'] = new_qty
    keranjang[pid]['total'] = new_qty * keranjang[pid]['harga']
    print(f"Jumlah untuk {pid} diperbarui menjadi {new_qty}.")

# ---------------------------
# Checkout
# ---------------------------
def checkout():
    if not keranjang:
        print("Keranjang kosong.")
        return
    # periksa stok
    for pid, item in keranjang.items():
        if pid not in produk_dict:
            print(f"Error: produk {pid} tidak ditemukan. Batalkan checkout.")
            return
        if item['jumlah'] > produk_dict[pid]['stok']:
            print(f"Stok untuk {pid} tidak mencukupi. Tersedia {produk_dict[pid]['stok']}, diminta {item['jumlah']}")
            return
    total = 0
    for pid, item in keranjang.items():
        produk_dict[pid]['stok'] -= item['jumlah']
        total += item['total']
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    lines = [
        "======= STRUK PEMBELIAN =======",
        f"Tanggal : {now}",
        "",
        f"{'ID':<6} {'Nama':<30} {'Merk':<15} {'Ukuran':<12} {'Jumlah':<8} {'Subtotal':>12}",
        "-" * 90,
    ]
    for pid, item in keranjang.items():
        lines.append(f"{pid:<6} {item['nama']:<30} {item['merk']:<15} {item['ukuran']:<12} {item['jumlah']:<8} {format_rp(item['total']):>12}")
    lines.append("-" * 90)
    lines.append(f"{'TOTAL BELANJA':<70} {format_rp(total):>15}")
    lines.append("Terima kasih telah berbelanja.")
    lines.append("==============================")
    isi = "\n".join(lines)
    print("\n" + isi + "\n")
    fname = f"struk_sembako_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
    try:
        with open(fname, "w", encoding="utf-8") as f:
            f.write(isi)
        print(f"Struk tersimpan: {os.path.abspath(fname)}")
    except Exception as e:
        print("Gagal menyimpan struk:", e)
    keranjang.clear()

# ---------------------------
# Retur barang
# ---------------------------
def retur_barang():
    pid = cari_produk_by_input("Masukkan ID atau nama produk yang diretur: ")
    if not pid:
        return
    try:
        qty = int(input("Jumlah retur: ").strip())
    except Exception:
        print("Jumlah harus angka.")
        return
    if qty <= 0:
        print("Jumlah harus > 0.")
        return
    alasan = input("Alasan retur (opsional): ").strip()
    produk_dict[pid]['stok'] += qty
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    subtotal = qty * produk_dict[pid]['harga']
    lines = [
        "======= STRUK RETUR =======",
        f"Tanggal : {now}",
        "",
        f"ID      : {pid}",
        f"Produk  : {produk_dict[pid]['nama']}",
        f"Merk    : {produk_dict[pid]['merk']}",
        f"Ukuran  : {produk_dict[pid]['ukuran']}",
        f"Jumlah  : {qty}",
        f"Subtotal: {format_rp(subtotal)}",
        "-" * 30,
        f"Alasan  : {alasan if alasan else '-'}",
        "===========================",
    ]
    isi = "\n".join(lines)
    print("\n" + isi + "\n")
    fname = f"retur_sembako_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
    try:
        with open(fname, "w", encoding="utf-8") as f:
            f.write(isi)
        retur_log.append({"pid": pid, "qty": qty, "file": fname})
        print(f"Struk retur tersimpan: {os.path.abspath(fname)}")
    except Exception as e:
        print("Gagal menyimpan struk retur:", e)

# ---------------------------
# Hapus histori retur (mengurangi stok sesuai qty) 
# ---------------------------
def hapus_history_retur():
    if not retur_log:
        print("Belum ada histori retur.")
        return
    print("\nDaftar histori retur:")
    for i, r in enumerate(retur_log, start=1):
        print(f"{i}. {r['pid']} | jumlah {r['qty']} | file: {r['file']}")
    pilih = input("\nMasukkan nomor yang ingin dihapus (contoh: all, 1,1-3): ").strip()
    selected = parse_selection_input(pilih, len(retur_log))
    if not selected:
        print("Tidak ada pilihan valid.")
        return
    # preview
    print("\nPreview pengurangan stok:")
    for i in sorted(selected):
        r = retur_log[i-1]
        stok = produk_dict[r['pid']]['stok']
        new_stok = max(0, stok - r['qty'])
        print(f"- {r['pid']} {produk_dict[r['pid']]['nama']} : {stok} -> {new_stok}")
    konfirm = input("\nKetik 'ya' untuk konfirmasi hapus: ").strip().lower()
    if konfirm != "ya":
        print("Dibatalkan.")
        return
    # apply deletion (reverse retur)
    for i in sorted(selected, reverse=True):
        r = retur_log[i-1]
        produk_dict[r['pid']]['stok'] = max(0, produk_dict[r['pid']]['stok'] - r['qty'])
        try:
            if os.path.exists(r['file']):
                os.remove(r['file'])
        except Exception:
            pass
        del retur_log[i-1]
    print("Histori retur dihapus dan stok diperbarui.")

# ---------------------------
# Menu utama
# ---------------------------
def main():
    while True:
        print("\n=== TOKO SEMBAKO SEDERHANA ===")
        print("1. Lihat produk")
        print("2. Tambah produk")
        print("3. Edit produk")
        print("4. Tambah stok produk")
        print("5. Tambah ke keranjang")
        print("6. Lihat keranjang")
        print("7. Hapus item dari keranjang")
        print("8. Ubah jumlah di keranjang")
        print("9. Checkout ")
        print("10. Retur barang ")
        print("11. Hapus histori retur")
        print("12. Keluar")
        pilih = input("Pilih menu: ").strip()
        if pilih == "1":
            tampilkan_produk()
        elif pilih == "2":
            tambah_produk()
        elif pilih == "3":
            edit_produk()
        elif pilih == "4":
            tambah_stok_produk()
        elif pilih == "5":
            tambah_ke_keranjang()
        elif pilih == "6":
            tampilkan_keranjang()
        elif pilih == "7":
            hapus_item_keranjang()
        elif pilih == "8":
            ubah_jumlah_keranjang()
        elif pilih == "9":
            checkout()
        elif pilih == "10":
            retur_barang()
        elif pilih == "11":
            hapus_history_retur()
        elif pilih == "12":
            print("Terima kasih. Keluar.")
            break
        else:
            print("Pilihan tidak valid.")

if __name__ == "__main__":
    main()