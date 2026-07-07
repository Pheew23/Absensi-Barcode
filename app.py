import streamlit as st
import pandas as pd
import datetime
import time

# Konfigurasi Halaman
st.set_page_config(
    page_title="RapatOnline Pro",
    page_icon="🎥",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- Inisialisasi Session State ---
if 'meeting_active' not in st.session_state:
    st.session_state.meeting_active = False
if 'meeting_room_id' not in st.session_state:
    st.session_state.meeting_room_id = ""
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []
if 'participants' not in st.session_state:
    st.session_state.participants = []

# --- Sidebar: Informasi & Kontrol ---
st.sidebar.title("🎛️ Kontrol Rapat")
st.sidebar.markdown("### Status Sistem")

status_options = ["Menunggu", "Sedang Berlangsung", "Selesai"]
current_status = st.sidebar.selectbox("Status Rapat", status_options, index=1 if st.session_state.meeting_active else 0)

# Update status berdasarkan input
if current_status == "Sedang Berlangsung" and not st.session_state.meeting_active:
    st.session_state.meeting_active = True
    st.session_state.meeting_room_id = f"rapat-{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}"
elif current_status != "Sedang Berlangsung":
    st.session_state.meeting_active = False
    st.session_state.meeting_room_id = ""

st.sidebar.divider()

# Input Peserta
st.sidebar.subheader("Daftar Peserta")
new_participant = st.sidebar.text_input("Tambah Peserta Baru")
if st.sidebar.button("Tambah"):
    if new_participant:
        st.session_state.participants.append(new_participant)
        st.sidebar.success(f"{new_participant} ditambahkan!")

# Tampilkan daftar peserta
if st.session_state.participants:
    st.sidebar.markdown("### Daftar Hadir")
    for i, p in enumerate(st.session_state.participants):
        st.sidebar.write(f"{i+1}. {p}")

# --- Area Utama ---

st.title("🎥 Platform Rapat Online Terintegrasi")

if not st.session_state.meeting_active:
    # Tampilan Awal: Jadwal & Info
    st.info("👋 Silakan ubah status di sidebar menjadi **'Sedang Berlangsung'** untuk memulai ruang rapat virtual.")

    col1, col2 = st.columns(2)
    with col1:
        st.markdown("### 📅 Fitur Utama")
        st.write("""
        - **Jadwal Rapat**: Buat dan kelola jadwal.
        - **Ruang Virtual**: Integrasi video call tanpa instalasi tambahan.
        - **Notulen Otomatis**: Catat poin penting selama rapat.
        - **Chat Real-time**: Diskusi teks pendamping.
        """)

    with col2:
        st.markdown("### 📋 Daftar Rapat Terakhir")
        # Dummy data untuk demonstrasi
        df_history = pd.DataFrame({
            "Topik": ["Review Q3", "Brainstorming Produk", "Onboarding Karyawan"],
            "Tanggal": ["2023-10-25", "2023-10-26", "2023-10-27"],
            "Peserta": ["5", "8", "12"]
        })
        st.dataframe(df_history, use_container_width=True)

else:
    # Tampilan Aktif: Video Call & Tools
    st.success(f"Rapat sedang berlangsung! ID Ruang: `{st.session_state.meeting_room_id}`")

    # Layout Grid: Video di Kiri, Tools di Kanan
    col_video, col_tools = st.columns([3, 1])

    with col_video:
        st.subheader("🎥 Ruang Rapat Virtual")
        st.markdown("""
        Menggunakan **Jitsi Meet** (Open Source). 
        *Catatan: Jika Anda berada di balik firewall korporat, pastikan port 443/8443 terbuka.*
        """)

        # URL Jitsi Meet dengan ID unik
        jitsi_url = f"https://meet.jit.si/{st.session_state.meeting_room_id}"

        # Embed Jitsi dalam Iframe dengan tinggi penuh
        st.markdown(
            f"""
            <iframe 
                src="{jitsi_url}" 
                width="100%" 
                height="600px" 
                allow="camera; microphone; fullscreen; display-capture; autoplay" 
                style="border: 1px solid #ddd; border-radius: 8px;">
            </iframe>
            """,
            unsafe_allow_html=True
        )

        st.warning("💡 **Tips**: Pastikan izin kamera dan mikrofon browser Anda sudah diizinkan.")

    with col_tools:
        st.subheader("📝 Notulen & Chat")

        # Tab untuk Notulen dan Chat
        tab1, tab2 = st.tabs(["Notulen", "Chat"])

        with tab1:
            note = st.text_area("Catat poin penting rapat:")
            if st.button("Simpan Catatan"):
                if note:
                    timestamp = datetime.datetime.now().strftime("%H:%M")
                    st.session_state.chat_history.append(f"[{timestamp}] 📝 **Catatan**: {note}")
                    st.success("Catatan disimpan!")
                    st.rerun()
            else:
                st.write("Belum ada catatan.")

        with tab2:
            chat_input = st.text_input("Kirim pesan ke peserta...")
            if st.button("Kirim"):
                if chat_input:
                    timestamp = datetime.datetime.now().strftime("%H:%M")
                    st.session_state.chat_history.append(f"[{timestamp}] 💬 **Anda**: {chat_input}")
                    st.rerun()

            st.divider()
            st.markdown("### Riwayat Chat")
            for msg in st.session_state.chat_history:
                st.markdown(msg)

# --- Footer ---
st.divider()
st.caption("Dibangun dengan Streamlit & Jitsi Meet. Aplikasi ini berjalan di browser Anda sepenuhnya.")
