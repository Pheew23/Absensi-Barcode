import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime
import json

# --- KONFIGURASI ---
st.set_page_config(page_title="Absensi Siswa", page_icon="🏫", layout="wide")

st.title("🏫 Absensi Siswa Cepat")
st.markdown("""
**Cara Menggunakan:**
1. Scan QR Code siswa menggunakan aplikasi kamera/QR Reader di HP Anda.
2. Salin NISN yang muncul.
3. Tempel (Paste) di kolom di bawah ini dan tekan 'Absen'.
""")

# --- SIDEBAR ---
st.sidebar.header("⚙️ Pengaturan")
sheet_id = st.sidebar.text_input("ID Google Sheet:", placeholder="Masukkan ID Sheet di sini...")
use_mock = st.sidebar.checkbox("Mode Simulasi (Tanpa Database)", value=False)

if not sheet_id and not use_mock:
    st.warning("⚠️ Harap masukkan ID Google Sheet atau aktifkan Mode Simulasi untuk melanjutkan.")
    st.stop()

# --- FUNGSI KONEKSI GOOGLE SHEETS ---
def get_data_siswa():
    if use_mock:
        return pd.DataFrame({'NISN': ['1001', '1002', '1003'], 'Nama': ['Budi', 'Siti', 'Ahmad'], 'Kelas': ['10A', '10B', '10A']})

    try:
        json_str = st.secrets["creds"]
        creds_dict = json.loads(json_str)
        scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
        creds = Credentials.from_service_account_info(creds_dict, scopes=scope)
        client = gspread.authorize(creds)
        sh = client.open_by_key(sheet_id)
        sheet_master = sh.worksheet("DataSiswa")
        return pd.DataFrame(sheet_master.get_all_records())
    except Exception as e:
        st.error(f"⚠️ Gagal mengambil data siswa: {e}")
        return None

def save_absensi(nisn, nama, kelas, waktu):
    try:
        json_str = st.secrets["creds"]
        creds_dict = json.loads(json_str)
        scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
        creds = Credentials.from_service_account_info(creds_dict, scopes=scope)
        client = gspread.authorize(creds)
        sh = client.open_by_key(sheet_id)
        sheet_absen = sh.worksheet("Absensi")

        # Cek duplikasi hari ini (Sederhana)
        data_absen = pd.DataFrame(sheet_absen.get_all_records())
        today = datetime.now().strftime("%Y-%m-%d")

        # Cek apakah sudah absen hari ini
        sudah_absen = False
        if not data_absen.empty:
            # Cek apakah ada baris dengan NISN yang sama dan tanggal hari ini
            # Kita asumsikan kolom 'Waktu' berisi format YYYY-MM-DD HH:MM:SS
            for index, row in data_absen.iterrows():
                if str(row['NISN']) == str(nisn) and today in str(row['Waktu']):
                    sudah_absen = True
                    break

        if sudah_absen:
            return "sudah_absen", None

        sheet_absen.append_row([waktu, str(nisn), nama, kelas])
        return "sukses", None
    except Exception as e:
        return "error", str(e)

# --- LOGIKA UTAMA ---
data_siswa_db = get_data_siswa()

col1, col2 = st.columns([1, 1])

with col1:
    st.subheader("📝 Input Absensi")
    nisn_input = st.text_input("Tempel NISN Siswa di sini:", placeholder="Contoh: 1001", key="input_nisn")

    if st.button("✅ Absen Sekarang", type="primary"):
        if not nisn_input:
            st.warning("⚠️ Harap masukkan NISN.")
        elif data_siswa_db is None:
            st.error("⚠️ Database tidak tersedia.")
        else:
            # Validasi Siswa
            if str(nisn_input) in data_siswa_db['NISN'].astype(str).values:
                siswa = data_siswa_db[data_siswa_db['NISN'].astype(str) == str(nisn_input)].iloc[0]
                nama = siswa['Nama']
                kelas = siswa['Kelas']
                waktu = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

                if use_mock:
                    st.balloons()
                    st.success(f"🎉 **Berhasil!**\n\n**Nama:** {nama}\n**Kelas:** {kelas}\n**Waktu:** {waktu}\n*(Mode Simulasi)*")
                else:
                    status, err_msg = save_absensi(nisn_input, nama, kelas, waktu)

                    if status == "sukses":
                        st.balloons()
                        st.success(f"🎉 **Berhasil!**\n\n**Nama:** {nama}\n**Kelas:** {kelas}\n**Waktu:** {waktu}")
                        st.success("✅ Data tersimpan ke Google Sheets.")
                        # Reset input
                        st.rerun()
                    elif status == "sudah_absen":
                        st.warning(f"⚠️ **Sudah Absen!**\n\nSiswa **{nama}** sudah melakukan absensi hari ini.")
                    else:
                        st.error(f"❌ Gagal menyimpan data: {err_msg}")
            else:
                st.error(f"❌ **NISN Tidak Ditemukan!**\n\nSiswa dengan NISN '{nisn_input}' tidak ada di database.")

with col2:
    st.subheader("📊 Daftar Siswa Terdaftar")
    if data_siswa_db is not None and not data_siswa_db.empty:
        st.dataframe(data_siswa_db, use_container_width=True)
    else:
        st.info("Belum ada data siswa atau mode simulasi aktif.")

# --- LAPORAN REAL-TIME ---
st.divider()
st.subheader("📋 Laporan Absensi Hari Ini")

if use_mock:
    st.dataframe(pd.DataFrame({'Waktu': ['07:00'], 'NISN': ['1001'], 'Nama': ['Budi'], 'Kelas': ['10A']}))
else:
    try:
        json_str = st.secrets["creds"]
        creds_dict = json.loads(json_str)
        scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
        creds = Credentials.from_service_account_info(creds_dict, scopes=scope)
        client = gspread.authorize(creds)
        sh = client.open_by_key(sheet_id)
        sheet_absen = sh.worksheet("Absensi")
        df = pd.DataFrame(sheet_absen.get_all_records())

        if not df.empty:
            # Filter hanya hari ini (opsional, tapi bagus)
            today_str = datetime.now().strftime("%Y-%m-%d")
            df_hari_ini = df[df['Waktu'].astype(str).str.contains(today_str)]

            st.dataframe(df_hari_ini, use_container_width=True)

            # Tombol Download
            csv = df.to_csv(index=False).encode('utf-8')
            st.download_button(
                "📥 Unduh Semua Data (CSV)",
                csv,
                "laporan_absensi.csv",
                "text/csv",
                key='download-csv'
            )
        else:
            st.info("Belum ada data absensi hari ini.")
    except Exception as e:
        st.error(f"⚠️ Gagal memuat laporan: {e}")
