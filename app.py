from datetime import date, timedelta
import sqlite3
from fpdf import FPDF
import pandas as pd
import streamlit as st

# ==========================================
# 1. KONFIGURASI HALAMAN STREAMLIT
# ==========================================
st.set_page_config(
    page_title="Sistem Rekap Toko & Penggajian",
    page_icon="🏪",
    layout="wide",
    initial_sidebar_state="expanded",
)


# ==========================================
# 2. INISIALISASI DATABASE SQLITE
# ==========================================
def get_connection():
  conn = sqlite3.connect("toko.db", check_same_thread=False)
  return conn


def init_db():
  conn = get_connection()
  c = conn.cursor()

  # Tabel Akun Pengguna
  c.execute("""
        CREATE TABLE IF NOT EXISTS users (
            username TEXT PRIMARY KEY,
            password TEXT NOT NULL,
            role TEXT NOT NULL,
            nama TEXT NOT NULL
        )
    """)

  # Tabel Penjualan Harian
  c.execute("""
        CREATE TABLE IF NOT EXISTS penjualan (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            tanggal DATE NOT NULL,
            jumlah REAL NOT NULL,
            keterangan TEXT,
            input_by TEXT
        )
    """)

  # Tabel Pengeluaran Operasional
  c.execute("""
        CREATE TABLE IF NOT EXISTS pengeluaran (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            tanggal DATE NOT NULL,
            nama_item TEXT NOT NULL,
            jumlah REAL NOT NULL,
            input_by TEXT
        )
    """)

  # Tabel Riwayat Slip Gaji (Tabel Baru)
  c.execute("""
        CREATE TABLE IF NOT EXISTS riwayat_gaji (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            tanggal_simpan DATE NOT NULL,
            nama_karyawan TEXT NOT NULL,
            tgl_mulai DATE NOT NULL,
            tgl_selesai DATE NOT NULL,
            gaji_per_hari REAL NOT NULL,
            jumlah_hari INTEGER NOT NULL,
            total_gaji_pokok REAL NOT NULL,
            persen_bonus REAL NOT NULL,
            omset_periode REAL NOT NULL,
            total_bonus REAL NOT NULL,
            grand_total REAL NOT NULL
        )
    """)

  # Akun Default
  c.execute("SELECT COUNT(*) FROM users")
  if c.fetchone()[0] == 0:
    c.execute(
        "INSERT INTO users VALUES ('admin', 'admin123', 'admin', 'Owner Toko')"
    )
    c.execute(
        "INSERT INTO users VALUES ('karyawan', 'karyawan123', 'karyawan', 'Staf"
        " Kasir')"
    )

  conn.commit()
  conn.close()


init_db()


# ==========================================
# 3. FUNGSI GENERATE PDF SLIP GAJI (UKURAN A6)
# ==========================================
def generate_pdf_slip(
    nama,
    tgl_mulai,
    tgl_selesai,
    gaji_harian,
    hari_kerja,
    total_pokok,
    persen_bonus,
    omset,
    total_bonus,
    grand_total,
):
  # Ukuran A6: 105 mm x 148 mm (Sesuai Standar Cetak Thermal / Portable)
  pdf = FPDF(orientation="P", unit="mm", format=(105, 148))
  pdf.set_margins(8, 8, 8)
  pdf.add_page()

  # Header Toko
  pdf.set_font("Helvetica", "B", 12)
  pdf.cell(0, 6, "SLIP GAJI KARYAWAN", ln=1, align="C")
  pdf.set_font("Helvetica", "", 8)
def generate_pdf_slip(
    nama,
    tgl_mulai,
    tgl_selesai,
    gaji_harian,
    hari_kerja,
    total_pokok,
    persen_bonus,
    omset,
    total_bonus,
    grand_total,
):
  # Ukuran A6: 105 mm x 148 mm (Sesuai Standar Cetak Thermal / Portable)
  pdf = FPDF(orientation="P", unit="mm", format=(105, 148))
  pdf.set_margins(8, 8, 8)
  pdf.add_page()

  # Header Toko
  pdf.set_font("Helvetica", "B", 12)
  pdf.cell(0, 6, "SLIP GAJI KARYAWAN", ln=1, align="C")
  pdf.set_font("Helvetica", "", 8)
