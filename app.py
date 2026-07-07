import streamlit as st
import pandas as pd
import datetime
import time
import random

# --- Konfigurasi Halaman & CSS Kustom ---
st.set_page_config(
    page_title="RapatHub - Tanpa Login",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# CSS Kustom untuk Tampilan Modern (Glassmorphism & Gradient)
st.markdown("""
<style>
    /* Background Gradient */
    .stApp {
        background: linear-gradient(135deg, #1e1e2f 0%, #2a2a40 100%);
        color: #ffffff;
    }

    /* Container Utama dengan Glass Effect */
    .main-container {
        background: rgba(255, 255, 255, 0.05);
        backdrop-filter: blur(10px);
        border-radius: 20px;
        padding: 30px;
        border: 1px solid rgba(255, 255, 255, 0.1);
        box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.37);
    }

    /* Judul dengan Gradasi */
    h1, h2, h3 {
        background: -webkit-linear-gradient(45deg, #00c6ff, #0072ff);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: 800;
    }

    /* Tombol Modern */
    .stButton>button {
        background: linear-gradient(45deg, #00c6ff, #0072ff);
        color: white;
        border: none;
        border-radius: 50px;
        padding: 10px 25px;
        font-weight: bold;
        transition: all 0.3s;
        box-shadow: 0 4px 15px rgba(0, 198, 255, 0.4);
    }
    .stButton>button:hover {
        transform: scale(1.05);
        box-shadow: 0 6px 20px rgba(0, 198, 255, 0.6);
    }

    /* Input Text Modern */
    .stTextInput>div>div>input {
        background-color: rgba(255, 255, 255, 0.1);
        color: white;
        border: 1px solid rgba(255, 255, 255, 0.2);
        border-radius: 10px;
    }

    /* Chat Bubble */
    .chat-bubble {
        background: rgba(255, 255, 255, 0.1);
        padding: 10px;
        border-radius: 10px;
        margin-bottom: 5px;
        border-left: 4px solid #00c6ff;
    }

    /* Statistik Card */
    .stat-card {
        background: rgba(255, 255, 255, 0.05);
        padding: 15px;
        border-radius: 15px;
        text-align: center;
        border: 1px solid rgba(255, 255, 255, 0.1);
    }
    .stat-value {
        font-size: 2em;
        font-weight: bold;
        color: #00c6ff;
    }
</style>
""", unsafe_allow_html=True)

# --- Inisialisasi Session State ---
if 'joined' not in st.session_state:
    st.session_state.joined = False
if 'username' not in st.session_state:
    st.session_state.username = "Guest"
if 'meeting_id' not in st.session_state:
    st.session_state.meeting_id = ""
if 'meeting_start' not in st.session_state:
    st.session_state.meeting_start = None
if 'chat_log' not in st.session_state:
    st.session_state.chat_log = []
if 'notes' not in st.session_state:
    st.session_state.notes = []
if 'reactions' not in st.session_state:
    st.session_state.reactions = {"👍": 0, "🔥": 0, "🎉": 0}

# --- Bagian Login yang Dimodifikasi ---
if not st.session_state.joined:
    st.markdown("<h1 style='text-align: center;'>🚀 RapatHub: Masuk Tanpa Login</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: #ccc;'>Masuk ke ruang rapat yang sudah dibuat Host.</p>", unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("### 🎤 Masukkan Detail Rapat")

        # 1. Input Nama
        name_input = st.text_input("Nama Anda", placeholder="Contoh: Budi")

        # 2. Input Kode Ruang (Ini kuncinya!)
        # Kita cek apakah ada kode dari URL (untuk sharing link)
        query_params = st.query_params
        room_code_from_url = query_params.get("room", [""])[0]

        room_input = st.text_input("Kode Ruang Rapat", value=room_code_from_url, placeholder="Contoh: RapatTimMarketing")

        if st.button("🚀 Masuk Sekarang"):
            if name_input and room_input:
                # Simpan data
                st.session_state.username = name_input
                st.session_state.joined = True
                st.session_state.meeting_id = room_input # Gunakan kode yang dimasukkan

                # Tambahkan kode ke URL agar bisa dibagikan lagi jika perlu
                st.query_params["room"] = room_input

                st.session_state.meeting_start = datetime.datetime.now()
                st.session_state.chat_log = [] # Reset chat (opsional)
                st.session_state.notes = []
                st.success(f"Berhasil masuk ke ruang: **{room_input}**!")
                st.rerun()
            else:
                st.error("Mohon isi Nama dan Kode Ruang!")

else:
    # --- Halaman Utama Rapat ---

    # Header dengan Durasi & User
    col_header, col_timer = st.columns([3, 1])
    with col_header:
        st.markdown(f"### 👋 Halo, **{st.session_state.username}**! | ID Ruang: `{st.session_state.meeting_id}`")
    with col_timer:
        # Hitung durasi real-time
        if st.session_state.meeting_start:
            duration = datetime.datetime.now() - st.session_state.meeting_start
            hours, remainder = divmod(int(duration.total_seconds()), 3600)
            minutes, seconds = divmod(remainder, 60)
            st.markdown(f"⏱️ Durasi: `{hours:02d}:{minutes:02d}:{seconds:02d}`")

    st.divider()

    # Layout Utama: Kiri (Video), Kanan (Tools)
    col_video, col_tools = st.columns([2, 1])

    with col_video:
        st.markdown("### 🎥 Ruang Rapat Virtual")
        st.markdown("Klik tombol di dalam video untuk mengaktifkan kamera/mikrofon.")

        # Embed Jitsi Meet
        jitsi_url = f"https://meet.jit.si/{st.session_state.meeting_id}"

        # Jikarame responsif
        st.markdown(f"""
        <div style="position: relative; padding-bottom: 56.25%; height: 0; overflow: hidden; border-radius: 15px; box-shadow: 0 10px 30px rgba(0,0,0,0.5);">
            <iframe src="{jitsi_url}" style="position: absolute; top: 0; left: 0; width: 100%; height: 100%; border: 0;" allow="camera; microphone; fullscreen; display-capture; autoplay"></iframe>
        </div>
        """, unsafe_allow_html=True)

        st.info("💡 **Tips**: Gunakan headphone untuk pengalaman audio terbaik.")

    with col_tools:
        st.markdown("### 🛠️ Papan Kontrol Rapat")

        # Tab untuk Chat, Notulen, dan Reaksi
        tab_chat, tab_notes, tab_react = st.tabs(["💬 Chat", "📝 Notulen", "🎉 Reaksi"])

        with tab_chat:
            st.markdown("### Obrolan Cepat")

            # Render Chat History
            chat_container = st.container()
            with chat_container:
                for entry in st.session_state.chat_log:
                    style = "background: rgba(255,255,255,0.1); padding: 8px; border-radius: 8px; margin-bottom: 5px;"
                    if entry['user'] == st.session_state.username:
                        style += " border-left: 3px solid #00c6ff;"
                    else:
                        style += " border-left: 3px solid #ff4b4b;"

                    st.markdown(f"""
                    <div style="{style}">
                        <small style="color: #aaa;">{entry['time']}</small><br>
                        <strong>{entry['user']}:</strong> {entry['msg']}
                    </div>
                    """, unsafe_allow_html=True)

            # Input Chat
            new_msg = st.text_input("Ketik pesan...", key="chat_input")
            if st.button("Kirim"):
                if new_msg:
                    time_now = datetime.datetime.now().strftime("%H:%M")
                    st.session_state.chat_log.append({
                        "time": time_now,
                        "user": st.session_state.username,
                        "msg": new_msg
                    })
                    st.rerun()

        with tab_notes:
            st.markdown("### 📝 Catat Poin Penting")
            note_input = st.text_area("Tulis notulen di sini...")
            if st.button("Simpan Notulen"):
                if note_input:
                    time_now = datetime.datetime.now().strftime("%H:%M")
                    st.session_state.notes.append({
                        "time": time_now,
                        "content": note_input
                    })
                    st.success("Notulen tersimpan!")
                    st.rerun()

            st.markdown("### Riwayat Notulen")
            if not st.session_state.notes:
                st.write("Belum ada notulen.")
            else:
                for n in st.session_state.notes:
                    st.markdown(f"🕒 **{n['time']}**: {n['content']}")

        with tab_react:
            st.markdown("### 🎉 Reaksi Cepat")
            st.markdown("Klik emoji untuk memberi semangat!")

            c1, c2, c3 = st.columns(3)
            with c1:
                if st.button("👍 Setuju", use_container_width=True):
                    st.session_state.reactions["👍"] += 1
                    st.toast("👍 Kamu memberi tepuk tangan!")
                    st.rerun()
                st.metric("Tepuk Tangan", st.session_state.reactions["👍"])

            with c2:
                if st.button("🔥 Semangat", use_container_width=True):
                    st.session_state.reactions["🔥"] += 1
                    st.toast("🔥 Api semangat menyala!")
                    st.rerun()
                st.metric("Semangat", st.session_state.reactions["🔥"])

            with c3:
                if st.button("🎉 Meriah", use_container_width=True):
                    st.session_state.reactions["🎉"] += 1
                    st.toast("🎉 Hore! Konfeti!")
                    st.rerun()
                st.metric("Meriah", st.session_state.reactions["🎉"])

    # Footer dengan Statistik
    st.divider()
    col_stats1, col_stats2, col_stats3 = st.columns(3)
    with col_stats1:
        st.markdown('<div class="stat-card"><div class="stat-value">👥 1</div><small>Peserta Aktif</small></div>', unsafe_allow_html=True)
    with col_stats2:
        st.markdown('<div class="stat-card"><div class="stat-value">📝 0</div><small>Catatan</small></div>', unsafe_allow_html=True)
    with col_stats3:
        st.markdown('<div class="stat-card"><div class="stat-value">💬 0</div><small>Pesan</small></div>', unsafe_allow_html=True)

    # Tombol Keluar
    if st.button("🚪 Keluar Rapat", type="secondary", use_container_width=True):
        st.session_state.joined = False
        st.session_state.chat_log = []
        st.session_state.notes = []
        st.session_state.reactions = {"👍": 0, "🔥": 0, "🎉": 0}
        st.rerun()

# --- Auto Refresh untuk Timer ---
# Streamlit tidak memiliki loop real-time native, jadi kita gunakan trick session_state
# atau biarkan user refresh manual untuk update timer (untuk demo ini cukup manual)
# Jika ingin timer update otomatis, bisa gunakan st.empty() dalam loop, tapi akan reload halaman.
