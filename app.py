import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime
import json

# --- KONFIGURASI ---
st.set_page_config(page_title="Absensi QR Code", page_icon="🏫", layout="wide")

st.title("🏫 Sistem Absensi Siswa via QR Code")
st.markdown("Scan QR Code siswa untuk absen.")

# --- SIDEBAR ---
st.sidebar.header("⚙️ Pengaturan")
sheet_id = st.sidebar.text_input("ID Google Sheet:", placeholder="1aBcD...")
use_mock = st.sidebar.checkbox("Mode Simulasi (Tanpa Database)", value=False)

if not sheet_id and not use_mock:
    st.warning("⚠️ Masukkan ID Google Sheet atau aktifkan Mode Simulasi.")
    st.stop()

# --- IMPORT LIBRARY SCANNER (Versi Ringan) ---
# Kita akan mencoba import, jika gagal, kita pakai fallback manual
try:
    from streamlit_qr_scanner import qr_scanner
    HAS_SCANNER = True
except ImportError:
    HAS_SCANNER = False
    st.warning("⚠️ Library scanner tidak ditemukan. Gunakan Mode Simulasi atau ketik manual.")

# --- FUNGSI KONEKSI GOOGLE SHEETS ---
def get_data_siswa():
    if use_mock:
        return pd.DataFrame({'NISN': ['1001', '1002'], 'Nama': ['Budi', 'Siti'], 'Kelas': ['10A', '10B']})

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
        st.error(f"Gagal koneksi: {e}")
        return None

# --- LOGIKA UTAMA ---
data_siswa_db = get_data_siswa()

st.subheader("📸 Scan QR Code Siswa")

qr_data = None

if HAS_SCANNER:
    # Gunakan komponen scanner
    result = qr_scanner("Scan QR Code di sini")
    if result:
        qr_data = result['data']
        st.success(f"✅ Terdeteksi: {qr_data}")
else:
    # Fallback: Upload Gambar atau Input Manual
    st.info("📷 Mode Manual (Scanner tidak aktif di server ini).")
    option = st.radio("Pilih cara input:", ["Upload Gambar QR", "Ketik NISN Manual"])

    if option == "Ketik NISN Manual":
        qr_data = st.text_input("Masukkan NISN Siswa:", placeholder="Contoh: 1001")
    elif option == "Upload Gambar QR":
        uploaded_file = st.file_uploader("Upload Foto QR Code", type=['png', 'jpg', 'jpeg'])
        if uploaded_file:
            # Di sini kita bisa coba decode manual dengan library ringan jika ada, 
            # atau biarkan user mengetik hasil scan dari gambar.
            st.warning("⚠️ Karena keterbatasan server, silakan baca QR dari foto dan ketik NISN-nya di bawah.")
            qr_data = st.text_input("Ketik NISN dari foto:", placeholder="Contoh: 1001")

# --- PROSES ABSENSI ---
if qr_data:
    st.divider()
    if data_siswa_db is not None:
        if str(qr_data) in data_siswa_db['NISN'].astype(str).values:
            siswa = data_siswa_db[data_siswa_db['NISN'].astype(str) == str(qr_data)].iloc[0]
            nama = siswa['Nama']
            kelas = siswa['Kelas']
            waktu = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            if use_mock:
                st.balloons()
                st.success(f"Simulasi: {nama} ({kelas}) absen pukul {waktu}")
            else:
                try:
                    json_str = st.secrets["creds"]
                    creds_dict = json.loads(json_str)
                    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
                    creds = Credentials.from_service_account_info(creds_dict, scopes=scope)
                    client = gspread.authorize(creds)
                    sh = client.open_by_key(sheet_id)
                    sheet_absen = sh.worksheet("Absensi")

                    sheet_absen.append_row([waktu, str(qr_data), nama, kelas])
                    st.balloons()
                    st.success(f"✅ Berhasil! {nama} ({kelas}) absen pukul {waktu}")
                    st.success("Data tersimpan ke Google Sheets.")
                except Exception as e:
                    st.error(f"Gagal simpan: {e}")
        else:
            st.error(f"❌ NISN {qr_data} tidak ditemukan di database.")
    else:
        st.error("❌ Database siswa tidak dapat dimuat.")

# --- LAPORAN ---
st.divider()
st.subheader("📊 Laporan")
if use_mock:
    st.dataframe(pd.DataFrame({'Waktu': ['07:00'], 'Nama': ['Budi']}))
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
        st.dataframe(df)
    except:
        st.info("Belum ada data.")
