import streamlit as st
import requests
import base64
import io
from docx import Document

st.set_page_config(page_title="Generátor případových studií", layout="centered")
st.title("📄 Generátor případových studií → Odeslání do Make")

# 1) Výběr šablony
st.subheader("1. Vyber šablonu")
template = st.radio("Zvol verzi šablony:", ["Bright", "Soft"], horizontal=True)

# 2) Nahrání DOCX s obsahem
st.subheader("2. Nahraj .docx soubor s textem případové studie")
docx_file = st.file_uploader("Text případové studie", type="docx", key="docx")

# 3) Nahrání fotodokumentace (volitelné)
st.subheader("3. Nahraj fotodokumentaci (volitelné)")
images = st.file_uploader(
    "Obrázky (JPG, PNG)", type=["jpg", "jpeg", "png"], accept_multiple_files=True, key="images"
)

# Webhook URL (napevno)
WEBHOOK_URL = "https://hook.eu2.make.com/hjbp2yaxrmiprs6hrchfz0lxhetbbslt"

# Pomocná funkce pro extrakci textu z DOCX
def extract_text_from_docx(docx_bytes):
    doc = Document(io.BytesIO(docx_bytes))
    text = []
    for para in doc.paragraphs:
        if para.text.strip():
            text.append(para.text.strip())
    return "\n".join(text)

# 4) Odeslání obsahu DOCX do Make
st.subheader("4. Odeslání dat do Make")
include_images = st.checkbox("Zahrnout obrázky do JSON (base64)")

template_selected = template.lower()

if st.button("📤 Odeslat do Make"):
    if not docx_file:
        st.error("Nejprve prosím nahraj .docx soubor.")
    else:
        try:
            # extrahuj text z DOCX
            raw_text = extract_text_from_docx(docx_file.getvalue())

            # připrav payload
            payload = {
                "template": template_selected,
                "raw_text": raw_text
            }

            if include_images and images:
                imgs = []
                for i, img in enumerate(images):
                    b64 = base64.b64encode(img.getvalue()).decode("utf-8")
                    imgs.append({
                        "filename": img.name,
                        "content_type": img.type,
                        "content_base64": b64,
                    })
                payload["images"] = imgs

            # odeslat do Make
            resp = requests.post(WEBHOOK_URL, json=payload, timeout=30)
            if 200 <= resp.status_code < 300:
                st.success(f"✅ Odesláno do Make. HTTP {resp.status_code}")
                if resp.text:
                    st.code(resp.text)
            else:
                st.error(f"❌ Chyba při odesílání: HTTP {resp.status_code}")
                st.code(resp.text)
        except Exception as e:
            st.error(f"❌ Výjimka při odeslání: {e}")

st.caption("Pozn.: Streamlit nyní používá python-docx pro extrakci čitelného textu z .docx a odesílá jej do Make. Naparsování do placeholderů zajistí GPT modul v Make.")
