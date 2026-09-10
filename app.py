from datetime import date, datetime
import sqlite3
import pandas as pd
import streamlit as st

# ==========================================
# 1. KONFIGURASI HALAMAN STREAMLIT
# ==========================================
st.set_page_config(
    page_title="Sistem Rekap Toko & Gaji",
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
            gaji_dasar REAL DEFAULT 0,
            persen_bonus REAL DEFAULT 0
        )
    """)

  # Cek & Tambah Kolom Gaji jika DB lama sudah terbentuk
  c.execute("PRAGMA table_info(users)")
  columns = [col[1] for col in c.fetchall()]
  if "gaji_dasar" not in columns:
    c.execute("ALTER TABLE users ADD COLUMN gaji_dasar REAL DEFAULT 0")
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

  # Buat Akun Default jika belum ada
  c.execute("SELECT COUNT(*) FROM users")
  if c.fetchone()[0] == 0:
    c.execute(
        "INSERT INTO users (username, password, role, nama, gaji_dasar,"
        " persen_bonus) VALUES ('admin', 'admin123', 'admin', 'Owner Toko', 0,"
        " 0)"
    )
    c.execute(
        "INSERT INTO users (username, password, role, nama, gaji_dasar,"
        " persen_bonus) VALUES ('karyawan', 'karyawan123', 'karyawan', 'Staf"
        " Kasir', 1500000, 2.5)"
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
      "SELECT username, nama, role, gaji_dasar, persen_bonus FROM users", conn
  )
  conn.close()
  return df


def update_gaji_user(username, gaji_dasar, persen_bonus):
  conn = get_connection()
  c = conn.cursor()
  c.execute(
      "UPDATE users SET gaji_dasar = ?, persen_bonus = ? WHERE username = ?",
      (gaji_dasar, persen_bonus, username),
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

  # Navigasi berdasarkan Role
  if st.session_state.role == "admin":
    menu = st.sidebar.radio(
        "Navigasi Menu",
        [
            "📊 Dashboard & Laporan",
            "✍️ Form Input Transaksi",
            "💵 Fitur Gaji & Bonus Karyawan",
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
  # MENU 3: FITUR GAJI & BONUS (Khusus Admin/Owner)
  # --------------------------------------------------
  elif menu == "💵 Fitur Gaji & Bonus Karyawan":
    st.title("💵 Manajemen Gaji & Bonus Karyawan")

    tab_g1, tab_g2 = st.tabs(
        ["⚙️ Pengaturan Gaji & Bonus", "🧾 Rekapitulasi Gaji Periode"]
    )

    # Tab 1: Setting Gaji Dasar dan Persentase Bonus
    with tab_g1:
      st.subheader("Atur Gaji Dasar & Bonus per Karyawan")
      df_u = load_users()

      # Tampilkan tabel daftar pengguna saat ini
      st.dataframe(
          df_u[
              [
                  "username",
                  "nama",
                  "role",
                  "gaji_dasar",
                  "persen_bonus",
              ]
          ].rename(
              columns={
                  "gaji_dasar": "Gaji Dasar (Rp)",
                  "persen_bonus": "Bonus (%)",
              }
          ),
          use_container_width=True,
      )

      st.markdown("---")
      st.write("**Form Edit Gaji & Bonus:**")

      user_list = df_u["username"].tolist()
      selected_user = st.selectbox("Pilih Karyawan / User", options=user_list)

      # Ambil nilai default user yang dipilih
      current_data = df_u[df_u["username"] == selected_user].iloc[0]

      with st.form("form_edit_gaji"):
        new_gaji = st.number_input(
            "Gaji Dasar (Rp)",
            value=float(current_data["gaji_dasar"]),
            step=50000.0,
            format="%.0f",
        )
        new_bonus = st.number_input(
            "Bonus Penjualan (%)",
            value=float(current_data["persen_bonus"]),
            min_value=0.0,
            max_value=100.0,
            step=0.5,
        )
        btn_save_gaji = st.form_submit_button("Simpan Pengaturan Gaji")

        if btn_save_gaji:
          update_gaji_user(selected_user, new_gaji, new_bonus)
          st.success(
              f"✅ Gaji & Bonus untuk {selected_user} berhasil diperbarui!"
          )
          st.rerun()

    # Tab 2: Hitung Total Gaji berdasarkan Periode
    with tab_g2:
      st.subheader("Hitung Gaji & Bonus Penjualan")

      col_t1, col_t2 = st.columns(2)
      with col_t1:
        tgl_awal = st.date_input("Dari Tanggal", value=date.today().replace(day=1))
      with col_t2:
        tgl_akhir = st.date_input("Sampai Tanggal", value=date.today())

      # Filter Penjualan pada Rentang Tanggal
      df_penjualan = load_penjualan()
      if not df_penjualan.empty:
        df_penjualan["tanggal"] = pd.to_datetime(df_penjualan["tanggal"]).dt.date
        mask = (df_penjualan["tanggal"] >= tgl_awal) & (
            df_penjualan["tanggal"] <= tgl_akhir
        )
        df_filtered = df_penjualan.loc[mask]
        total_omset_periode = df_filtered["jumlah"].sum()
      else:
        total_omset_periode = 0.0

      st.info(
          f"📌 Total Omset Penjualan Toko ({tgl_awal} s/d {tgl_akhir}): **Rp"
          f" {total_omset_periode:,.0f}**"
      )

      # Kalkulasi untuk setiap karyawan
      df_users = load_users()
      karyawan_list = df_users[df_users["role"] == "karyawan"]

      hasil_gaji = []
      for idx, row in karyawan_list.iterrows():
        g_dasar = row["gaji_dasar"]
        p_bonus = row["persen_bonus"]
        nominal_bonus = (p_bonus / 100) * total_omset_periode
        total_gaji = g_dasar + nominal_bonus

        hasil_gaji.append({
            "Nama Karyawan": row["nama"],
            "Gaji Dasar (Rp)": f"{g_dasar:,.0f}",
            "Bonus (%)": f"{p_bonus}%",
            "Nominal Bonus (Rp)": f"{nominal_bonus:,.0f}",
            "TOTAL GAJI (Rp)": f"{total_gaji:,.0f}",
        })

      st.write("### 📋 Rincian Slip Gaji Karyawan")
      st.table(pd.DataFrame(hasil_gaji))

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