def generate_pdf_slip(
    nama,
    tgl_mulai,
    tgl_selesai,
    gaji_harian,
    hari_kerja,
    total_pokok,
    persen_bonus,
    omset,
    total_bonus,
    grand_total,
):
  # Ukuran A6: 105 mm x 148 mm (Sesuai Standar Cetak Thermal / Portable)
  pdf = FPDF(orientation="P", unit="mm", format=(105, 148))
  pdf.set_margins(8, 8, 8)
  pdf.add_page()

  # Header Toko
  pdf.set_font("Helvetica", "B", 12)
  pdf.cell(0, 6, "SLIP GAJI KARYAWAN", ln=1, align="C")
  pdf.set_font("Helvetica", "", 8)
def generate_pdf_slip(
    nama,
    tgl_mulai,
    tgl_selesai,
    gaji_harian,
    hari_kerja,
    total_pokok,
    persen_bonus,
    omset,
    total_bonus,
    grand_total,
):
  # Ukuran A6: 105 mm x 148 mm (Sesuai Standar Cetak Thermal / Portable)
  pdf = FPDF(orientation="P", unit="mm", format=(105, 148))
  pdf.set_margins(8, 8, 8)
  pdf.add_page()

  # Header Toko
  pdf.set_font("Helvetica", "B", 12)
  pdf.cell(0, 6, "SLIP GAJI KARYAWAN", ln=1, align="C")
  pdf.set_font("Helvetica", "", 8)
def generate_pdf_slip(
    nama,
    tgl_mulai,
    tgl_selesai,
    gaji_harian,
    hari_kerja,
    total_pokok,
    persen_bonus,
    omset,
    total_bonus,
    grand_total,
):
  # Ukuran A6: 105 mm x 148 mm (Sesuai Standar Cetak Thermal / Portable)
  pdf = FPDF(orientation="P", unit="mm", format=(105, 148))
  pdf.set_margins(8, 8, 8)
  pdf.add_page()

  # Header Toko
  pdf.set_font("Helvetica", "B", 12)
  pdf.cell(0, 6, "SLIP GAJI KARYAWAN", ln=1, align="C")
  pdf.set_font("Helvetica", "", 8)
def generate_pdf_slip(
    nama,
    tgl_mulai,
    tgl_selesai,
    gaji_harian,
    hari_kerja,
    total_pokok,
    persen_bonus,
    omset,
    total_bonus,
    grand_total,
):
  # Ukuran A6: 105 mm x 148 mm (Sesuai Standar Cetak Thermal / Portable)
  pdf = FPDF(orientation="P", unit="mm", format=(105, 148))
  pdf.set_margins(8, 8, 8)
  pdf.add_page()

  # Header Toko
  pdf.set_font("Helvetica", "B", 12)
  pdf.cell(0, 6, "SLIP GAJI KARYAWAN", ln=1, align="C")
  pdf.set_font("Helvetica", "", 8)
