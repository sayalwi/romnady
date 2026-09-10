from datetime import date, datetime
import sqlite3
import pandas as pd
import streamlit as st

# ==========================================
# 1. KONFIGURASI HALAMAN STREAMLIT
# ==========================================
st.set_page_config(
    page_title="Sistem Rekap Toko Modern",
    page_icon="🏪",
    layout="wide",
    initial_sidebar_state="expanded",
)


# ==========================================
# 2. INISIALISASI DATABASE SQLITE
# ==========================================
def get_connection():
  # SQLite membuat database 'toko.db' secara otomatis di server
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

  # Buat Akun Default jika belum ada data
  c.execute("SELECT COUNT(*) FROM users")
  if c.fetchone()[0] == 0:
    # Akun Admin/Owner (Password: admin123)
    c.execute(
        "INSERT INTO users VALUES ('admin', 'admin123', 'admin', 'Owner"
        " Toko')"
    )
    # Akun Karyawan (Password: karyawan123)
    c.execute(
        "INSERT INTO users VALUES ('karyawan', 'karyawan123', 'karyawan', 'Staf"
        " Kasir')"
    )

  conn.commit()
  conn.close()


# Jalankan pembuat database
init_db()


# ==========================================
# 3. FUNGSI OLAH DATA & AUTENTIKASI
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


def hapus_transaksi(tabel, id_transaksi):
  conn = get_connection()
  c = conn.cursor()
  c.execute(f"DELETE FROM {tabel} WHERE id = ?", (id_transaksi,))
  conn.commit()
  conn.close()


# ==========================================
# 4. MANAJEMEN SESI (SESSION STATE)
# ==========================================
if "logged_in" not in st.session_state:
  st.session_state.logged_in = False
  st.session_state.username = ""
  st.session_state.role = ""
  st.session_state.nama = ""


