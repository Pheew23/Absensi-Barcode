import streamlit as st
import sqlite3
import uuid
import csv
import io
from datetime import datetime
import time

# --- Konfigurasi Halaman (Mobile Friendly) ---
st.set_page_config(
    page_title="Meeting HP",
    page_icon="📱",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- Custom CSS untuk Mobile ---
# Ini adalah kunci agar video tidak terpotong di HP
st.markdown("""
<style>
    /* Hilangkan padding berlebih di atas/bawah untuk video */
    .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
        padding-left: 1rem;
        padding-right: 1rem;
    }

    /* Pastikan kontainer video memenuhi lebar layar */
    [data-testid="stVerticalBlock"] > div > div {
        width: 100%;
    }

    /* Perbaiki tinggi iframe Jitsi di mobile */
    iframe {
        border-radius: 8px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }

    /* Sembunyikan elemen yang tidak perlu saat meeting aktif di HP */
    .meeting-active .st-emotion-cache-1c7f0r {
        display: none; /* Sembunyikan header jika perlu (opsional) */
    }

    /* Pastikan tabel responsif */
    .stDataFrame {
        font-size: 12px;
    }
</style>
""", unsafe_allow_html=True)

# --- Database Logic (Sama seperti sebelumnya) ---
DB_FILE = "meeting_db.sqlite"

def init_db():
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
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    waktu = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    c.execute("SELECT * FROM attendance WHERE nama = ? AND room_id = ?", (nama, room_id))
    if c.fetchone():
        conn.close()
        return False, "Nama sudah terdaftar."
    c.execute("INSERT INTO attendance (nama, peran, room_id, waktu_masuk) VALUES (?, ?, ?, ?)",
              (nama, peran, room_id, waktu))
    conn.commit()
    conn.close()
    return True, "Berhasil!"

def get_attendance(room_id):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("SELECT id, nama, peran, waktu_masuk FROM attendance WHERE room_id = ? ORDER BY waktu_masuk DESC", (room_id,))
    rows = c.fetchall()
    conn.close()
    return rows

def clear_attendance(room_id):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("DELETE FROM attendance WHERE room_id = ?", (room_id,))
    conn.commit()
    conn.close()

init_db()

# --- State Management ---
if 'current_room_id' not in st.session_state:
    st.session_state['current_room_id'] = ""
if 'current_user_name' not in st.session_state:
    st.session_state['current_user_name'] = ""
if 'user_registered' not in st.session_state:
    st.session_state['user_registered'] = False

# --- Tampilan Header ---
st.title("📱 Meeting & Absensi")
st.caption("Mode Mobile: Video akan memenuhi layar.")

# --- LOGIKA UTAMA ---

# Jika user sudah terdaftar, tampilkan Video zuerst (Prioritas HP)
if st.session_state.get('user_registered') and st.session_state.get('current_room_id'):
    room_id = st.session_state['current_room_id']
    user_name = st.session_state['current_user_name']
    domain = "meet.jit.si"

    # Tampilan Full Screen Video
    st.markdown(f"### 🟢 Ruangan: `{room_id}`")

    # Tombol Keluar di bagian atas agar mudah diakses
    if st.button("🛑 Keluar Meeting", use_container_width=True, type="secondary"):
        st.session_state['user_registered'] = False
        st.session_state['current_room_id'] = ""
        st.rerun()

    st.divider()

    # --- JITSI EMBED (CSS PERBAIKAN KHUSUS) ---
    # Height diatur ke 80vh (80% tinggi layar) + scroll hidden
    jitsi_html = f"""
    <div style="width: 100%; height: 80vh; overflow: hidden; border-radius: 12px; position: relative;">
        <div id="jitsi-container" style="width: 100%; height: 100%;"></div>
        <script src='https://meet.jit.si/external_api.js'></script>
        <script>
            var domain = '{domain}';
            var options = {{
                roomName: '{room_id}',
                width: '100%',
                height: '100%',
                parentNode: document.querySelector('#jitsi-container'),
                lang: 'id',
                userInfo: {{
                    displayName: '{user_name}'
                }},
                configOverwrite: {{ 
                    startWithAudioMuted: false, 
                    startWithVideoMuted: false,
                    disableDeepLinking: true,
                    prejoinPageEnabled: false
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

            // Event: Ketika user keluar dari Jitsi, kita reset state
            api.addEventListeners({{
                videoConferenceLeft: function () {{
                    console.log("User left");
                }}
            }});
        </script>
    </div>
    """

    st.components.v1.html(jitsi_html, height=600, scrolling=False)

    # Tampilkan daftar hadir di bawah video (agar tidak menutupi video)
    st.divider()
    st.subheader("📋 Daftar Hadir")

    data_rows = get_attendance(room_id)
    if data_rows:
        import pandas as pd
        data_list = [{"No": i+1, "Waktu": r[3], "Nama": r[1], "Peran": r[2]} for i, r in enumerate(data_rows)]
        df = pd.DataFrame(data_list)
        # Scrollable table di HP
        st.dataframe(df, use_container_width=True, hide_index=True, height=200)

        # Tombol Download & Reset
        col1, col2 = st.columns(2)
        with col1:
            csv_buffer = io.StringIO()
            writer = csv.writer(csv_buffer)
            writer.writerow(["No", "Waktu", "Nama", "Peran"])
            for i, r in enumerate(data_rows):
                writer.writerow([i+1, r[3], r[1], r[2]])
            st.download_button("⬇️ Unduh CSV", csv_buffer.getvalue(), f"absensi_{room_id}.csv", "text/csv", use_container_width=True)

        with col2:
            if st.button("🗑️ Reset", use_container_width=True):
                clear_attendance(room_id)
                st.rerun()
    else:
        st.info("Belum ada peserta.")

else:
    # --- LAYAR INPUT (SEBELUM MASUK) ---
    st.markdown("### 📝 Masuk ke Rapat")

    col1, col2 = st.columns([3, 1])
    with col1:
        room_input = st.text_input("ID Ruangan", placeholder="Contoh: rapat-123", key="room_in")
    with col2:
        if st.button("🎲 Acak", use_container_width=True):
            st.session_state['temp_room'] = f"rapat-{uuid.uuid4().hex[:6]}"
            st.rerun()

    if st.session_state.get('temp_room'):
        room_input = st.session_state['temp_room']
        st.warning(f"ID Ruangan: `{room_input}` (Gunakan ID ini untuk semua peserta)")
        # Hapus temp setelah ditampilkan
        del st.session_state['temp_room']
        st.session_state['current_room_id'] = room_input

    if room_input:
        st.session_state['current_room_id'] = room_input.strip()

    with st.form("join_form"):
        name_in = st.text_input("Nama Lengkap", placeholder="Nama Anda")
        role_in = st.selectbox("Peran", ["Peserta", "Narasumber", "Moderator"])

        submit = st.form_submit_button("✅ Daftar & Masuk", type="primary", use_container_width=True)

        if submit:
            if not room_input:
                st.error("⚠️ Masukkan ID Ruangan!")
            elif not name_in:
                st.error("⚠️ Masukkan Nama!")
            else:
                success, msg = add_attendance(name_in.strip(), role_in, room_input.strip())
                if success:
                    st.session_state['current_user_name'] = name_in.strip()
                    st.session_state['user_registered'] = True
                    st.success("Berhasil! Mengarahkan ke video...")
                    st.rerun()
                else:
                    st.error(msg)
    else:
        st.info("👇 Silakan isi ID Ruangan di atas.")

# Footer
st.markdown("---")
st.caption("Aplikasi Meeting & Absensi Mobile-Optimized")
