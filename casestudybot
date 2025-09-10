import streamlit as st
import requests

st.set_page_config(page_title="Generátor případových studií", layout="centered")
st.title("📄 Generátor případových studií")

# Výběr šablony
st.subheader("1. Vyber šablonu")
template = st.radio("Zvol verzi šablony:", ["Bright", "Soft"], horizontal=True)

# Nahrání dokumentu s textem
st.subheader("2. Nahraj .docx soubor s textem případové studie")
docx_file = st.file_uploader("Text případové studie", type="docx", key="docx")

# Nahrání fotodokumentace (obrázky)
st.subheader("3. Nahraj fotodokumentaci (volitelné)")
images = st.file_uploader("Obrázky (JPG, PNG)", type=["jpg", "jpeg", "png"], accept_multiple_files=True, key="images")

# Tlačítko pro odeslání
template_selected = template.lower()

if st.button("📤 Odeslat ke zpracování"):
    if not docx_file:
        st.error("Nejprve prosím nahraj .docx soubor.")
    else:
        with st.spinner("Odesílám data ke zpracování..."):
            files = {
                'docx': (docx_file.name, docx_file.getvalue(), 'application/vnd.openxmlformats-officedocument.wordprocessingml.document')
            }
            for i, img in enumerate(images):
                files[f'image_{i}'] = (img.name, img.getvalue(), img.type)

            data = {'template': template_selected}
            
            # ZDE VLOŽ SVOU WEBHOOK URL:
            webhook_url = "https://hook.integromat.com/TVŮJ_WEBHOOK_URL"

            try:
                response = requests.post(webhook_url, data=data, files=files)
                if response.status_code == 200:
                    st.success("✅ Prezentace byla úspěšně odeslána ke zpracování.")
                    # volitelně: nabídnout stažení
                else:
                    st.error(f"❌ Chyba při zpracování: {response.status_code}")
            except Exception as e:
                st.error(f"❌ Nepodařilo se odeslat data: {str(e)}")
