import streamlit as st
import pandas as pd
from io import BytesIO

# Sayfa yapılandırması
st.set_page_config(page_title="Maaş Bordro Sistemi", layout="centered")

# Session state başlatma
if 'df' not in st.session_state:
    st.session_state.df = None
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'user_name' not in st.session_state:
    st.session_state.user_name = None

# Başlık
st.title("💼 Maaş Bordro Sistemi")

# Admin Excel Yükleme Bölümü
with st.expander("🔧 Admin - Excel Yükle"):
    uploaded_file = st.file_uploader("Excel dosyası yükleyin", type=['xlsx', 'xls'])
    
    if uploaded_file is not None:
        try:
            # Excel'i oku
            df = pd.read_excel(uploaded_file)
            
            # Sütun kontrolü
            expected_columns = ['İsim', 'Maaş', 'Kesinti', 'Prim', 'Cüzdan', 'Şifre']
            if list(df.columns) == expected_columns:
                st.session_state.df = df
                st.success(f"✅ Excel başarıyla yüklendi! Toplam {len(df)} kullanıcı kaydı bulundu.")
            else:
                st.error(f"❌ Excel sütunları hatalı! Beklenen sütunlar: {', '.join(expected_columns)}")
        except Exception as e:
            st.error(f"❌ Excel okuma hatası: {str(e)}")

st.divider()

# Kullanıcı Giriş Bölümü
if not st.session_state.logged_in:
    # Excel yüklenmiş mi kontrol et
    if st.session_state.df is None:
        st.warning("⚠️ Veri henüz yüklenmedi. Lütfen admin ile iletişime geçin.")
    else:
        st.subheader("🔐 Kullanıcı Girişi")
        
        # Giriş formu
        with st.form("login_form"):
            isim = st.text_input("İsim")
            sifre = st.text_input("Şifre", type="password")
            submit = st.form_submit_button("Giriş Yap")
            
            if submit:
                if isim and sifre:
                    # DataFrame'de kullanıcıyı ara
                    df = st.session_state.df
                    
                    # İsim ve şifre kontrolü
                    user_row = df[(df['İsim'] == isim) & (df['Şifre'].astype(str) == sifre)]
                    
                    if not user_row.empty:
                        # Giriş başarılı
                        st.session_state.logged_in = True
                        st.session_state.user_name = isim
                        st.rerun()
                    else:
                        st.error("❌ İsim veya şifre hatalı!")
                else:
                    st.warning("⚠️ Lütfen tüm alanları doldurun!")

else:
    # Kullanıcı giriş yapmış - bilgilerini göster
    st.subheader(f"👤 Hoş geldiniz, {st.session_state.user_name}!")
    
    # Kullanıcının bilgilerini getir
    df = st.session_state.df
    user_data = df[df['İsim'] == st.session_state.user_name].iloc[0]
    
    st.divider()
    
    # Bilgileri göster
    col1, col2 = st.columns(2)
    
    with col1:
        st.metric("💰 Maaş", f"{user_data['Maaş']:,.2f} ₺")
        st.metric("➖ Kesinti", f"{user_data['Kesinti']:,.2f} ₺")
    
    with col2:
        st.metric("➕ Prim", f"{user_data['Prim']:,.2f} ₺")
        st.metric("💳 Cüzdan", user_data['Cüzdan'])
    
    st.divider()
    
    # Net hesaplama
    net_maas = user_data['Maaş'] - user_data['Kesinti'] + user_data['Prim']
    st.success(f"**💵 Net Ödeme: {net_maas:,.2f} ₺**")
    
    st.divider()
    
    # Çıkış butonu
    if st.button("🚪 Çıkış Yap"):
        st.session_state.logged_in = False
        st.session_state.user_name = None
        st.rerun()