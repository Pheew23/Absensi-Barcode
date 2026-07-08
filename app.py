import streamlit as st
import sqlite3
import uuid
import csv
import io
from datetime import datetime
import os

# --- Konfigurasi Database (SQLite) ---
# File database akan dibuat otomatis di folder tempat script dijalankan
DB_FILE = "meeting_db.sqlite"

def init_db():
    """Inisialisasi tabel database jika belum ada"""
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS attendance (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nama TEXT NOT NULL,
            peran TEXT NOT NULL,
            waktu_masuk TEXT NOT NULL,
            room_id TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

def add_attendance(nama, peran, room_id):
    """Menambahkan data ke database"""
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    waktu = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Cek duplikasi berdasarkan nama dan room_id dalam 1 menit terakhir (pencegahan spam)
    c.execute("SELECT * FROM attendance WHERE nama = ? AND room_id = ? AND waktu_masuk > ?", 
              (nama, room_id, datetime.now().strftime("%Y-%m-%d %H:%M:%S", datetime.now().timetuple())))
    if c.fetchone():
        conn.close()
        return False, "Nama ini sudah terdaftar di ruangan ini."

    c.execute("INSERT INTO attendance (nama, peran, room_id, waktu_masuk) VALUES (?, ?, ?, ?)",
              (nama, peran, room_id, waktu))
    conn.commit()
    conn.close()
    return True, "Berhasil didaftarkan!"

def get_attendance(room_id):
    """Mengambil data absensi dari database untuk ruangan tertentu"""
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    # Ambil semua data untuk room_id tersebut, urutkan berdasarkan waktu
    c.execute("SELECT id, nama, peran, waktu_masuk FROM attendance WHERE room_id = ? ORDER BY waktu_masuk DESC", (room_id,))
    rows = c.fetchall()
    conn.close()
    return rows

def clear_attendance(room_id):
    """Menghapus data absensi untuk ruangan tertentu (opsional, untuk reset)"""
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("DELETE FROM attendance WHERE room_id = ?", (room_id,))
    conn.commit()
    conn.close()

# Inisialisasi DB saat pertama kali dijalankan
init_db()

# --- Konfigurasi Halaman ---
st.set_page_config(
    page_title="Meeting & Absensi Global",
    page_icon="🌐",
    layout="wide",
    initial_sidebar_state="collapsed"
)

st.title("🌐 Video Meeting & Absensi Global")
st.markdown("""
**Catatan Penting:** Data absensi ini disimpan secara **Global** ke database server.
Semua peserta yang membuka aplikasi dengan **ID Ruangan yang sama** akan melihat daftar hadir yang sama.
""")

# --- Inisialisasi Session State (Khusus Sesi Pengguna) ---
if 'current_room_id' not in st.session_state:
    st.session_state['current_room_id'] = ""
if 'current_user_name' not in st.session_state:
    st.session_state['current_user_name'] = ""
if 'user_registered' not in st.session_state:
    st.session_state['user_registered'] = False

# --- Layout ---
col_input, col_video = st.columns([1, 2], gap="medium")

with col_input:
    st.header("📝 Pendaftaran Peserta")

    # Input ID Ruangan (Wajib untuk sinkronisasi)
    room_id_input = st.text_input(
        "🆔 ID Ruangan Meeting", 
        placeholder="Contoh: rapat-bos-123",
        help="Semua orang harus memasukkan ID ini agar terhubung ke daftar yang sama."
    )

    if room_id_input:
        st.session_state['current_room_id'] = room_id_input.strip()

    # Cek apakah user sudah terdaftar di room ini
    is_registered = False
    if st.session_state['current_room_id'] and st.session_state.get('current_user_name'):
        # Cek database apakah user sudah ada di room ini
        rows = get_attendance(st.session_state['current_room_id'])
        if any(row[1] == st.session_state['current_user_name'] for row in rows):
            is_registered = True

    with st.form(key="absensi_form"):
        p_name = st.text_input("Nama Lengkap Anda", placeholder="Contoh: Budi Santoso")
        p_role = st.selectbox("Peran", ["Peserta", "Narasumber", "Moderator", "Tamu"])

        submit_btn = st.form_submit_button("✅ Daftar & Masuk")

        if submit_btn:
            if not room_id_input:
                st.error("⚠️ **ID Ruangan harus diisi!** Semua peserta harus menggunakan ID yang sama.")
            elif not p_name.strip():
                st.error("⚠️ **Nama tidak boleh kosong!**")
            else:
                success, msg = add_attendance(p_name.strip(), p_role, room_id_input.strip())
                if success:
                    st.session_state['current_user_name'] = p_name.strip()
                    st.session_state['current_room_id'] = room_id_input.strip()
                    st.session_state['user_registered'] = True
                    st.success(f"✅ {msg}")
                    st.rerun()
                else:
                    st.error(f"⚠️ {msg}")

    st.divider()

    # Panel Daftar Hadir (Diambil dari Database)
    if st.session_state['current_room_id']:
        st.subheader(f"📋 Daftar Hadir: `{st.session_state['current_room_id']}`")

        # Ambil data terbaru dari DB
        data_rows = get_attendance(st.session_state['current_room_id'])

        if data_rows:
            import pandas as pd
            data_list = [{"No": i+1, "Waktu": r[3], "Nama": r[1], "Peran": r[2]} for i, r in enumerate(data_rows)]
            df = pd.DataFrame(data_list)
            st.dataframe(df, use_container_width=True, hide_index=True)

            # Tombol Download
            csv_buffer = io.StringIO()
            writer = csv.writer(csv_buffer)
            writer.writerow(["No", "Waktu", "Nama", "Peran"])
            for i, r in enumerate(data_rows):
                writer.writerow([i+1, r[3], r[1], r[2]])

            col_d1, col_d2 = st.columns(2)
            with col_d1:
                st.download_button(
                    label="⬇️ Unduh CSV",
                    data=csv_buffer.getvalue(),
                    file_name=f"absensi_{st.session_state['current_room_id']}.csv",
                    mime="text/csv"
                )
            with col_d2:
                if st.button("🗑️ Hapus Daftar (Reset)", type="secondary"):
                    clear_attendance(st.session_state['current_room_id'])
                    st.rerun()
        else:
            st.info("Belum ada peserta yang mendaftar di ruangan ini.")
            st.warning("Pastikan semua peserta memasukkan **ID Ruangan yang sama** di atas.")
    else:
        st.info("Silakan masukkan ID Ruangan di atas untuk melihat daftar hadir.")

with col_video:
    st.header("📹 Ruang Video")

    if st.session_state.get('user_registered') and st.session_state.get('current_room_id'):
        room_id = st.session_state['current_room_id']
        user_name = st.session_state['current_user_name']
        domain = "meet.jit.si"

        st.success(f"🟢 **Anda terhubung ke ruang:** `{room_id}`")
        st.caption(f"Hadir sebagai: **{user_name}**")

        if st.button("🛑 Keluar Meeting"):
            st.session_state['user_registered'] = False
            st.rerun()

        st.divider()

        # Embed Jitsi
        jitsi_embed_code = f"""
        <div id="jitsi-meet-container" style="width: 100%; height: 70vh; border-radius: 12px; overflow: hidden; box-shadow: 0 4px 20px rgba(0,0,0,0.3);"></div>

        <script src='https://meet.jit.si/external_api.js'></script>
        <script>
            var domain = '{domain}';
            var options = {{
                roomName: '{room_id}',
                width: '100%',
                height: '100%',
                parentNode: document.querySelector('#jitsi-meet-container'),
                lang: 'id',
                userInfo: {{
                    displayName: '{user_name}'
                }},
                configOverwrite: {{ 
                    startWithAudioMuted: false, 
                    startWithVideoMuted: false,
                    disableDeepLinking: true
                }},
                interfaceConfigOverwrite: {{
                    TOOLBAR_BUTTONS: [
                        'microphone', 'camera', 'closedcaptions', 'desktop', 'fullscreen',
                        'fodeviceselection', 'hangup', 'profile', 'chat', 'recording',
                        'livestreaming', 'etherpad', 'sharedvideo', 'settings', 'raisehand',
                        'videoquality', 'filmstrip', 'invite', 'feedback', 'stats', 'shortcuts',
                        'tileview', 'videobackgroundblur', 'download', 'help', 'mute-everyone',
                        'security'
                    ],
                    DISABLE_JOIN_LEAVE_NOTIFICATIONS: false,
                    SHOW_JITSI_WATERMARK: false
                }}
            }};
            var api = new JitsiMeetExternalAPI(domain, options);
        </script>
        """
        st.components.v1.html(jitsi_embed_code, height=600, scrolling=False)
    else:
        st.info("👈 Silakan isi ID Ruangan dan Nama di sebelah kiri untuk masuk.")
        