def generate_pdf_slip(
    nama,
    tgl_mulai,
    tgl_selesai,
    gaji_harian,
    hari_kerja,
    total_pokok,
    persen_bonus,
    omset,
    total_bonus,
    grand_total,
):
  # Format A6 didefinisikan langsung dengan tuple (105 mm x 148 mm)
  pdf = FPDF(orientation="P", unit="mm", format=(105, 148))
  pdf.set_margins(8, 8, 8)
  pdf.add_page()

  # Header Toko
  pdf.set_font("Helvetica", "B", 12)
  pdf.cell(0, 6, "SLIP GAJI KARYAWAN", ln=1, align="C")
  pdf.set_font("Helvetica", "", 8)
  pdf.cell(0, 4, "REKAP TOKO OPERASIONAL", ln=1, align="C")
  pdf.line(8, pdf.get_y() + 1, 97, pdf.get_y() + 1)
  pdf.ln(3)

  # Data Karyawan & Periode
  pdf.set_font("Helvetica", "", 8)
  pdf.cell(28, 4, "Nama Karyawan", ln=0)
  pdf.cell(0, 4, f": {nama}", ln=1)
  pdf.cell(28, 4, "Periode Kerja", ln=0)
  pdf.cell(0, 4, f": {tgl_mulai} s/d {tgl_selesai}", ln=1)
  pdf.ln(2)
  pdf.line(8, pdf.get_y(), 97, pdf.get_y())
  pdf.ln(2)

  # Rincian Penghitungan Gaji
  pdf.set_font("Helvetica", "B", 8)
  pdf.cell(0, 4, "RINCIAN PEMBAYARAN", ln=1)
  pdf.set_font("Helvetica", "", 8)

  # 1. Gaji Pokok
  pdf.cell(
      52, 4, f"Gaji Pokok ({hari_kerja} hr x Rp {gaji_harian:,.0f})", ln=0
  )
  pdf.cell(0, 4, f"Rp {total_pokok:,.0f}", ln=1, align="R")

  # 2. Bonus Omset
  pdf.cell(52, 4, f"Bonus Omset ({persen_bonus}% x Rp {omset:,.0f})", ln=0)
  pdf.cell(0, 4, f"Rp {total_bonus:,.0f}", ln=1, align="R")

  pdf.ln(2)
  pdf.line(8, pdf.get_y(), 97, pdf.get_y())
  pdf.ln(2)

  # Total Penerimaan Gaji
  pdf.set_font("Helvetica", "B", 9)
  pdf.cell(52, 5, "TOTAL DITERIMA", ln=0)
  pdf.cell(0, 5, f"Rp {grand_total:,.0f}", ln=1, align="R")

  pdf.ln(6)
  pdf.set_font("Helvetica", "I", 7)
  pdf.cell(0, 4, "Dokumen sah dihitung otomatis oleh sistem.", ln=1, align="C")
  pdf.cell(0, 3, "Terima kasih atas kerja keras Anda!", ln=1, align="C")

  return bytes(pdf.output())


# ==========================================
# 4. FUNGSI OLAH DATA
# ==========================================
def check_login(username, password):
  conn = get_connection()
  c = conn.cursor()
  c.execute(
      "SELECT username, role, nama FROM users WHERE username = ? AND password ="
      " ?",
      (username, password),
  )
  user = c.fetchone()
  conn.close()
  return user


def simpan_penjualan(tanggal, jumlah, keterangan, input_by):
  conn = get_connection()
  c = conn.cursor()
  c.execute(
      "INSERT INTO penjualan (tanggal, jumlah, keterangan, input_by) VALUES"
      " (?, ?, ?, ?)",
      (tanggal, jumlah, keterangan, input_by),
  )
  conn.commit()
  conn.close()


def simpan_pengeluaran(tanggal, nama_item, jumlah, input_by):
  conn = get_connection()
  c = conn.cursor()
  c.execute(
      "INSERT INTO pengeluaran (tanggal, nama_item, jumlah, input_by) VALUES"
      " (?, ?, ?, ?)",
      (tanggal, nama_item, jumlah, input_by),
  )
  conn.commit()
  conn.close()


def simpan_riwayat_gaji(
    nama,
    tgl_m,
    tgl_s,
    g_hari,
    jml_h,
    tot_pokok,
    p_bonus,
    omset,
    tot_bonus,
    g_total,
):
  conn = get_connection()
  c = conn.cursor()
  c.execute(
      """
        INSERT INTO riwayat_gaji (
            tanggal_simpan, nama_karyawan, tgl_mulai, tgl_selesai, gaji_per_hari, 
            jumlah_hari, total_gaji_pokok, persen_bonus, omset_periode, total_bonus, grand_total
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """,
      (
          date.today(),
          nama,
          tgl_m,
          tgl_s,
          g_hari,
          jml_h,
          tot_pokok,
          p_bonus,
          omset,
          tot_bonus,
          g_total,
      ),
  )
  conn.commit()
  conn.close()


def load_penjualan():
  conn = get_connection()
  df = pd.read_sql_query("SELECT * FROM penjualan ORDER BY tanggal DESC", conn)
  conn.close()
  return df


