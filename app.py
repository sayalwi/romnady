from datetime import date, datetime, timedelta
import hashlib
import io
import sqlite3
from fpdf import FPDF
import pandas as pd
import streamlit as st

# ==========================================
# 1. KONFIGURASI HALAMAN STREAMLIT
# ==========================================
st.set_page_config(
    page_title="Sistem Rekap Toko & Penggajian Pro",
    page_icon="🏪",
    layout="wide",
    initial_sidebar_state="expanded",
)


# ==========================================
# 2. HELPER KEAMANAN & DATABASE
# ==========================================
def hash_password(password):
  return hashlib.sha256(password.encode()).hexdigest()


def get_connection():
  conn = sqlite3.connect("toko.db", check_same_thread=False)
  return conn


def init_db():
  conn = get_connection()
  c = conn.cursor()

  # Tabel Users
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
            metode_pembayaran TEXT DEFAULT 'Cash',
            keterangan TEXT,
            input_by TEXT
        )
    """)

  # Tabel Pengeluaran Operasional
  c.execute("""
        CREATE TABLE IF NOT EXISTS pengeluaran (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            tanggal DATE NOT NULL,
            kategori TEXT DEFAULT 'Operasional',
            nama_item TEXT NOT NULL,
            jumlah REAL NOT NULL,
            input_by TEXT
        )
    """)

  # Tabel Riwayat Slip Gaji
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

  # Migrasi Kolom jika DB Lama Ada
  c.execute("PRAGMA table_info(penjualan)")
  cols_p = [col[1] for col in c.fetchall()]
  if "metode_pembayaran" not in cols_p:
    c.execute(
        "ALTER TABLE penjualan ADD COLUMN metode_pembayaran TEXT DEFAULT 'Cash'"
    )

  c.execute("PRAGMA table_info(pengeluaran)")
  cols_e = [col[1] for col in c.fetchall()]
  if "kategori" not in cols_e:
    c.execute(
        "ALTER TABLE pengeluaran ADD COLUMN kategori TEXT DEFAULT 'Operasional'"
    )

  # Akun Default (Hashed Password)
  c.execute("SELECT COUNT(*) FROM users")
  if c.fetchone()[0] == 0:
    c.execute(
        "INSERT INTO users VALUES (?, ?, ?, ?)",
        ("admin", hash_password("admin123"), "admin", "Owner Toko"),
    )
    c.execute(
        "INSERT INTO users VALUES (?, ?, ?, ?)",
        ("karyawan", hash_password("karyawan123"), "karyawan", "Staf Kasir"),
    )

  conn.commit()
  conn.close()


init_db()


# ==========================================
# 3. GENERATE PDF SLIP GAJI (FORMAT A6)
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
  pdf = FPDF(orientation="P", unit="mm", format=(105, 148))
  pdf.set_margins(8, 8, 8)
  pdf.add_page()

  pdf.set_font("Helvetica", "B", 12)
  pdf.cell(0, 6, "SLIP GAJI KARYAWAN", ln=1, align="C")
  pdf.set_font("Helvetica", "", 8)
  pdf.cell(0, 4, "REKAP TOKO OPERASIONAL", ln=1, align="C")
  pdf.line(8, pdf.get_y() + 1, 97, pdf.get_y() + 1)
  pdf.ln(3)

  pdf.set_font("Helvetica", "", 8)
  pdf.cell(28, 4, "Nama Karyawan", ln=0)
  pdf.cell(0, 4, f": {nama}", ln=1)
  pdf.cell(28, 4, "Periode Kerja", ln=0)
  pdf.cell(0, 4, f": {tgl_mulai} s/d {tgl_selesai}", ln=1)
  pdf.ln(2)
  pdf.line(8, pdf.get_y(), 97, pdf.get_y())
  pdf.ln(2)

  pdf.set_font("Helvetica", "B", 8)
  pdf.cell(0, 4, "RINCIAN PEMBAYARAN", ln=1)
  pdf.set_font("Helvetica", "", 8)

  pdf.cell(
      52, 4, f"Gaji Pokok ({hari_kerja} hr x Rp {gaji_harian:,.0f})", ln=0
  )
  pdf.cell(0, 4, f"Rp {total_pokok:,.0f}", ln=1, align="R")

  pdf.cell(52, 4, f"Bonus Omset ({persen_bonus}% x Rp {omset:,.0f})", ln=0)
  pdf.cell(0, 4, f"Rp {total_bonus:,.0f}", ln=1, align="R")

  pdf.ln(2)
  pdf.line(8, pdf.get_y(), 97, pdf.get_y())
  pdf.ln(2)

  pdf.set_font("Helvetica", "B", 9)
  pdf.cell(52, 5, "TOTAL DITERIMA", ln=0)
  pdf.cell(0, 5, f"Rp {grand_total:,.0f}", ln=1, align="R")

  pdf.ln(6)
  pdf.set_font("Helvetica", "I", 7)
  pdf.cell(0, 4, "Dokumen sah dihitung otomatis oleh sistem.", ln=1, align="C")
  pdf.cell(0, 3, "Terima kasih atas kerja keras Anda!", ln=1, align="C")

  return bytes(pdf.output())


# ==========================================
# 4. FUNGSI CRUD & DATA
# ==========================================
def check_login(username, password):
  conn = get_connection()
  c = conn.cursor()
  c.execute(
      "SELECT username, role, nama FROM users WHERE username = ? AND password ="
      " ?",
      (username, hash_password(password)),
  )
  user = c.fetchone()
  conn.close()
  return user


def simpan_penjualan(tanggal, jumlah, metode, keterangan, input_by):
  conn = get_connection()
  c = conn.cursor()
  c.execute(
      "INSERT INTO penjualan (tanggal, jumlah, metode_pembayaran, keterangan,"
      " input_by) VALUES (?, ?, ?, ?, ?)",
      (tanggal, jumlah, metode, keterangan, input_by),
  )
  conn.commit()
  conn.close()


def update_penjualan(id_p, tanggal, jumlah, metode, keterangan):
  conn = get_connection()
  c = conn.cursor()
  c.execute(
      "UPDATE penjualan SET tanggal=?, jumlah=?, metode_pembayaran=?,"
      " keterangan=? WHERE id=?",
      (tanggal, jumlah, metode, keterangan, id_p),
  )
  conn.commit()
  conn.close()


def simpan_pengeluaran(tanggal, kategori, nama_item, jumlah, input_by):
  conn = get_connection()
  c = conn.cursor()
  c.execute(
      "INSERT INTO pengeluaran (tanggal, kategori, nama_item, jumlah, input_by)"
      " VALUES (?, ?, ?, ?, ?)",
      (tanggal, kategori, nama_item, jumlah, input_by),
  )
  conn.commit()
  conn.close()


def update_pengeluaran(id_e, tanggal, kategori, nama_item, jumlah):
  conn = get_connection()
  c = conn.cursor()
  c.execute(
      "UPDATE pengeluaran SET tanggal=?, kategori=?, nama_item=?, jumlah=?"
      " WHERE id=?",
      (tanggal, kategori, nama_item, jumlah, id_e),
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


def tambah_user(username, password, role, nama):
  conn = get_connection()
  c = conn.cursor()
  try:
    c.execute(
        "INSERT INTO users VALUES (?, ?, ?, ?)",
        (username, hash_password(password), role, nama),
    )
    conn.commit()
    conn.close()
    return True
  except:
    conn.close()
    return False


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


def load_users():
  conn = get_connection()
  df = pd.read_sql_query("SELECT username, role, nama FROM users", conn)
  conn.close()
  return df


def hapus_transaksi(tabel, id_transaksi):
  conn = get_connection()
  c = conn.cursor()
  c.execute(f"DELETE FROM {tabel} WHERE id = ?", (id_transaksi,))
  conn.commit()
  conn.close()


def export_to_excel(df_p, df_e):
  output = io.BytesIO()
  with pd.ExcelWriter(output, engine="openpyxl") as writer:
    df_p.to_excel(writer, sheet_name="Penjualan", index=False)
    df_e.to_excel(writer, sheet_name="Pengeluaran", index=False)
  return output.getvalue()


# ==========================================
# 5. MANAJEMEN SESI & LOGIN
# ==========================================
if "logged_in" not in st.session_state:
  st.session_state.logged_in = False
  st.session_state.username = ""
  st.session_state.role = ""
  st.session_state.nama = ""

if not st.session_state.logged_in:
  st.markdown(
      "<h2 style='text-align: center;'>🏪 Sistem Rekap Toko & Penggajian"
      " Pro</h2>",
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
# 6. HALAMAN UTAMA SETELAH LOGIN
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
            "⚙️ Edit & Hapus Transaksi",
            "👥 Kelola Akun Karyawan",
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
        metode_bayar = st.selectbox(
            "Metode Pembayaran", options=["Cash / Tunai", "QRIS / Transfer"]
        )
        ket_penjualan = st.text_input("Keterangan / Shift (Opsional)")
        btn_penjualan = st.form_submit_button("Simpan Penjualan")

        if btn_penjualan and jumlah_penjualan > 0:
          simpan_penjualan(
              tgl_penjualan,
              jumlah_penjualan,
              metode_bayar,
              ket_penjualan,
              st.session_state.nama,
          )
          st.success("✅ Data penjualan berhasil tersimpan!")

    with tab2:
      st.subheader("Form Input Belanja / Biaya Operasional Toko")
      with st.form("form_pengeluaran", clear_on_submit=True):
        tgl_pengeluaran = st.date_input("Tanggal", value=date.today())
        kategori_e = st.selectbox(
            "Kategori Pengeluaran",
            options=[
                "Operasional & Plastik",
                "Belanja Stok",
                "Token Listrik & Air",
                "Gaji & Bonus Karyawan",
                "Lain-lain",
            ],
        )
        nama_item = st.text_input("Nama Pengeluaran / Item")
        jumlah_pengeluaran = st.number_input(
            "Total Biaya (Rp)", min_value=0.0, step=5000.0, format="%.0f"
        )
        btn_pengeluaran = st.form_submit_button("Simpan Pengeluaran")

        if btn_pengeluaran and nama_item and jumlah_pengeluaran > 0:
          simpan_pengeluaran(
              tgl_pengeluaran,
              kategori_e,
              nama_item,
              jumlah_pengeluaran,
              st.session_state.nama,
          )
          st.success("✅ Data pengeluaran berhasil tersimpan!")

  # --------------------------------------------------
  # MENU 2: DASHBOARD & FILTER TANGGAL (Admin)
  # --------------------------------------------------
  elif menu == "📊 Dashboard & Laporan":
    st.title("📊 Laporan Finansial & Dashboard Toko")

    # Filter Periode Tanggal
    col_filter, col_exp = st.columns([3, 1])
    with col_filter:
      filter_opt = st.selectbox(
          "Filter Periode Tanggal",
          options=[
              "Hari Ini",
              "7 Hari Terakhir",
              "Bulan Ini",
              "Semua Data",
              "Custom Tanggal",
          ],
      )

    df_p = load_penjualan()
    df_e = load_pengeluaran()

    if not df_p.empty:
      df_p["tanggal"] = pd.to_datetime(df_p["tanggal"]).dt.date
    if not df_e.empty:
      df_e["tanggal"] = pd.to_datetime(df_e["tanggal"]).dt.date

    today = date.today()

    if filter_opt == "Hari Ini":
      df_p_f = df_p[df_p["tanggal"] == today] if not df_p.empty else df_p
      df_e_f = df_e[df_e["tanggal"] == today] if not df_e.empty else df_e
    elif filter_opt == "7 Hari Terakhir":
      start_d = today - timedelta(days=6)
      df_p_f = (
          df_p[(df_p["tanggal"] >= start_d) & (df_p["tanggal"] <= today)]
          if not df_p.empty
          else df_p
      )
      df_e_f = (
          df_e[(df_e["tanggal"] >= start_d) & (df_e["tanggal"] <= today)]
          if not df_e.empty
          else df_e
      )
    elif filter_opt == "Bulan Ini":
      start_d = today.replace(day=1)
      df_p_f = (
          df_p[(df_p["tanggal"] >= start_d) & (df_p["tanggal"] <= today)]
          if not df_p.empty
          else df_p
      )
      df_e_f = (
          df_e[(df_e["tanggal"] >= start_d) & (df_e["tanggal"] <= today)]
          if not df_e.empty
          else df_e
      )
    elif filter_opt == "Custom Tanggal":
      c_d1, c_d2 = st.columns(2)
      with c_d1:
        start_custom = st.date_input(
            "Dari Tanggal", value=today - timedelta(days=7)
        )
      with c_d2:
        end_custom = st.date_input("Sampai Tanggal", value=today)
      df_p_f = (
          df_p[
              (df_p["tanggal"] >= start_custom) & (df_p["tanggal"] <= end_custom)
          ]
          if not df_p.empty
          else df_p
      )
      df_e_f = (
          df_e[
              (df_e["tanggal"] >= start_custom) & (df_e["tanggal"] <= end_custom)
          ]
          if not df_e.empty
          else df_e
      )
    else:
      df_p_f, df_e_f = df_p, df_e

    # Export Excel Button
    with col_exp:
      if not df_p.empty or not df_e.empty:
        excel_bytes = export_to_excel(df_p, df_e)
        st.download_button(
            label="📥 Export Excel (.xlsx)",
            data=excel_bytes,
            file_name=f"Laporan_Toko_{today}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True,
        )

    # Metrics Summary
    tot_p = df_p_f["jumlah"].sum() if not df_p_f.empty else 0
    tot_e = df_e_f["jumlah"].sum() if not df_e_f.empty else 0
    laba = tot_p - tot_e

    tot_cash = (
        df_p_f[df_p_f["metode_pembayaran"] == "Cash / Tunai"]["jumlah"].sum()
        if not df_p_f.empty and "metode_pembayaran" in df_p_f.columns
        else 0
    )
    tot_qris = (
        df_p_f[df_p_f["metode_pembayaran"] == "QRIS / Transfer"]["jumlah"].sum()
        if not df_p_f.empty and "metode_pembayaran" in df_p_f.columns
        else 0
    )

    c1, c2, c3 = st.columns(3)
    c1.metric("Total Penjualan Omset", f"Rp {tot_p:,.0f}")
    c2.metric("Total Pengeluaran", f"Rp {tot_e:,.0f}")
    c3.metric("Margin Laba / Rugi", f"Rp {laba:,.0f}")

    st.markdown("---")
    st.subheader("💳 Breakdown Kas Metode Pembayaran")
    mc1, mc2 = st.columns(2)
    mc1.info(f"💵 **Uang Tunai (Cash di Kasir):** Rp {tot_cash:,.0f}")
    mc2.success(f"📱 **QRIS / Transfer (Bank):** Rp {tot_qris:,.0f}")

    st.divider()
    st.subheader("📈 Grafik Tren Penjualan Harian")
    if not df_p_f.empty:
      chart_data = df_p_f.groupby("tanggal")["jumlah"].sum()
      st.line_chart(chart_data)

  # --------------------------------------------------
  # MENU 3: FITUR HITUNG & CETAK GAJI (Khusus Admin)
  # --------------------------------------------------
  elif menu == "💵 Fitur Hitung & Cetak Gaji":
    st.title("💵 Form Penggajian & Cetak Slip Gaji")
    tab_g1, tab_g2 = st.tabs(
        ["📝 Form Pengisian Gaji", "📑 Riwayat Slip Gaji Tersimpan"]
    )

    with tab_g1:
      st.subheader("Pengisian Data Gaji Karyawan")
      nama_karyawan_input = st.text_input(
          "1. Nama Karyawan (Isi Manual)",
          placeholder="Masukkan nama lengkap...",
      )

      st.write("**Periode Hari Kerja (Hitung Omset Toko):**")
      col_d1, col_d2 = st.columns(2)
      with col_d1:
        default_start = date.today() - timedelta(days=13)
        tgl_mulai = st.date_input("Dari Tanggal", value=default_start)
      with col_d2:
        tgl_selesai = st.date_input("Sampai Tanggal", value=date.today())

      col_f1, col_f2, col_f3 = st.columns(3)
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
      with col_f3:
        persen_bonus = st.number_input(
            "3. Persentase Bonus Omset (%)",
            value=2.0,
            step=0.5,
            format="%.1f",
        )

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

      total_gaji_pokok = gaji_per_hari * jumlah_hari_kerja
      total_bonus = (persen_bonus / 100) * total_omset_periode
      grand_total_gaji = total_gaji_pokok + total_bonus

      st.markdown("---")
      st.subheader("🧾 Ringkasan Hasil Gaji")
      res_c1, res_c2, res_c3 = st.columns(3)
      res_c1.metric(
          "Gaji Pokok",
          f"Rp {total_gaji_pokok:,.0f}",
          delta=f"{jumlah_hari_kerja} hr x Rp {gaji_per_hari:,.0f}",
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
      col_btn1, col_btn2 = st.columns(2)

      with col_btn1:
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
            st.success("✅ Data slip gaji berhasil disimpan!")

      with col_btn2:
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
              label="🖨️ 5. Cetak PDF Slip Gaji (A6 Thermal)",
              data=pdf_data,
              file_name=(
                  f"Slip_Gaji_{nama_karyawan_input.replace(' ', '_')}_{tgl_selesai}.pdf"
              ),
              mime="application/pdf",
              use_container_width=True,
          )

    # TAB 2: RIWAYAT GAJI TERSIMPAN & RE-PRINT PDF
    with tab_g2:
      st.subheader("Tabel Riwayat Slip Gaji Tersimpan")
      df_gaji = load_riwayat_gaji()
      if df_gaji.empty:
        st.info("Belum ada riwayat gaji yang disimpan.")
      else:
        st.dataframe(df_gaji, use_container_width=True)
        st.markdown("---")
        st.write("**🖨️ Cetak Ulang Slip Gaji dari Riwayat:**")

        id_gaji_print = st.selectbox(
            "Pilih ID Slip Gaji yang ingin dicetak ulang",
            options=df_gaji["id"].tolist(),
        )

        row_print = df_gaji[df_gaji["id"] == id_gaji_print].iloc[0]
        pdf_reprint = generate_pdf_slip(
            row_print["nama_karyawan"],
            row_print["tgl_mulai"],
            row_print["tgl_selesai"],
            row_print["gaji_per_hari"],
            row_print["jumlah_hari"],
            row_print["total_gaji_pokok"],
            row_print["persen_bonus"],
            row_print["omset_periode"],
            row_print["total_bonus"],
            row_print["grand_total"],
        )

        st.download_button(
            label=f"Unduh Slip Gaji ID #{id_gaji_print} ({row_print['nama_karyawan']})",
            data=pdf_reprint,
            file_name=f"Slip_Gaji_{row_print['nama_karyawan']}_{row_print['tgl_selesai']}.pdf",
            mime="application/pdf",
        )

  # --------------------------------------------------
  # MENU 4: EDIT & HAPUS TRANSAKSI (Admin)
  # --------------------------------------------------
  elif menu == "⚙️ Edit & Hapus Transaksi":
    st.title("⚙️ Koreksi / Edit & Hapus Transaksi")
    tab_edit1, tab_edit2 = st.tabs(["Edit Penjualan", "Edit Pengeluaran"])

    # EDIT PENJUALAN
    with tab_edit1:
      df_p = load_penjualan()
      st.dataframe(df_p, use_container_width=True)
      if not df_p.empty:
        st.markdown("---")
        st.write("**Pilih ID Penjualan untuk Diubah / Dihapus:**")
        id_p_select = st.selectbox(
            "Pilih ID Penjualan", options=df_p["id"].tolist(), key="select_p"
        )
        data_p_sel = df_p[df_p["id"] == id_p_select].iloc[0]

        with st.form("form_edit_p"):
          ep_tgl = st.date_input(
              "Tanggal",
              value=pd.to_datetime(data_p_sel["tanggal"]).date(),
          )
          ep_jumlah = st.number_input(
              "Total Penjualan (Rp)",
              value=float(data_p_sel["jumlah"]),
              step=5000.0,
          )
          ep_metode = st.selectbox(
              "Metode Pembayaran",
              options=["Cash / Tunai", "QRIS / Transfer"],
              index=(
                  0
                  if data_p_sel.get("metode_pembayaran") == "Cash / Tunai"
                  else 1
              ),
          )
          ep_ket = st.text_input(
              "Keterangan", value=str(data_p_sel["keterangan"] or "")
          )

          col_ed_btn1, col_ed_btn2 = st.columns(2)
          with col_ed_btn1:
            btn_update_p = st.form_submit_button("✏️ Simpan Perubahan")
          with col_ed_btn2:
            btn_del_p = st.form_submit_button("🗑️ Hapus Data Ini")

          if btn_update_p:
            update_penjualan(id_p_select, ep_tgl, ep_jumlah, ep_metode, ep_ket)
            st.success("✅ Data penjualan berhasil diperbarui!")
            st.rerun()

          if btn_del_p:
            hapus_transaksi("penjualan", id_p_select)
            st.success("✅ Data penjualan berhasil dihapus!")
            st.rerun()

    # EDIT PENGELUARAN
    with tab_edit2:
      df_e = load_pengeluaran()
      st.dataframe(df_e, use_container_width=True)
      if not df_e.empty:
        st.markdown("---")
        st.write("**Pilih ID Pengeluaran untuk Diubah / Dihapus:**")
        id_e_select = st.selectbox(
            "Pilih ID Pengeluaran", options=df_e["id"].tolist(), key="select_e"
        )
        data_e_sel = df_e[df_e["id"] == id_e_select].iloc[0]

        with st.form("form_edit_e"):
          ee_tgl = st.date_input(
              "Tanggal",
              value=pd.to_datetime(data_e_sel["tanggal"]).date(),
          )
          ee_kat = st.selectbox(
              "Kategori Pengeluaran",
              options=[
                  "Operasional & Plastik",
                  "Belanja Stok",
                  "Token Listrik & Air",
                  "Gaji & Bonus Karyawan",
                  "Lain-lain",
              ],
          )
          ee_nama = st.text_input("Nama Item", value=str(data_e_sel["nama_item"]))
          ee_jumlah = st.number_input(
              "Total Biaya (Rp)",
              value=float(data_e_sel["jumlah"]),
              step=5000.0,
          )

          col_ee_btn1, col_ee_btn2 = st.columns(2)
          with col_ee_btn1:
            btn_update_e = st.form_submit_button("✏️ Simpan Perubahan")
          with col_ee_btn2:
            btn_del_e = st.form_submit_button("🗑️ Hapus Data Ini")

          if btn_update_e:
            update_pengeluaran(id_e_select, ee_tgl, ee_kat, ee_nama, ee_jumlah)
            st.success("✅ Data pengeluaran berhasil diperbarui!")
            st.rerun()

          if btn_del_e:
            hapus_transaksi("pengeluaran", id_e_select)
            st.success("✅ Data pengeluaran berhasil dihapus!")
            st.rerun()

  # --------------------------------------------------
  # MENU 5: KELOLA AKUN KARYAWAN (Admin)
  # --------------------------------------------------
  elif menu == "👥 Kelola Akun Karyawan":
    st.title("👥 Kelola Akun Pengguna & Karyawan")

    df_u = load_users()
    st.subheader("Daftar Pengguna Aktif")
    st.dataframe(df_u, use_container_width=True)

    st.markdown("---")
    st.subheader("➕ Tambah Akun Karyawan Baru")
    with st.form("form_add_user", clear_on_submit=True):
      u_username = st.text_input("Username (Tanpa Spasi)")
      u_nama = st.text_input("Nama Lengkap Karyawan")
      u_password = st.text_input("Password", type="password")
      u_role = st.selectbox("Role Hak Akses", options=["karyawan", "admin"])
      btn_add_u = st.form_submit_button("Tambah Akun Baru")

      if btn_add_u:
        if u_username and u_password and u_nama:
          res = tambah_user(u_username, u_password, u_role, u_nama)
          if res:
            st.success(f"✅ Akun '{u_username}' berhasil ditambahkan!")
            st.rerun()
          else:
            st.error("❌ Username sudah dipakai. Gunakan username lain.")
        else:
          st.warning("⚠️ Mohon lengkapi semua kolom.")
