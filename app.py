from datetime import date, timedelta
import sqlite3
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
            nama TEXT NOT NULL,
            gaji_per_hari REAL DEFAULT 0,
            persen_bonus REAL DEFAULT 0
        )
    """)

  # Penyesuaian Kolom jika Database Lama Ada
  c.execute("PRAGMA table_info(users)")
  columns = [col[1] for col in c.fetchall()]
  if "gaji_per_hari" not in columns:
    c.execute("ALTER TABLE users ADD COLUMN gaji_per_hari REAL DEFAULT 0")
  if "persen_bonus" not in columns:
    c.execute("ALTER TABLE users ADD COLUMN persen_bonus REAL DEFAULT 0")

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

  # Akun Default
  c.execute("SELECT COUNT(*) FROM users")
  if c.fetchone()[0] == 0:
    c.execute(
        "INSERT INTO users (username, password, role, nama, gaji_per_hari,"
        " persen_bonus) VALUES ('admin', 'admin123', 'admin', 'Owner Toko', 0,"
        " 0)"
    )
    c.execute(
        "INSERT INTO users (username, password, role, nama, gaji_per_hari,"
        " persen_bonus) VALUES ('karyawan', 'karyawan123', 'karyawan', 'Staf"
        " Kasir', 75000, 2.0)"
    )

  conn.commit()
  conn.close()


init_db()


# ==========================================
# 3. FUNGSI OLAH DATA
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


def load_users():
  conn = get_connection()
  df = pd.read_sql_query(
      "SELECT username, nama, role, gaji_per_hari, persen_bonus FROM users",
      conn,
  )
  conn.close()
  return df


def update_gaji_user(username, gaji_per_hari, persen_bonus):
  conn = get_connection()
  c = conn.cursor()
  c.execute(
      "UPDATE users SET gaji_per_hari = ?, persen_bonus = ? WHERE username ="
      " ?",
      (gaji_per_hari, persen_bonus, username),
  )
  conn.commit()
  conn.close()


def hapus_transaksi(tabel, id_transaksi):
  conn = get_connection()
  c = conn.cursor()
  c.execute(f"DELETE FROM {tabel} WHERE id = ?", (id_transaksi,))
  conn.commit()
  conn.close()


# ==========================================
# 4. MANAJEMEN SESI
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
            "💵 Fitur Gaji 2 Mingguan",
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
  # MENU 1: INPUT TRANSAKSI
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
  # MENU 2: DASHBOARD
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
  # MENU 3: FITUR GAJI 2 MINGGUAN (Sesuai Permintaan)
  # --------------------------------------------------
  elif menu == "💵 Fitur Gaji 2 Mingguan":
    st.title("💵 Hitung Gaji 2 Mingguan & Bonus Karyawan")

    tab_g1, tab_g2 = st.tabs(
        ["📝 Form Hitung Gaji 2 Mingguan", "⚙️ Master Tarif Harian & Bonus"]
    )

    df_users = load_users()
    karyawan_df = df_users[df_users["role"] == "karyawan"]

    # TAB 1: FORM PENGISIAN GAJI INTERAKTIF
    with tab_g1:
      st.subheader("Form Hitung Gaji Karyawan (Per 2 Minggu)")

      if karyawan_df.empty:
        st.warning(
            "Belum ada akun karyawan terdaftar. Tambahkan karyawan terlebih"
            " dahulu."
        )
      else:
        # 1. Pilih Nama Karyawan
        karyawan_options = dict(
            zip(karyawan_df["username"], karyawan_df["nama"])
        )
        selected_username = st.selectbox(
            "Pilih Karyawan",
            options=list(karyawan_options.keys()),
            format_func=lambda x: karyawan_options[x],
        )

        user_data = karyawan_df[
            karyawan_df["username"] == selected_username
        ].iloc[0]

        # 2. Periode Kerja 2 Minggu (Default 14 Hari Terakhir)
        col_d1, col_d2 = st.columns(2)
        with col_d1:
          default_start = date.today() - timedelta(days=13)
          tgl_mulai = st.date_input("Dari Tanggal", value=default_start)
        with col_d2:
          tgl_selesai = st.date_input("Sampai Tanggal", value=date.today())

        st.markdown("---")

        # 3. Input Nilai Gaji & Hari Kerja
        col_f1, col_f2, col_f3 = st.columns(3)

        with col_f1:
          # Gaji per Hari (Diisi otomatis dari standar, namun bisa diubah manual)
          gaji_harian_input = st.number_input(
              "Gaji per Hari (Rp)",
              value=float(user_data["gaji_per_hari"]),
              step=5000.0,
              format="%.0f",
          )

        with col_f2:
          # Jumlah Hari Kerja
          jumlah_hari_kerja = st.number_input(
              "Jumlah Hari Kerja (2 Minggu)",
              min_value=0,
              max_value=14,
              value=12,
              step=1,
          )

        with col_f3:
          # Persentase Bonus
          persen_bonus_input = st.number_input(
              "Bonus Penjualan (%)",
              value=float(user_data["persen_bonus"]),
              step=0.5,
              format="%.1f",
          )

        # 4. Ambil Rekap Penjualan Harian pada Rentang Tanggal
        df_penjualan = load_penjualan()
        total_omset = 0.0

        if not df_penjualan.empty:
          df_penjualan["tanggal"] = pd.to_datetime(
              df_penjualan["tanggal"]
          ).dt.date
          mask = (df_penjualan["tanggal"] >= tgl_mulai) & (
              df_penjualan["tanggal"] <= tgl_selesai
          )
          df_periode = df_penjualan.loc[mask]
          total_omset = df_periode["jumlah"].sum()

        # 5. KALKULASI GAJI & BONUS
        total_gaji_pokok = gaji_harian_input * jumlah_hari_kerja
        total_nominal_bonus = (persen_bonus_input / 100) * total_omset
        grand_total_gaji = total_gaji_pokok + total_nominal_bonus

        # 6. RINGKASAN SLIP GAJI
        st.markdown("### 🧾 Rincian Slip Gaji Periode")

        st.info(
            f"📍 **Omset Penjualan Toko ({tgl_mulai} s/d {tgl_selesai}):** Rp"
            f" {total_omset:,.0f}"
        )

        res_c1, res_c2, res_c3 = st.columns(3)
        res_c1.metric(
            "Total Gaji Pokok",
            f"Rp {total_gaji_pokok:,.0f}",
            delta=f"{jumlah_hari_kerja} hari x Rp {gaji_harian_input:,.0f}",
        )
        res_c2.metric(
            "Bonus Penjualan",
            f"Rp {total_nominal_bonus:,.0f}",
            delta=f"{persen_bonus_input}% dari Omset",
        )
        res_c3.metric(
            "TOTAL GAJI DITERIMA",
            f"Rp {grand_total_gaji:,.0f}",
            delta="Gaji Pokok + Bonus",
        )

    # TAB 2: MASTER TARIF DASAR (Atur Standar per Karyawan)
    with tab_g2:
      st.subheader("Atur Standar Tarif Harian & Persentase Bonus")
      st.dataframe(
          karyawan_df[
              [
                  "username",
                  "nama",
                  "gaji_per_hari",
                  "persen_bonus",
              ]
          ].rename(
              columns={
                  "gaji_per_hari": "Gaji per Hari (Rp)",
                  "persen_bonus": "Bonus Default (%)",
              }
          ),
          use_container_width=True,
      )

      st.markdown("---")
      with st.form("form_master_gaji"):
        user_to_edit = st.selectbox(
            "Pilih Karyawan yang Ingin Diatur",
            options=list(karyawan_options.keys()),
            format_func=lambda x: karyawan_options[x],
        )
        m_gaji = st.number_input(
            "Standar Gaji per Hari (Rp)", min_value=0.0, step=5000.0
        )
        m_bonus = st.number_input(
            "Standar Bonus (%)", min_value=0.0, max_value=100.0, step=0.5
        )
        btn_save_master = st.form_submit_button("Simpan Standar Baru")

        if btn_save_master:
          update_gaji_user(user_to_edit, m_gaji, m_bonus)
          st.success("✅ Standar tarif harian & bonus berhasil diperbarui!")
          st.rerun()

  # --------------------------------------------------
  # MENU 4: KELOLA & HAPUS DATA
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
