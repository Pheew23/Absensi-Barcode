import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime
import cv2
import numpy as np
from pyzbar.pyzbar import decode

# --- KONFIGURASI HALAMAN ---
st.set_page_config(page_title="Absensi QR Code", page_icon="🏫", layout="wide")

st.title("🏫 Sistem Absensi Siswa via QR Code")
st.markdown("Arahkan kamera ke QR Code siswa untuk absen.")

# --- SIDEBAR ---
st.sidebar.header("⚙️ Pengaturan")
sheet_id = st.sidebar.text_input("ID Google Sheet:", placeholder="1aBcD...")
use_mock = st.sidebar.checkbox("Mode Simulasi (Tanpa Database)", value=False)

if not sheet_id and not use_mock:
    st.warning("⚠️ Masukkan ID Google Sheet atau aktifkan Mode Simulasi.")
    st.stop()

# --- FUNGSI KONEKSI GOOGLE SHEETS ---
def get_data_siswa():
    if use_mock:
        return pd.DataFrame({'NISN': ['1001', '1002'], 'Nama': ['Budi', 'Siti'], 'Kelas': ['10A', '10B']})

    try:
        json_str = st.secrets["creds"]
        import json
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

# --- FUNGSI SCAN GAMBAR ---
def scan_qr_from_image(image_bytes):
    try:
        # Konversi bytes ke array numpy
        nparr = np.frombuffer(image_bytes, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

        # Decode QR Code
        decoded_objects = decode(img)

        if decoded_objects:
            # Ambil data dari objek pertama yang ditemukan
            return decoded_objects[0].data.decode('utf-8')
        return None
    except Exception as e:
        st.error(f"Error saat memproses gambar: {e}")
        return None

# --- LOGIKA UTAMA ---
data_siswa_db = get_data_siswa()

st.subheader("📸 Scan QR Code Siswa")
camera_input = st.camera_input("Ambil Gambar QR Code")

if camera_input:
    with st.spinner("Sedang memindai..."):
        qr_data = scan_qr_from_image(camera_input.getvalue())

        if qr_data:
            st.success(f"✅ QR Code Terbaca: **{qr_data}**")

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
                            import json
                            creds_dict = json.loads(json_str)
                            scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
                            creds = Credentials.from_service_account_info(creds_dict, scopes=scope)
                            client = gspread.authorize(creds)
                            sh = client.open_by_key(sheet_id)
                            sheet_absen = sh.worksheet("Absensi")

                            # Cek duplikasi (sederhana)
                            data_absen = pd.DataFrame(sheet_absen.get_all_records())
                            today = datetime.now().strftime("%Y-%m-%d")
                            # Logika cek duplikasi bisa diperbaiki di sini

                            sheet_absen.append_row([waktu, str(qr_data), nama, kelas])
                            st.balloons()
                            st.success(f"✅ Berhasil! {nama} ({kelas}) absen pukul {waktu}")
                            st.success("Data tersimpan ke Google Sheets.")
                        except Exception as e:
                            st.error(f"Gagal simpan ke Sheets: {e}")
                else:
                    st.error("❌ NISN tidak ditemukan.")
            else:
                st.error("❌ Database siswa tidak dapat dimuat.")
        else:
            st.warning("⚠️ QR Code tidak terbaca. Pastikan pencahayaan cukup dan kode jelas.")

# --- LAPORAN ---
st.divider()
st.subheader("📊 Laporan")
if use_mock:
    st.dataframe(pd.DataFrame({'Waktu': ['07:00'], 'Nama': ['Budi']}))
else:
    try:
        json_str = st.secrets["creds"]
        import json
        creds_dict = json.loads(json_str)
        scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
        creds = Credentials.from_service_account_info(creds_dict, scopes=scope)
        client = gspread.authorize(creds)
        sh = client.open_by_key(sheet_id)
        sheet_absen = sh.worksheet("Absensi")
        df = pd.DataFrame(sheet_absen.get_all_records())
        st.dataframe(df)
    except:
        st.info("Belum ada data atau error koneksi.")
