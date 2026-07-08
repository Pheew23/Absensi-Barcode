import streamlit as st
import uuid
import os

# Konfigurasi Halaman
st.set_page_config(
    page_title="Video Meeting Jitsi - Streamlit",
    page_icon="📹",
    layout="wide"
)

st.title("📹 Aplikasi Video Meeting Jitsi")
st.markdown("""
Aplikasi ini mengintegrasikan **Jitsi Meet** ke dalam Streamlit.
Silakan masukkan nama Anda dan ID Ruangan untuk bergabung.
""")

# Sidebar untuk pengaturan
with st.sidebar:
    st.header("🔧 Pengaturan Meeting")
    participant_name = st.text_input("Nama Peserta", value="Pengguna Streamlit")

    # Opsi ID Ruangan: Random atau Manual
    room_option = st.radio("Pilih ID Ruangan:", ["Acak (Random ID)", "Input Manual"])

    jitsi_domain = st.text_input("Domain Jitsi", value="meet.jit.si")

    generate_btn = st.button("🚀 Mulai Meeting")

# Logika Utama
if generate_btn:
    if not participant_name:
        st.error("⚠️ Nama peserta tidak boleh kosong!")
    else:
        # Menentukan ID Ruangan
        if room_option == "Acak (Random ID)":
            room_id = f"ruang-meeting-{uuid.uuid4().hex[:8]}"
            st.success(f"✅ Ruangan dibuat: `{room_id}`")
        else:
            room_id = st.text_input("Masukkan ID Ruangan Manual", key="manual_room")
            if not room_id:
                st.warning("⚠️ ID ruangan manual belum diisi.")
                st.stop()

        # Mengonstruksi URL Jitsi
        # Format: https://meet.jit.si/RoomName
        jitsi_url = f"https://{jitsi_domain}/{room_id}"

        st.divider()

        # Kontainer untuk Iframe Jitsi
        st.markdown(f"### 🗣️ Ruang Meeting: `{room_id}`")
        st.markdown(f"**Siap bergabung sebagai:** {participant_name}")

        # Embed Jitsi Meet External API
        # Kita menggunakan komponen HTML Streamlit untuk menyuntikkan script JS Jitsi
        jitsi_html = f"""
        <div id="jitsi-container" style="height: 600px; width: 100%;"></div>
        <script src='https://meet.jit.si/external_api.js'></script>
        <script>
            var domain = '{jitsi_domain}';
            var options = {{
                roomName: '{room_id}',
                width: '100%',
                height: '600',
                parentNode: document.querySelector('#jitsi-container'),
                userInfo: {{
                    displayName: '{participant_name}'
                }},
                configOverwrite: {{ 
                    startWithAudioMuted: false, 
                    startWithVideoMuted: false 
                }},
                interfaceConfigOverwrite: {{ 
                    TOOLBAR_BUTTONS: [
                        'microphone', 'camera', 'closedcaptions', 'desktop', 'fullscreen',
                        'fodeviceselection', 'hangup', 'profile', 'chat', 'recording',
                        'livestreaming', 'etherpad', 'sharedvideo', 'settings', 'raisehand',
                        'videoquality', 'filmstrip', 'invite', 'feedback', 'stats', 'shortcuts',
                        'tileview', 'videobackgroundblur', 'download', 'help', 'mute-everyone',
                        'security'
                    ]
                }}
            }};
            var api = new JitsiMeetExternalAPI(domain, options);

            // Event listeners opsional (contoh: saat user keluar)
            api.addEventListeners({{
                videoConferenceLeft: function () {{
                    console.log("User has left the conference");
                }}
            }});
        </script>
        """

        st.components.v1.html(jitsi_html, height=650)

else:
    st.info("💡 Silakan isi nama dan klik 'Mulai Meeting' di sidebar untuk masuk ke ruang konferensi.")
