"""
GA4 Chatbot - Streamlit Web Arayuzu
Hurriyet Haber Sitesi Analytics
"""

import streamlit as st
import sys
import os
import html

# Proje klasorunu path'e ekle
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from chatbot import GA4Chatbot
from fuzzy_matcher import DimensionMetricMatcher, EditorMatcher, AuthorMatcher
from ga4_client import BRAND_PROPERTIES

# Sayfa ayarlari
st.set_page_config(
    page_title="GA4 Chatbot - Hurriyet Analytics",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS stilleri
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 1rem;
    }
    .sub-header {
        font-size: 1.2rem;
        color: #666;
        text-align: center;
        margin-bottom: 2rem;
    }
    .chat-message {
        padding: 1rem;
        border-radius: 10px;
        margin-bottom: 1rem;
    }
    .user-message {
        background-color: #e3f2fd;
        border-left: 4px solid #1976d2;
    }
    .bot-message {
        background-color: #f5f5f5;
        border-left: 4px solid #4caf50;
    }
    .example-query {
        background-color: #fff3e0;
        padding: 0.5rem 1rem;
        border-radius: 5px;
        margin: 0.25rem 0;
        cursor: pointer;
    }
    .metric-card {
        background-color: #ffffff;
        padding: 1rem;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        text-align: center;
    }
    .bot-response {
        background-color: #f8f9fa;
        border-left: 4px solid #4caf50;
        padding: 1rem;
        border-radius: 8px;
        margin: 0.5rem 0;
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    }
    .bot-response pre {
        background-color: #ffffff;
        padding: 1rem;
        border-radius: 5px;
        overflow-x: auto;
        font-size: 12px;
        line-height: 1.4;
        white-space: pre-wrap;
        word-wrap: break-word;
    }
    .bot-response table {
        width: 100%;
        border-collapse: collapse;
        margin-top: 10px;
    }
    .bot-response th, .bot-response td {
        border: 1px solid #ddd;
        padding: 8px;
        text-align: left;
    }
    .bot-response th {
        background-color: #4caf50;
        color: white;
    }
    .bot-response tr:nth-child(even) {
        background-color: #f2f2f2;
    }
