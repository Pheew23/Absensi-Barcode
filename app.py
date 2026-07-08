import streamlit as st
import uuid

# --- Konfigurasi Halaman ---
st.set_page_config(
    page_title="Jitsi Meeting Pro",
    page_icon="📹",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- Header & Styling ---
st.title("🎥 Video Meeting Jitsi Meet")
st.markdown("""
> Aplikasi ini memungkinkan Anda membuat atau bergabung ke ruang konferensi video secara instan.
> **Tips:** Gunakan ID ruangan yang unik agar tidak bentrok dengan orang lain.
""")

# --- Kontrol Input (Dibuat di bagian atas, bukan sidebar) ---
col1, col2 = st.columns([3, 1])

with col1:
    participant_name = st.text_input("Nama Anda (Nama Peserta)", placeholder="Masukkan nama panggilan...", key="name_input")

with col2:
    st.markdown("<br>", unsafe_allow_html=True)
    # Tombol untuk membuat ID acak
    if st.button("🎲 Buat ID Acak", key="random_id_btn"):
        new_id = f"meeting-{uuid.uuid4().hex[:8]}"
        st.session_state.room_id = new_id
        st.rerun()

# Input ID Ruangan
st.divider()
st.subheader("📍 Masuk ke Ruang Meeting")

col_room1, col_room2 = st.columns([4, 1])

with col_room1:
    # Cek apakah ada ID di session state (dari tombol random atau input sebelumnya)
    default_room = st.session_state.get("room_id", "")
    room_id = st.text_input(
        "Masukkan ID Ruang Meeting (Contoh: ruang-kerja-123)", 
        value=default_room,
        placeholder="Ketik ID ruangan atau gunakan tombol 'Buat ID Acak' di atas",
        key="room_input"
    )

with col_room2:
    st.markdown("<br>", unsafe_allow_html=True)
    join_btn = st.button("🚀 Bergabung Sekarang", type="primary", use_container_width=True)

# --- Logika Penampilan Jitsi ---
if join_btn:
    if not participant_name.strip():
        st.error("⚠️ **Harap isi Nama Anda terlebih dahulu!**")
    elif not room_id.strip():
        st.error("⚠️ **Harap isi ID Ruangan!**")
    else:
        # Membersihkan ID ruangan (menghilangkan spasi di awal/akhir)
        clean_room_id = room_id.strip()

        # Konfigurasi Jitsi
        # Kita menggunakan meet.jit.si (Server Publik)
        domain = "meet.jit.si"
        url = f"https://{domain}/{clean_room_id}"

        st.success(f"✅ Bergabung ke ruang: **`{clean_room_id}`**")
        st.info(f"👤 Anda masuk sebagai: **{participant_name}**")

        # --- Embed Jitsi dengan Tinggi Besar ---
        st.markdown("### 📹 Ruang Video Aktif")

        # HTML Kustom untuk memaksimalkan tinggi video
        # Tinggi diatur ke 80vh (80% dari tinggi viewport) agar terlihat besar
        jitsi_embed_code = f"""
        <div id="jitsi-meet-container" style="width: 100%; height: 80vh; border-radius: 10px; overflow: hidden; box-shadow: 0 4px 15px rgba(0,0,0,0.2);"></div>

        <script src='https://meet.jit.si/external_api.js'></script>
        <script>
            var domain = '{domain}';
            var options = {{
                roomName: '{clean_room_id}',
                width: '100%',
                height: '100%',
                parentNode: document.querySelector('#jitsi-meet-container'),
                lang: 'id', // Bahasa Indonesia
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
                    SHOW_JITSI_WATERMARK: false,
                    SHOW_BRAND_WATERMARK: false
                }}
            }};

            var api = new JitsiMeetExternalAPI(domain, options);

            // Event Listener untuk logika tambahan jika diperlukan
            api.addEventListeners({{
                readyToClose: function() {{
                    console.log("Meeting ditutup");
                }},
                videoConferenceJoined: function() {{
                    console.log("User joined the conference");
                }}
            }});
        </script>
        """

        # Render HTML
        st.components.v1.html(jitsi_embed_code, height=700, scrolling=False)

        st.divider()
        st.markdown("""
        <div style="text-align: center; color: #666; font-size: 0.9em;">
            <em>Untuk keluar dari meeting, klik ikon "Hangup" (Telepon Merah) di dalam jendela video.</em>
        </div>
        """, unsafe_allow_html=True)

else:
    st.markdown("""
    <div style="text-align: center; padding: 50px; color: #888;">
        <h3>Siap Meeting?</h3>
        <p>Masukkan nama dan ID ruangan di atas, lalu klik <strong>"Bergabung Sekarang"</strong>.</p>
    </div>
    """, unsafe_allow_html=True)
