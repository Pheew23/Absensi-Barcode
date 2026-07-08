import streamlit as st
import uuid
import csv
import io
from datetime import datetime

# --- Konfigurasi Halaman ---
st.set_page_config(
    page_title="Jitsi Meeting + Absensi",
    page_icon="📋",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- Inisialisasi Session State untuk Absensi ---
if 'attendance_list' not in st.session_state:
    st.session_state['attendance_list'] = []
if 'meeting_active' not in st.session_state:
    st.session_state['meeting_active'] = False

# --- Header ---
st.title("🎥 Video Meeting & Absensi Otomatis")
st.markdown("""
### Fitur:
1. **Video Meeting**: Terintegrasi Jitsi Meet (Full Screen).
2. **Absensi**: Rekam nama peserta sebelum bergabung.
3. **Export**: Unduh daftar hadir dalam format Excel/CSV.
""")

# --- Layout Utama: 2 Kolom (Kiri: Kontrol, Kanan: Video/Absensi) ---
# Kita buat layout yang membagi area: Kiri untuk input, Kanan untuk video besar
col_control, col_video = st.columns([1, 2], gap="small")

with col_control:
    st.header("📝 Data Peserta")
    st.markdown("Masukkan nama Anda sebelum bergabung.")

    with st.form(key="absensi_form"):
        p_name = st.text_input("Nama Lengkap", placeholder="Contoh: Budi Santoso")
        p_role = st.selectbox("Peran", ["Peserta", "Narasumber", "Moderator", "Tamu"])

        submit_absen = st.form_submit_button("✅ Daftar & Masuk Meeting")

    st.divider()

    # Panel Absensi Terdaftar
    st.subheader("📋 Daftar Hadir Saat Ini")

    if st.session_state['attendance_list']:
        for i, item in enumerate(st.session_state['attendance_list']):
            st.markdown(f"**{i+1}.** {item['nama']} ({item['role']})")

        # Tombol Download
        st.divider()
        st.markdown("### 📥 Unduh Laporan")

        # Membuat file CSV
        csv_buffer = io.StringIO()
        writer = csv.writer(csv_buffer)
        writer.writerow(["No", "Waktu", "Nama", "Peran"])
        for idx, item in enumerate(st.session_state['attendance_list'], 1):
            writer.writerow([idx, item['waktu'], item['nama'], item['role']])

        csv_data = csv_buffer.getvalue()

        st.download_button(
            label="⬇️ Download Absensi (CSV)",
            data=csv_data,
            file_name=f"absensi_meeting_{datetime.now().strftime('%Y%m%d_%H%M')}.csv",
            mime="text/csv",
            use_container_width=True
        )

        if st.button("🗑️ Reset Daftar Absensi"):
            st.session_state['attendance_list'] = []
            st.rerun()
    else:
        st.info("Belum ada peserta yang terdaftar.")

with col_video:
    st.header("📹 Ruang Video Meeting")

    if st.session_state.get('meeting_active'):
        # Data dari session state sebelumnya
        clean_room_id = st.session_state['room_id']
        participant_name = st.session_state['participant_name']
        domain = "meet.jit.si"

        st.success(f"🟢 **Meeting Berlangsung**: `{clean_room_id}`")
        st.caption(f"Host: {participant_name}")

        # --- Embed Jitsi (Tampilan Besar) ---
        jitsi_embed_code = f"""
        <div id="jitsi-meet-container" style="width: 100%; height: 75vh; border-radius: 12px; overflow: hidden; box-shadow: 0 4px 20px rgba(0,0,0,0.3);"></div>

        <script src='https://meet.jit.si/external_api.js'></script>
        <script>
            var domain = '{domain}';
            var options = {{
                roomName: '{clean_room_id}',
                width: '100%',
                height: '100%',
                parentNode: document.querySelector('#jitsi-meet-container'),
                lang: 'id',
                userInfo: {{
                    displayName: '{participant_name}'
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
        st.components.v1.html(jitsi_embed_code, height=650, scrolling=False)

        st.divider()
        if st.button("🛑 Selesai Meeting (Reset)"):
            st.session_state['meeting_active'] = False
            st.rerun()

    else:
        # Tampilan Awal Sebelum Masuk
        st.info("👈 Silakan isi form di sebelah kiri untuk mendaftar dan masuk ke ruang meeting.")

        # Tombol Acak Room ID jika belum ada
        if 'room_id' not in st.session_state:
            if st.button("🎲 Buat ID Ruangan Baru"):
                st.session_state['room_id'] = f"rapat-{uuid.uuid4().hex[:6]}"
                st.rerun()
        else:
            st.markdown(f"**ID Ruangan Saat Ini:** `{st.session_state['room_id']}`")

# --- Logika Utama: Saat Form Absensi Disubmit ---
if submit_absen:
    if not p_name.strip():
        st.error("⚠️ Nama tidak boleh kosong!")
    else:
        # 1. Buat ID Ruangan jika belum ada
        if 'room_id' not in st.session_state:
            st.session_state['room_id'] = f"rapat-{uuid.uuid4().hex[:6]}"

        # 2. Simpan data absensi
        new_entry = {
            "nama": p_name.strip(),
            "role": p_role,
            "waktu": datetime.now().strftime("%H:%M:%S")
        }

        # Cek duplikasi nama sederhana
        exists = any(item['nama'].lower() == p_name.lower() for item in st.session_state['attendance_list'])
        if not exists:
            st.session_state['attendance_list'].append(new_entry)
            st.session_state['participant_name'] = p_name.strip()
            st.session_state['meeting_active'] = True

            st.success(f"✅ {p_name} berhasil didaftarkan! Mengalihkan ke video...")
            st.rerun()
        else:
            st.warning(f"⚠️ Nama '{p_name}' sudah terdaftar. Silakan gunakan nama lain.")

# --- Footer ---
st.divider()
st.markdown("""
<div style="text-align: center; color: #aaa; font-size: 0.8em;">
    Disarankan menggunakan browser Chrome atau Edge untuk performa terbaik.<br>
    Aplikasi ini berjalan di server publik Jitsi. Pastikan koneksi internet stabil.
</div>
""", unsafe_allow_html=True)