</style>
""", unsafe_allow_html=True)

# Session state baslat
if "messages" not in st.session_state:
    st.session_state.messages = []
if "chatbot" not in st.session_state:
    st.session_state.chatbot = None
if "dm_matcher" not in st.session_state:
    st.session_state.dm_matcher = DimensionMetricMatcher()
if "editor_matcher" not in st.session_state:
    st.session_state.editor_matcher = None  # Chatbot baslatilinca set edilecek
if "author_matcher" not in st.session_state:
    st.session_state.author_matcher = None  # Chatbot baslatilinca set edilecek
if "selected_brand" not in st.session_state:
    st.session_state.selected_brand = "hurriyet"  # Varsayilan marka

# Sidebar
with st.sidebar:
    st.markdown("### 🔧 Ayarlar")

    # Marka secimi
    st.markdown("---")
    st.markdown("### 🏢 Marka Secimi")

    # Marka listesini olustur
    brand_options = {key: f"{info['name']} ({info['domain']})" for key, info in BRAND_PROPERTIES.items()}
    brand_keys = list(brand_options.keys())
    brand_labels = list(brand_options.values())

    # Mevcut secili markanin indexi
    current_index = brand_keys.index(st.session_state.selected_brand) if st.session_state.selected_brand in brand_keys else 0

    selected_brand_label = st.selectbox(
        "Marka",
        brand_labels,
        index=current_index,
        key="brand_selector"
    )

    # Secilen markayi bul
    selected_brand_key = brand_keys[brand_labels.index(selected_brand_label)]

    # Marka degistiyse chatbot'u yeniden baslat
    if selected_brand_key != st.session_state.selected_brand:
        st.session_state.selected_brand = selected_brand_key
        st.session_state.chatbot = None  # Chatbot'u sifirla
        st.rerun()

    # Chatbot durumu
    st.markdown("---")
    st.markdown("### 📊 Chatbot Durumu")

    if st.button("🔄 Chatbot'u Baslat/Yenile", use_container_width=True):
        with st.spinner("Chatbot yukleniyor..."):
            try:
                # Secili marka ile chatbot baslat
                from ga4_client import GA4Client
                client = GA4Client(brand=st.session_state.selected_brand)
                st.session_state.chatbot = GA4Chatbot()
                st.session_state.chatbot.client = client  # Client'i degistir
                # Editor ve Author matcher'lari chatbot'tan al
                st.session_state.editor_matcher = st.session_state.chatbot.editor_matcher
                st.session_state.author_matcher = st.session_state.chatbot.author_matcher
                st.success(f"Chatbot basariyla yuklendi! ({client.brand_name})")
            except Exception as e:
                st.error(f"Hata: {str(e)}")

    if st.session_state.chatbot:
        brand_info = BRAND_PROPERTIES.get(st.session_state.selected_brand, {})
        st.success(f"✅ Aktif: {brand_info.get('name', 'Bilinmeyen')}")
    else:
        st.warning("⚠️ Chatbot baslatilmadi")

    # Ornek sorgular
    st.markdown("---")
    st.markdown("### 💡 Ornek Sorgular")

    example_queries = [
        "Bugün kaç kullanıcı geldi?",
        "Dün en çok okunan haberler",
        "Son 7 günde cihaz dağılımı",
        "Dünün kategori özeti",
        "Cihaz türlerine göre kullanıcı oranı",
        "En popüler editörler",
        "Türkiye'den gelen trafik",
        "Haftalık trend raporu"
    ]

    for query in example_queries:
        if st.button(f"📝 {query}", key=f"example_{query}", use_container_width=True):
            st.session_state.selected_query = query

    # Test araclari
    st.markdown("---")
    st.markdown("### 🧪 Test Araclari")

    test_mode = st.selectbox(
        "Test Modu",
        ["Normal Chat", "Dimension/Metric Test", "Editor/Yazar Test"]
    )

    st.session_state.test_mode = test_mode

# Ana baslik - Aktif markaya gore dinamik
active_brand_info = BRAND_PROPERTIES.get(st.session_state.selected_brand, {"name": "Bilinmeyen"})
st.markdown('<p class="main-header">📊 GA4 Chatbot</p>', unsafe_allow_html=True)
st.markdown(f'<p class="sub-header">{active_brand_info["name"]} Analytics Asistani</p>', unsafe_allow_html=True)

# Tab'lar
tab1, tab2, tab3 = st.tabs(["💬 Chat", "🔍 Fuzzy Matcher Test", "📚 Dokumantasyon"])

with tab1:
    # Chat arayuzu
    st.markdown("### Soru Sorun")

    # Mesaj gecmisi
    chat_container = st.container()

    with chat_container:
        for i, msg in enumerate(st.session_state.messages):
            if msg["role"] == "user":
                st.markdown(f"""
                <div class="chat-message user-message">
                    <strong>👤 Siz:</strong><br>{msg["content"]}
                </div>
                """, unsafe_allow_html=True)
            else:
                # Bot yaniti
                st.markdown("**🤖 Chatbot:**")

                # DataFrame varsa tablo olarak goster
                if "dataframe" in msg and msg["dataframe"] is not None:
                    df = msg["dataframe"]
                    # Baslik ve ozet bilgisi
                    content_lines = msg["content"].split("\n")
                    # Sadece baslik satirlarini goster (= ile cevrelenmiş)
                    for line in content_lines[:5]:
                        if line.strip() and ("=" in line or line.strip().startswith("Toplam")):
                            st.markdown(f"**{line.strip()}**")

                    # Haftalik trend ise grafik goster
                    if "_chart_type" in df.columns and df["_chart_type"].iloc[0] == "weekly_trend":
                        # Grafik icin _chart_type sutununu kaldir
                        chart_df = df.drop(columns=["_chart_type"])

                        # Line chart olustur
                        st.line_chart(
                            chart_df.set_index("Tarih") if "Tarih" in chart_df.columns else chart_df,
                            use_container_width=True
                        )

                        # Tablo da goster
                        st.dataframe(
                            chart_df,
                            use_container_width=True,
                            hide_index=True
                        )
                    else:
                        # Normal DataFrame'i interaktif tablo olarak goster
                        st.dataframe(
                            df,
                            use_container_width=True,
                            hide_index=True,
                            height=min(400, 35 * len(df) + 38)  # Dinamik yukseklik
                        )
                    st.caption(f"Toplam {len(df)} satir")
                else:
                    # Normal metin yaniti
                    escaped_content = html.escape(msg["content"])
                    st.markdown(f"""
                    <div class="bot-response">
                        <pre>{escaped_content}</pre>
                    </div>
                    """, unsafe_allow_html=True)

    # Ornek sorgu secildiyse
    if "selected_query" in st.session_state and st.session_state.selected_query:
        user_input = st.session_state.selected_query
        st.session_state.selected_query = None
    else:
        user_input = None

    # Kullanici girisi
    col1, col2 = st.columns([5, 1])
    with col1:
        query = st.text_input(
            "Sorunuzu yazin:",
            value=user_input if user_input else "",
            placeholder="Ornegin: Bugun kac kullanici geldi?",
            key="chat_input"
        )
    with col2:
        send_button = st.button("📤 Gonder", use_container_width=True)

    # Mesaj gonder
    if (send_button or user_input) and (query or user_input):
        final_query = query if query else user_input

        # Kullanici mesajini ekle
        st.session_state.messages.append({"role": "user", "content": final_query})

        # Chatbot yaniti
        if st.session_state.chatbot:
            with st.spinner("Dusunuyor..."):
                try:
                    response = st.session_state.chatbot.process_query(final_query)
                    # DataFrame varsa ayri sakla
                    if hasattr(st.session_state.chatbot, 'last_dataframe') and st.session_state.chatbot.last_dataframe is not None:
                        st.session_state.messages.append({
                            "role": "assistant",
                            "content": response,
                            "dataframe": st.session_state.chatbot.last_dataframe.copy()
                        })
                        st.session_state.chatbot.last_dataframe = None
                    else:
                        st.session_state.messages.append({"role": "assistant", "content": response})
                except Exception as e:
                    error_msg = f"Hata olustu: {str(e)}"
                    st.session_state.messages.append({"role": "assistant", "content": error_msg})
        else:
            st.session_state.messages.append({
                "role": "assistant",
                "content": "⚠️ Chatbot henuz baslatilmadi. Lutfen sol menuden 'Chatbot'u Baslat' butonuna tiklayin."
            })

        st.rerun()

    # Temizle butonu
    if st.button("🗑️ Sohbeti Temizle"):
        st.session_state.messages = []
        st.rerun()

with tab2:
    st.markdown("### 🔍 Fuzzy Matcher Test Arayuzu")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("#### Dimension/Metric Testi")

        test_text = st.text_input(
            "Test metni girin:",
            placeholder="Ornegin: goruntuleme, kullanici, cihaz turleri",
            key="dm_test_input"
        )

        if st.button("🔬 Dimension/Metric Ara", use_container_width=True):
            if test_text:
                dm_matcher = st.session_state.dm_matcher

                # Dimension ara
                st.markdown("##### 📐 Dimension Sonuclari:")
                dim_result = dm_matcher.find_dimension(test_text)
                if dim_result:
                    st.success(f"✅ Bulunan: **{dim_result['api_name']}**")
                    st.info(f"Eslesme: {dim_result['matched_alias']} (Skor: {dim_result['score']:.2f})")
                else:
                    st.warning("Dimension bulunamadi")

                # Metric ara
                st.markdown("##### 📊 Metric Sonuclari:")
                metric_result = dm_matcher.find_metric(test_text)
                if metric_result:
                    st.success(f"✅ Bulunan: **{metric_result['api_name']}**")
                    st.info(f"Eslesme: {metric_result['matched_alias']} (Skor: {metric_result['score']:.2f})")
                else:
                    st.warning("Metric bulunamadi")

                # Tam sorgu analizi
                st.markdown("##### 📝 Tam Sorgu Analizi:")
                suggestions = dm_matcher.suggest_for_query(test_text)

                st.write(f"**Guven Seviyesi:** {suggestions['confidence']}")

                if suggestions.get('suggested_dimensions'):
                    st.write("**Bulunan Dimension'lar:**")
                    for d in suggestions['suggested_dimensions']:
                        st.write(f"  - {d['api_name']} (alias: {d['matched_alias']}, skor: {d['score']:.2f})")

                if suggestions.get('suggested_metrics'):
                    st.write("**Bulunan Metric'ler:**")
                    for m in suggestions['suggested_metrics']:
                        st.write(f"  - {m['api_name']} (alias: {m['matched_alias']}, skor: {m['score']:.2f})")

    with col2:
        st.markdown("#### Editor/Yazar Testi")

        editor_test = st.text_input(
            "Editor adi girin:",
            placeholder="Ornegin: ahmet yilmaz",
            key="editor_test_input"
        )

        if st.button("🔬 Editor/Yazar Ara", use_container_width=True):
            if editor_test:
                editor_matcher = st.session_state.editor_matcher
                author_matcher = st.session_state.author_matcher

                if not editor_matcher or not author_matcher:
                    st.warning("⚠️ Oncelikle sol menuden Chatbot'u baslatmaniz gerekiyor.")
                else:
                    # Editor ara
                    st.markdown("##### 👤 Editor Sonuclari:")
                    editor_result = editor_matcher.find_editor(editor_test)
                    if editor_result and editor_result.get("matches"):
                        for i, match in enumerate(editor_result["matches"][:5], 1):
                            st.write(f"{i}. {match['code']} (Skor: {match['score']:.2f})")
                    else:
                        st.warning("Editor bulunamadi")

                    # Yazar ara
                    st.markdown("##### ✍️ Yazar Sonuclari:")
                    author_result = author_matcher.find_editor(editor_test)
                    if author_result and author_result.get("matches"):
                        for i, match in enumerate(author_result["matches"][:5], 1):
                            st.write(f"{i}. {match['code']} (Skor: {match['score']:.2f})")
                    else:
                        st.warning("Yazar bulunamadi")

    # Toplu test
    st.markdown("---")
    st.markdown("#### 📋 Toplu Dimension/Metric Testi")

    test_queries = st.text_area(
        "Her satira bir sorgu yazin:",
        value="goruntuleme\nkullanici sayisi\nmobil cihazlar\nspor kategorisi\neditor performansi",
        height=150
    )

    if st.button("🚀 Toplu Test Calistir", use_container_width=True):
        queries = [q.strip() for q in test_queries.split("\n") if q.strip()]

        results = []
        for q in queries:
            dm_matcher = st.session_state.dm_matcher
            suggestions = dm_matcher.suggest_for_query(q)

            dims = [d['api_name'] for d in suggestions.get('suggested_dimensions', [])]
            metrics = [m['api_name'] for m in suggestions.get('suggested_metrics', [])]

            results.append({
                "Sorgu": q,
                "Dimensions": ", ".join(dims) if dims else "-",
                "Metrics": ", ".join(metrics) if metrics else "-",
                "Guven": suggestions['confidence']
            })

        # Sonuclari tablo olarak goster
        import pandas as pd
        df = pd.DataFrame(results)
        st.dataframe(df, use_container_width=True)

with tab3:
    st.markdown("### 📚 Kullanim Kilavuzu")

    st.markdown("""
    #### 🎯 Desteklenen Sorgu Turleri

    **1. Temel Metrikler:**
    - "Bugun kac kullanici geldi?"
    - "Dunku goruntuleme sayisi"
    - "Haftalik oturum sayisi"

    **2. Zaman Bazli Sorgular:**
    - "Bugun", "Dun", "Bu hafta", "Gecen hafta"
    - "Son 7 gun", "Son 30 gun"
    - "Bu ay", "Gecen ay"

    **3. Kategori Analizi:**
    - "Spor kategorisi performansi"
    - "Ekonomi haberleri goruntulenmeleri"
    - "Gundem bolumu kullanici sayisi"

    **4. Cihaz Analizi:**
    - "Mobil kullanici orani"
    - "Desktop vs mobil karsilastirmasi"
    - "Tablet kullanimlari"

    **5. Cografi Analiz:**
    - "Turkiye'den gelen trafik"
    - "Istanbul kullanicilari"
    - "Ulke bazli dagilim"

    **6. Editor/Yazar Performansi:**
    - "Ahmet Yilmaz'in haberleri"
    - "En cok okunan editorler"
    - "Yazar performans raporu"

    ---

    #### 🔧 Teknik Bilgiler

    - **Property ID:** 497151965
    - **Fuzzy Matching Esigi:** 0.6
    - **Desteklenen Dimension Sayisi:** 39
    - **Desteklenen Metric Sayisi:** 18
    - **Turkce Alias Sayisi:** 300+

    ---

    #### 💡 Ipuclari

    1. Dogal Turkce kullanin - sistem sizin dilinizi anlar
    2. Zaman belirtmezseniz "bugun" varsayilan olarak kullanilir
    3. Birden fazla dimension/metric kullanabilirsiniz
    4. Editor/yazar isimlerinde tam eslesme gerekmez
    """)

# Footer
st.markdown("---")
st.markdown(
    "<p style='text-align: center; color: #888;'>GA4 Chatbot - Hurriyet Analytics | Powered by Streamlit</p>",
    unsafe_allow_html=True
)
