import streamlit as st
import uuid
import csv
import io
from datetime import datetime

# --- Konfigurasi Halaman ---
st.set_page_config(
    page_title="Meeting & Absensi Pro",
    page_icon="📹",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- Inisialisasi Session State ---
if 'attendance_list' not in st.session_state:
    st.session_state['attendance_list'] = []
if 'meeting_active' not in st.session_state:
    st.session_state['meeting_active'] = False
if 'room_id' not in st.session_state:
    st.session_state['room_id'] = ""
if 'participant_name' not in st.session_state:
    st.session_state['participant_name'] = ""

# --- Header ---
st.title("🎥 Meeting Jitsi + Absensi Cerdas")
st.markdown("""
**Panduan Cepat:**
1. Isi Nama & Peran di kiri.
2. (Opsional) Isi ID Ruangan jika punya, atau biarkan kosong untuk Otomatis Acak.
3. Klik **"Daftar & Masuk"**.
4. Download absensi setelah selesai.
""")

# --- Layout: Kiri (Kontrol) | Kanan (Video) ---
col_control, col_video = st.columns([1, 2], gap="medium")

with col_control:
    st.header("📝 Form Pendaftaran & Absensi")

    with st.form(key="absensi_form", clear_on_submit=False):
        p_name = st.text_input("Nama Lengkap", placeholder="Contoh: Budi Santoso")
        p_role = st.selectbox("Peran", ["Peserta", "Narasumber", "Moderator", "Tamu"])

        st.divider()
        st.caption("🏠 Pengaturan Ruangan")
        # Input ID Manual (Optional)
        custom_room = st.text_input(
            "ID Ruangan (Opsional)", 
            placeholder="Kosongkan untuk ID Acak",
            help="Masukkan ID spesifik jika sudah punya (misal: rapat-bos-123)"
        )

        submit_btn = st.form_submit_button("✅ Daftar & Masuk Meeting", type="primary")

    st.divider()

    # Tampilan Daftar Absensi
    st.subheader("📋 Daftar Hadir ({})".format(len(st.session_state['attendance_list'])))

    if st.session_state['attendance_list']:
        # Tampilkan dalam bentuk tabel kecil
        data_for_table = []
        for i, item in enumerate(st.session_state['attendance_list']):
            data_for_table.append({
                "No": i+1,
                "Waktu": item['waktu'],
                "Nama": item['nama'],
                "Peran": item['role']
            })

        import pandas as pd
        df = pd.DataFrame(data_for_table)
        st.dataframe(df, hide_index=True, use_container_width=True)

        # Tombol Aksi
        col_btn1, col_btn2 = st.columns(2)
        with col_btn1:
            # Buat CSV
            csv_buffer = io.StringIO()
            writer = csv.writer(csv_buffer)
            writer.writerow(["No", "Waktu", "Nama", "Peran"])
            for idx, item in enumerate(st.session_state['attendance_list'], 1):
                writer.writerow([idx, item['waktu'], item['nama'], item['role']])

            st.download_button(
                label="⬇️ Unduh CSV",
                data=csv_buffer.getvalue(),
                file_name=f"absensi_{datetime.now().strftime('%H%M')}.csv",
                mime="text/csv"
            )

        with col_btn2:
            if st.button("🗑️ Reset Data"):
                st.session_state['attendance_list'] = []
                st.rerun()
    else:
        st.info("Belum ada data absensi.")

with col_video:
    st.header("📹 Ruang Video Meeting")

    # Jika meeting aktif
    if st.session_state['meeting_active']:
        clean_room_id = st.session_state['room_id']
        participant_name = st.session_state['participant_name']
        domain = "meet.jit.si"

        # Info Badge
        st.success(f"🟢 **Ruang Aktif**: `{clean_room_id}`")
        st.caption(f"Menghubungkan sebagai: **{participant_name}**")

        # Tombol Keluar/Selesai
        if st.button("🛑 Keluar & Selesai Meeting", type="secondary"):
            st.session_state['meeting_active'] = False
            st.rerun()

        st.divider()

        # Embed Jitsi (Tampilan Penuh)
        jitsi_embed_code = f"""
        <div id="jitsi-meet-container" style="width: 110%; height: 70vh; border-radius: 12px; overflow: hidden; box-shadow: 0 4px 20px rgba(0,0,0,0.3);"></div>

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
        st.components.v1.html(jitsi_embed_code, height=600, scrolling=false)

    else:
        # Tampilan Awal (Placeholder)
        st.markdown("""
        <div style="background-color: #f0f2f6; padding: 40px; border-radius: 12px; text-align: center;">
            <h3>📹 Ruang Video Siap</h3>
            <p>Silakan isi form pendaftaran di sebelah kiri untuk memulai.</p>
            <p>Atau gunakan tombol di bawah jika ingin membuat ID Ruangan saja.</p>
            <hr>
            <p style="font-size: 12px; color: #666;">Video meeting akan muncul di sini setelah Anda mendaftar.</p>
        </div>
        """, unsafe_allow_html=True)

# --- Logika Utama: Submit Form ---
if submit_btn:
    if not p_name.strip():
        st.error("⚠️ **Nama tidak boleh kosong!**")
    else:
        # Tentukan ID Ruangan
        final_room_id = ""
        if custom_room.strip():
            final_room_id = custom_room.strip()
        else:
            final_room_id = f"rapat-{uuid.uuid4().hex[:6]}"

        # Simpan ke State
        st.session_state['room_id'] = final_room_id
        st.session_state['participant_name'] = p_name.strip()

        # Simpan ke Absensi
        new_entry = {
            "nama": p_name.strip(),
            "role": p_role,
            "waktu": datetime.now().strftime("%H:%M:%S")
        }

        # Cek duplikasi
        exists = any(item['nama'].lower() == p_name.lower() for item in st.session_state['attendance_list'])
        if not exists:
            st.session_state['attendance_list'].append(new_entry)
            st.session_state['meeting_active'] = True
            st.success(f"✅ Berhasil! Mengalihkan ke ruangan: `{final_room_id}`")
            st.rerun()
        else:
            st.error(f"⚠️ Nama '{p_name}' sudah ada di daftar hadir. Silakan gunakan nama lain.")

# --- Footer ---
st.divider()
st.markdown("""
<div style="text-align: center; color: #888; font-size: 0.8em;">
    Aplikasi Meeting & Absensi berbasis Streamlit & Jitsi.
</div>
""", unsafe_allow_html=True)
