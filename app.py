import streamlit as st
import uuid
import csv
import io
from datetime import datetime

# --- Konfigurasi Halaman ---
st.set_page_config(
    page_title="Meeting Mobile",
    page_icon="📱",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- CSS untuk Perbaikan Tampilan Mobile ---
st.markdown("""
<style>
    .block-container {
        padding-top: 1rem;
        padding-bottom: 1rem;
        padding-left: 0.5rem;
        padding-right: 0.5rem;
    }
    .stButton > button {
        height: 50px;
        font-size: 16px;
        width: 100%;
    }
</style>
""", unsafe_allow_html=True)

st.title("📱 Meeting Jitsi & Catatan")
st.caption("Mode Tanpa Database: Data absensi hanya tersimpan di HP Anda.")

# --- Inisialisasi State ---
if 'room_id' not in st.session_state:
    st.session_state['room_id'] = ""
if 'user_name' not in st.session_state:
    st.session_state['user_name'] = ""
if 'is_meeting' not in st.session_state:
    st.session_state['is_meeting'] = False
if 'my_attendance' not in st.session_state:
    st.session_state['my_attendance'] = []

# --- LOGIKA UTAMA ---

# 1. Jika Meeting Aktif -> Tampilkan Video
if st.session_state['is_meeting']:
    room_id = st.session_state['room_id']
    user_name = st.session_state['user_name']
    domain = "meet.jit.si"

    st.markdown(f"### 🟢 Ruangan: `{room_id}`")

    if st.button("🛑 Keluar Meeting", use_container_width=True, type="secondary"):
        st.session_state['is_meeting'] = False
        st.rerun()

    st.divider()

    # Embed Jitsi dengan tinggi besar (80vh)
    jitsi_code = f"""
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
                    SHOW_JITSI_WATERMARK: false
                }}
            }};
            var api = new JitsiMeetExternalAPI(domain, options);
        </script>
    </div>
    """
    st.components.v1.html(jitsi_code, height=650, scrolling=False)

    st.divider()
    st.subheader("📝 Catatan Absensi Pribadi (HP Anda)")
    st.info("⚠️ Catatan ini hanya tersimpan di HP Anda. Salin ke WhatsApp jika perlu.")

    # Form Tambah Catatan
    with st.form("note_form", clear_on_submit=True):
        note_name = st.text_input("Nama yang hadir")
        note_role = st.selectbox("Peran", ["Peserta", "Narasumber"])
        btn_add_note = st.form_submit_button("➕ Tambah ke Catatan")

        if btn_add_note and note_name:
            st.session_state['my_attendance'].append({
                "nama": note_name,
                "role": note_role,
                "waktu": datetime.now().strftime("%H:%M")
            })
            st.success("Catatan ditambahkan!")
            st.rerun()

    # Tampilkan Daftar Catatan
    if st.session_state['my_attendance']:
        st.markdown("**Daftar yang tercatat di HP ini:**")
        for i, item in enumerate(st.session_state['my_attendance']):
            st.markdown(f"{i+1}. **{item['nama']}** ({item['role']}) - {item['waktu']}")

        # Export CSV
        csv_buffer = io.StringIO()
        writer = csv.writer(csv_buffer)
        writer.writerow(["No", "Waktu", "Nama", "Peran"])
        for i, item in enumerate(st.session_state['my_attendance'], 1):
            writer.writerow([i, item['waktu'], item['nama'], item['role']])

        st.download_button(
            label="⬇️ Unduh Catatan Saya (CSV)",
            data=csv_buffer.getvalue(),
            file_name=f"catatan_{user_name}.csv",
            mime="text/csv",
            use_container_width=True
        )

        if st.button("🗑️ Hapus Catatan Pribadi"):
            st.session_state['my_attendance'] = []
            st.rerun()

# 2. Jika Belum Masuk -> Tampilkan Form Login
else:
    st.markdown("### 📝 Masuk ke Rapat")

    col1, col2 = st.columns([3, 1])
    with col1:
        room_input = st.text_input("ID Ruangan (Harus Sama)", placeholder="Contoh: rapat-123")

    with col2:
        if st.button("🎲 Acak ID"):
            st.session_state['temp_id'] = f"rapat-{uuid.uuid4().hex[:6]}"
            st.rerun()

    # Handle ID Acak
    if 'temp_id' in st.session_state:
        room_input = st.session_state['temp_id']
        st.warning(f"ID Ruangan: `{room_input}` (Salin ID ini dan kirim ke peserta lain)")
        del st.session_state['temp_id']
        st.session_state['room_id'] = room_input

    if room_input:
        st.session_state['room_id'] = room_input.strip()

    with st.form("login_form"):
        name_input = st.text_input("Nama Lengkap Anda", placeholder="Contoh: Budi")
        role_input = st.selectbox("Peran", ["Peserta", "Narasumber", "Moderator"])

        btn_join = st.form_submit_button("✅ Masuk & Mulai Meeting", type="primary")

        if btn_join:
            if not room_input:
                st.error("⚠️ Masukkan ID Ruangan!")
            elif not name_input:
                st.error("⚠️ Masukkan Nama!")
            else:
                st.session_state['user_name'] = name_input.strip()
                st.session_state['room_id'] = room_input.strip()
                st.session_state['is_meeting'] = True
                st.success("✅ Mengalihkan ke video...")
                st.rerun()
    else:
        st.info("👇 Silakan isi ID Ruangan di atas.")

st.markdown("---")
st.caption("Aplikasi Mobile-Optimized | Tanpa Database Global")