def load_pengeluaran():
  conn = get_connection()
  df = pd.read_sql_query(
      "SELECT * FROM pengeluaran ORDER BY tanggal DESC", conn
  )
  conn.close()
  return df


def load_riwayat_gaji():
  conn = get_connection()
  df = pd.read_sql_query(
      "SELECT * FROM riwayat_gaji ORDER BY id DESC", conn
  )
  conn.close()
  return df


def hapus_transaksi(tabel, id_transaksi):
  conn = get_connection()
  c = conn.cursor()
  c.execute(f"DELETE FROM {tabel} WHERE id = ?", (id_transaksi,))
  conn.commit()
  conn.close()


# ==========================================
# 5. MANAJEMEN SESI
# ==========================================
if "logged_in" not in st.session_state:
  st.session_state.logged_in = False
  st.session_state.username = ""
  st.session_state.role = ""
  st.session_state.nama = ""


# ==========================================
# 6. HALAMAN LOGIN
# ==========================================
if not st.session_state.logged_in:
  st.markdown(
      "<h2 style='text-align: center;'>🏪 Sistem Rekap Toko & Penggajian</h2>",
      unsafe_allow_html=True,
  )
  col1, col2, col3 = st.columns([1, 2, 1])
  with col2:
    with st.form("login_form"):
      username_input = st.text_input("Username")
      password_input = st.text_input("Password", type="password")
      submit_button = st.form_submit_button(
          "Masuk Ke Sistem", use_container_width=True
      )

      if submit_button:
        user_info = check_login(username_input, password_input)
        if user_info:
          st.session_state.logged_in = True
          st.session_state.username = user_info[0]
          st.session_state.role = user_info[1]
          st.session_state.nama = user_info[2]
          st.rerun()
        else:
          st.error("Username atau Password salah!")


