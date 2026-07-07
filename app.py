import streamlit as st
import pandas as pd
import datetime

# 1. Konfigurasi Halaman
st.set_page_config(page_title="Sistem Absensi Siswa", page_icon="🏫", layout="wide")

# Judul
st.title("🏫 Sistem Absensi Siswa dengan Barcode")
st.markdown("Scan barcode siswa untuk mencatat kehadiran secara otomatis.")

# 2. Sidebar untuk Navigasi
menu = ["Absensi Masuk", "Laporan Hari Ini", "Data Master Siswa"]
choice = st.sidebar.selectbox("Menu", menu)

# 3. Fungsi Dummy untuk simulasi (Karena kita belum connect database asli)
# Dalam implementasi nyata, ini akan membaca Google Sheets
if choice == "Data Master Siswa":
    st.header("📋 Data Master Siswa (Contoh)")
    # Data contoh (Nanti diganti dengan load dari Google Sheet)
    data_siswa = pd.DataFrame({
        'NISN': ['1001', '1002', '1003', '1004'],
        'Nama': ['Budi Santoso', 'Siti Aminah', 'Ahmad Rizki', 'Dewi Lestari'],
        'Kelas': ['10A', '10B', '10A', '11A']
    })
    st.dataframe(data_siswa)
    st.info("💡 Di aplikasi nyata, data ini diambil langsung dari Google Sheet Anda.")

elif choice == "Absensi Masuk":
    st.header("📸 Scan Barcode Siswa")

    # Simulasi input (Karena scan kamera butuh library tambahan di backend)
    # Di aplikasi nyata, kita akan menggunakan st.camera_input dan library barcode

    nisn_input = st.text_input("Masukkan NISN (Simulasi Scan):", placeholder="Scan barcode di sini...")

    if st.button("Cek Kehadiran"):
        if not nisn_input:
            st.warning("⚠️ Silakan masukkan NISN atau scan barcode.")
        else:
            # Logika sederhana
            if nisn_input in ['1001', '1002', '1003', '1004']:
                st.success(f"✅ Berhasil! Siswa dengan NISN {nisn_input} telah absen.")
                # Di sini akan ada kode untuk menyimpan ke Google Sheet
            else:
                st.error("❌ NISN tidak ditemukan!")

elif choice == "Laporan Hari Ini":
    st.header("📊 Laporan Kehadiran")
    st.write("Data absensi hari ini akan muncul di sini.")
    # Simulasi data laporan
    data_laporan = pd.DataFrame({
        'Waktu': ['07:05', '07:10', '07:15'],
        'NISN': ['1001', '1003', '1002'],
        'Nama': ['Budi Santoso', 'Ahmad Rizki', 'Siti Aminah'],
        'Status': ['Hadir', 'Hadir', 'Hadir']
    })
    st.dataframe(data_laporan)

    # Tombol Download
    csv = data_laporan.to_csv(index=False).encode('utf-8')
    st.download_button(
        "📥 Unduh Laporan (CSV)",
        csv,
        "laporan_absensi.csv",
        "text/csv",
        key='download-csv'
    )