# ==========================================
# 5. HALAMAN LOGIN
# ==========================================
if not st.session_state.logged_in:
  st.markdown(
      "<h2 style='text-align: center;'>🏪 Sistem Rekap Penjualan Toko</h2>",
      unsafe_allow_html=True,
  )
  st.markdown(
      "<p style='text-align: center; color: gray;'>Masuk menggunakan akun Anda"
      " untuk melanjutkan</p>",
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
          st.success(f"Selamat datang, {user_info[2]}!")
          st.rerun()
        else:
          st.error("Username atau Password salah!")


# ==========================================
# 6. HALAMAN UTAMA SETELAH LOGIN
# ==========================================
else:
  # Sidebar Informasi & Menu
  st.sidebar.title(f"👤 {st.session_state.nama}")
  st.sidebar.caption(f"Role: **{st.session_state.role.upper()}**")

  # Pembatasan Hak Akses Menu
  if st.session_state.role == "admin":
    menu = st.sidebar.radio(
        "Navigasi Menu",
        [
            "📊 Dashboard & Laporan",
            "✍️ Form Input Transaksi",
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
    tab1, tab2, tab3 = st.tabs([
        "💰 Input Penjualan",
        "🛒 Input Belanja Operasional",
        "📋 Input Hari Ini",
    ])

    with tab1:
      st.subheader("Form Input Penjualan Harian")
      with st.form("form_penjualan", clear_on_submit=True):
        tgl_penjualan = st.date_input("Tanggal", value=date.today())
        jumlah_penjualan = st.number_input(
            "Total Penjualan (Rp)", min_value=0.0, step=10000.0, format="%.0f"
        )
        ket_penjualan = st.text_input("Keterangan / Shift (Opsional)")
        btn_penjualan = st.form_submit_button("Simpan Penjualan")

        if btn_penjualan:
          if jumlah_penjualan > 0:
            simpan_penjualan(
                tgl_penjualan,
                jumlah_penjualan,
                ket_penjualan,
                st.session_state.nama,
            )
            st.success("✅ Data penjualan berhasil tersimpan!")
          else:
            st.warning("Nominal penjualan harus lebih besar dari 0.")

    with tab2:
      st.subheader("Form Input Belanja / Biaya Operasional Toko")
      with st.form("form_pengeluaran", clear_on_submit=True):
        tgl_pengeluaran = st.date_input("Tanggal", value=date.today())
        nama_item = st.text_input(
            "Nama Pengeluaran (Contoh: Beli Token Listrik, Plastik, Kebersihan)"
        )
        jumlah_pengeluaran = st.number_input(
            "Total Biaya (Rp)", min_value=0.0, step=5000.0, format="%.0f"
        )
        btn_pengeluaran = st.form_submit_button("Simpan Pengeluaran")

        if btn_pengeluaran:
          if nama_item and jumlah_pengeluaran > 0:
            simpan_pengeluaran(
                tgl_pengeluaran,
                nama_item,
                jumlah_pengeluaran,
                st.session_state.nama,
            )
            st.success("✅ Data pengeluaran berhasil tersimpan!")
          else:
            st.warning("Lengkapi nama item dan total biaya pengeluaran.")

    with tab3:
      st.subheader("Ringkasan Data yang Diinput Hari Ini")
      df_p = load_penjualan()
      df_e = load_pengeluaran()

      today_str = str(date.today())
      df_p_today = (
          df_p[df_p["tanggal"] == today_str] if not df_p.empty else pd.DataFrame()
      )
      df_e_today = (
          df_e[df_e["tanggal"] == today_str] if not df_e.empty else pd.DataFrame()
      )

      col_a, col_b = st.columns(2)
      with col_a:
        st.write("**Penjualan Hari Ini:**")
        st.dataframe(df_p_today, use_container_width=True)
      with col_b:
        st.write("**Pengeluaran Hari Ini:**")
        st.dataframe(df_e_today, use_container_width=True)

  # --------------------------------------------------
  # MENU 2: DASHBOARD & LAPORAN (Khusus Admin/Owner)
  # --------------------------------------------------
  elif menu == "📊 Dashboard & Laporan":
    st.title("📊 Laporan Finansial & Margin Laba/Rugi")

    df_p = load_penjualan()
    df_e = load_pengeluaran()

    if df_p.empty and df_e.empty:
      st.info("Belum ada data transaksi yang dapat ditampilkan.")
    else:
      # Hitung Ringkasan Finansial Total
      tot_penjualan = df_p["jumlah"].sum() if not df_p.empty else 0
      tot_pengeluaran = df_e["jumlah"].sum() if not df_e.empty else 0
      laba_rugi = tot_penjualan - tot_pengeluaran

      # Ringkasan Metrics
      c1, c2, c3 = st.columns(3)
      c1.metric("Total Penjualan", f"Rp {tot_penjualan:,.0f}")
      c2.metric("Total Pengeluaran", f"Rp {tot_pengeluaran:,.0f}")
      c3.metric("Margin Laba / Rugi Net", f"Rp {laba_rugi:,.0f}")

      st.divider()

      # Visualisasi Grafik Penjualan & Pengeluaran
      st.subheader("📈 Grafik Perbandingan Penjualan vs Pengeluaran Harian")

      if not df_p.empty:
        df_p["tanggal"] = pd.to_datetime(df_p["tanggal"])
      if not df_e.empty:
        df_e["tanggal"] = pd.to_datetime(df_e["tanggal"])

      p_daily = (
          df_p.groupby("tanggal")["jumlah"].sum().reset_index()
          if not df_p.empty
          else pd.DataFrame(columns=["tanggal", "jumlah"])
      )
      e_daily = (
          df_e.groupby("tanggal")["jumlah"].sum().reset_index()
          if not df_e.empty
          else pd.DataFrame(columns=["tanggal", "jumlah"])
      )

      merged = pd.merge(
          p_daily,
          e_daily,
          on="tanggal",
          how="outer",
          suffixes=("_penjualan", "_pengeluaran"),
      ).fillna(0)
      merged = merged.rename(
          columns={
              "jumlah_penjualan": "Penjualan (Rp)",
              "jumlah_pengeluaran": "Pengeluaran (Rp)",
          }
      )
      merged = merged.set_index("tanggal")

      # Tampilkan Line Chart Interaktif
      st.line_chart(merged)

  # --------------------------------------------------
  # MENU 3: KELOLA & HAPUS DATA (Khusus Admin/Owner)
  # --------------------------------------------------
  elif menu == "⚙️ Kelola & Hapus Data":
    st.title("⚙️ Hapus Data Transaksi (Koreksi Input)")

    tab_h1, tab_h2 = st.tabs(["Data Penjualan", "Data Pengeluaran"])

    with tab_h1:
      df_p = load_penjualan()
      st.dataframe(df_p, use_container_width=True)
      if not df_p.empty:
        id_del_p = st.number_input(
            "Masukkan ID Penjualan yang ingin dihapus", min_value=1, step=1
        )
        if st.button("Hapus Data Penjualan", type="primary"):
          hapus_transaksi("penjualan", id_del_p)
          st.success(f"Data Penjualan ID {id_del_p} berhasil dihapus!")
          st.rerun()

    with tab_h2:
      df_e = load_pengeluaran()
      st.dataframe(df_e, use_container_width=True)
      if not df_e.empty:
        id_del_e = st.number_input(
            "Masukkan ID Pengeluaran yang ingin dihapus", min_value=1, step=1
        )
        if st.button("Hapus Data Pengeluaran", type="primary"):
          hapus_transaksi("pengeluaran", id_del_e)
          st.success(f"Data Pengeluaran ID {id_del_e} berhasil dihapus!")
          st.rerun()