# ==========================================
# 7. HALAMAN UTAMA SETELAH LOGIN
# ==========================================
else:
  st.sidebar.title(f"👤 {st.session_state.nama}")
  st.sidebar.caption(f"Role: **{st.session_state.role.upper()}**")

  if st.session_state.role == "admin":
    menu = st.sidebar.radio(
        "Navigasi Menu",
        [
            "📊 Dashboard & Laporan",
            "✍️ Form Input Transaksi",
            "💵 Fitur Hitung & Cetak Gaji",
            "⚙️ Kelola & Hapus Data",
        ],
    )
  else:
    menu = st.sidebar.radio(
        "Navigasi Menu",
        ["✍️ Form Input Transaksi"],
    )

  if st.sidebar.button("🚪 Keluar / Logout", use_container_width=True):
    st.session_state.logged_in = False
    st.session_state.username = ""
    st.session_state.role = ""
    st.session_state.nama = ""
    st.rerun()

  # --------------------------------------------------
  # MENU 1: INPUT TRANSAKSI (Karyawan & Admin)
  # --------------------------------------------------
  if menu == "✍️ Form Input Transaksi":
    st.title("✍️ Input Penjualan & Pengeluaran Toko")
    tab1, tab2 = st.tabs(["💰 Input Penjualan", "🛒 Input Belanja Operasional"])

    with tab1:
      st.subheader("Form Input Penjualan Harian")
      with st.form("form_penjualan", clear_on_submit=True):
        tgl_penjualan = st.date_input("Tanggal", value=date.today())
        jumlah_penjualan = st.number_input(
            "Total Penjualan (Rp)", min_value=0.0, step=10000.0, format="%.0f"
        )
        ket_penjualan = st.text_input("Keterangan / Shift (Opsional)")
        btn_penjualan = st.form_submit_button("Simpan Penjualan")

        if btn_penjualan and jumlah_penjualan > 0:
          simpan_penjualan(
              tgl_penjualan,
              jumlah_penjualan,
              ket_penjualan,
              st.session_state.nama,
          )
          st.success("✅ Data penjualan berhasil tersimpan!")

    with tab2:
      st.subheader("Form Input Belanja / Biaya Operasional Toko")
      with st.form("form_pengeluaran", clear_on_submit=True):
        tgl_pengeluaran = st.date_input("Tanggal", value=date.today())
        nama_item = st.text_input("Nama Pengeluaran")
        jumlah_pengeluaran = st.number_input(
            "Total Biaya (Rp)", min_value=0.0, step=5000.0, format="%.0f"
        )
        btn_pengeluaran = st.form_submit_button("Simpan Pengeluaran")

        if btn_pengeluaran and nama_item and jumlah_pengeluaran > 0:
          simpan_pengeluaran(
              tgl_pengeluaran,
              nama_item,
              jumlah_pengeluaran,
              st.session_state.nama,
          )
          st.success("✅ Data pengeluaran berhasil tersimpan!")

  # --------------------------------------------------
  # MENU 2: DASHBOARD (Khusus Admin/Owner)
  # --------------------------------------------------
  elif menu == "📊 Dashboard & Laporan":
    st.title("📊 Laporan Finansial Toko")
    df_p = load_penjualan()
    df_e = load_pengeluaran()

    tot_p = df_p["jumlah"].sum() if not df_p.empty else 0
    tot_e = df_e["jumlah"].sum() if not df_e.empty else 0
    laba = tot_p - tot_e

    c1, c2, c3 = st.columns(3)
    c1.metric("Total Penjualan", f"Rp {tot_p:,.0f}")
    c2.metric("Total Pengeluaran", f"Rp {tot_e:,.0f}")
    c3.metric("Margin Laba / Rugi", f"Rp {laba:,.0f}")

    st.divider()
    st.subheader("📈 Grafik Penjualan Harian")
    if not df_p.empty:
      df_p["tanggal"] = pd.to_datetime(df_p["tanggal"])
      chart_data = df_p.groupby("tanggal")["jumlah"].sum()
      st.line_chart(chart_data)

  # --------------------------------------------------
  # MENU 3: FITUR HITUNG & CETAK GAJI (Khusus Admin)
  # --------------------------------------------------
  elif menu == "💵 Fitur Hitung & Cetak Gaji":
    st.title("💵 Form Penggajian & Cetak Slip Gaji")

    tab_g1, tab_g2 = st.tabs(
        ["📝 Form Pengisian Gaji", "📑 Riwayat Slip Gaji Tersimpan"]
    )

    # TAB 1: FORM PENGISIAN GAJI MANUAL & CETAK PDF
    with tab_g1:
      st.subheader("Pengisian Data Gaji Karyawan")

      # 1. Nama Karyawan (Input Manual)
      nama_karyawan_input = st.text_input(
          "1. Nama Karyawan (Isi Manual)",
          placeholder="Masukkan nama lengkap karyawan...",
      )

      # Periode Hari Kerja untuk Menghitung Omset
      st.write("**Periode Hari Kerja (Untuk Menghitung Rekap Omset Toko):**")
      col_d1, col_d2 = st.columns(2)
      with col_d1:
        default_start = date.today() - timedelta(days=13)
        tgl_mulai = st.date_input("Dari Tanggal", value=default_start)
      with col_d2:
        tgl_selesai = st.date_input("Sampai Tanggal", value=date.today())

      col_f1, col_f2, col_f3 = st.columns(3)

      # 2. Gaji Pokok per Hari & Jumlah Hari Kerja
      with col_f1:
        gaji_per_hari = st.number_input(
            "2. Gaji Pokok per Hari (Rp)",
            value=75000.0,
            step=5000.0,
            format="%.0f",
        )

      with col_f2:
        jumlah_hari_kerja = st.number_input(
            "Jumlah Hari Kerja", min_value=0, value=12, step=1
        )

      # 3. Persentase Bonus Omset
      with col_f3:
        persen_bonus = st.number_input(
            "3. Persentase Bonus Omset (%)",
            value=2.0,
            step=0.5,
            format="%.1f",
        )

      # Hitung Omset Toko Sesuai Periode Hari Kerja
      df_penjualan = load_penjualan()
      total_omset_periode = 0.0

      if not df_penjualan.empty:
        df_penjualan["tanggal"] = pd.to_datetime(
            df_penjualan["tanggal"]
        ).dt.date
        mask = (df_penjualan["tanggal"] >= tgl_mulai) & (
            df_penjualan["tanggal"] <= tgl_selesai
        )
        total_omset_periode = df_penjualan.loc[mask, "jumlah"].sum()

      # Kalkulasi Otomatis
      total_gaji_pokok = gaji_per_hari * jumlah_hari_kerja
      total_bonus = (persen_bonus / 100) * total_omset_periode
      grand_total_gaji = total_gaji_pokok + total_bonus

      st.markdown("---")

      # Ringkasan Hasil Kalkulasi
      st.subheader("🧾 Ringkasan Hasil Gaji")
      st.caption(
          f"Omset Toko Terhitung ({tgl_mulai} s/d {tgl_selesai}): **Rp"
          f" {total_omset_periode:,.0f}**"
      )

      res_c1, res_c2, res_c3 = st.columns(3)
      res_c1.metric(
          "Gaji Pokok",
          f"Rp {total_gaji_pokok:,.0f}",
          delta=f"{jumlah_hari_kerja} hari x Rp {gaji_per_hari:,.0f}",
      )
      res_c2.metric(
          "Bonus Omset",
          f"Rp {total_bonus:,.0f}",
          delta=f"{persen_bonus}% x Omset",
      )
      res_c3.metric(
          "TOTAL GAJI DITERIMA",
          f"Rp {grand_total_gaji:,.0f}",
          delta="Gaji Pokok + Bonus",
      )

      st.markdown("---")

      # 4 & 5. Tombol Simpan & Cetak PDF A6
      col_btn1, col_btn2 = st.columns(2)

      with col_btn1:
        # 4. Tombol Simpan Ke Database
        if st.button("💾 4. Simpan Slip Gaji", use_container_width=True):
          if nama_karyawan_input.strip() == "":
            st.warning("⚠️ Mohon isi nama karyawan terlebih dahulu!")
          else:
            simpan_riwayat_gaji(
                nama_karyawan_input,
                tgl_mulai,
                tgl_selesai,
                gaji_per_hari,
                jumlah_hari_kerja,
                total_gaji_pokok,
                persen_bonus,
                total_omset_periode,
                total_bonus,
                grand_total_gaji,
            )
            st.success("✅ Data slip gaji berhasil disimpan ke database!")

      with col_btn2:
        # 5. Tombol Cetak PDF A6 / Thermal
        if nama_karyawan_input.strip() != "":
          pdf_data = generate_pdf_slip(
              nama_karyawan_input,
              tgl_mulai,
              tgl_selesai,
              gaji_per_hari,
              jumlah_hari_kerja,
              total_gaji_pokok,
              persen_bonus,
              total_omset_periode,
              total_bonus,
              grand_total_gaji,
          )

          st.download_button(
              label="🖨️ 5. Cetak PDF Slip Gaji (Ukuran A6)",
              data=pdf_data,
              file_name=(
                  f"Slip_Gaji_{nama_karyawan_input.replace(' ', '_')}_{tgl_selesai}.pdf"
              ),
              mime="application/pdf",
              use_container_width=True,
          )
        else:
          st.button(
              "🖨️ 5. Cetak PDF Slip Gaji (Isi Nama Dulu)",
              disabled=True,
              use_container_width=True,
          )

    # TAB 2: RIWAYAT GAJI TERSIMPAN
    with tab_g2:
      st.subheader("Tabel Riwayat Slip Gaji Tersimpan")
      df_gaji = load_riwayat_gaji()
      if df_gaji.empty:
        st.info("Belum ada riwayat gaji yang disimpan.")
      else:
        st.dataframe(df_gaji, use_container_width=True)

  # --------------------------------------------------
  # MENU 4: KELOLA & HAPUS DATA (Khusus Admin/Owner)
  # --------------------------------------------------
  elif menu == "⚙️ Kelola & Hapus Data":
    st.title("⚙️ Hapus Data Transaksi")
    df_p = load_penjualan()
    st.dataframe(df_p, use_container_width=True)
    if not df_p.empty:
      id_del = st.number_input(
          "Masukkan ID Penjualan yang dihapus", min_value=1, step=1
      )
      if st.button("Hapus Data"):
        hapus_transaksi("penjualan", id_del)
        st.success("Data berhasil dihapus!")
        st.rerun()
