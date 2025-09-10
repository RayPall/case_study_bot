import streamlit as st
import requests
from docx import Document
import base64
import io

st.set_page_config(page_title="Generátor případových studií", layout="centered")
st.title("📄 Generátor případových studií → JSON pro Make")

# 1) Výběr šablony
st.subheader("1. Vyber šablonu")
template = st.radio("Zvol verzi šablony:", ["Bright", "Soft"], horizontal=True)

# 2) Nahrání DOCX s obsahem
st.subheader("2. Nahraj .docx soubor s textem případové studie")
docx_file = st.file_uploader("Text případové studie", type="docx", key="docx")

# 3) Nahrání fotodokumentace (volitelně)
st.subheader("3. Nahraj fotodokumentaci (volitelné)")
images = st.file_uploader(
    "Obrázky (JPG, PNG)", type=["jpg", "jpeg", "png"], accept_multiple_files=True, key="images"
)

# 4) Webhook URL
st.subheader("4. Make webhook URL")
webhook_url = "https://hook.eu2.make.com/hjbp2yaxrmiprs6hrchfz0lxhetbbslt"

# Pomocná funkce: DOCX → JSON (podle nadpisů)
def parse_docx_to_json(docx_bytes):
    doc = Document(io.BytesIO(docx_bytes))
    data = {}
    current_heading = None

    mapping = {
        "Zákazník": "zakaznik",
        "Výzva": "vyzva",
        "Řešení": "reseni",
        "Výsledky": "vysledky",
        "O společnosti": "spolecnost"
    }

    for para in doc.paragraphs:
        text = para.text.strip()
        if not text:
            continue
        if para.style and para.style.name and para.style.name.startswith("Heading"):
            current_heading = mapping.get(text, None)
        elif current_heading:
            if current_heading not in data:
                data[current_heading] = text
            else:
                data[current_heading] += "\n" + text

    return data

# 5) Zpracování → JSON
st.subheader("5. Zpracování")
include_images = st.checkbox("Zahrnout obrázky do JSON (base64)")

template_selected = template.lower()

if st.button("🧠 Vytvořit JSON náhled"):
    if not docx_file:
        st.error("Nejprve prosím nahraj .docx soubor.")
    else:
        parsed_data = parse_docx_to_json(docx_file.getvalue())
        payload = {
            "template": template_selected,
            "data": parsed_data,
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
        st.success("✅ JSON připraven. Zkontroluj obsah níže.")
        st.json(payload)
        st.session_state["last_payload"] = payload

# 6) Odeslání na Make webhook (application/json)
if st.button("🚀 Odeslat JSON do Make"):
    payload = st.session_state.get("last_payload")
    if not payload:
        st.error("Nejprve vytvoř JSON náhled (tlačítko výše).")
    elif not webhook_url:
        st.error("Zadej prosím Make webhook URL.")
    else:
        try:
            resp = requests.post(webhook_url, json=payload, timeout=30)
            if 200 <= resp.status_code < 300:
                st.success(f"✅ Odesláno. HTTP {resp.status_code}")
                # Volitelně zobrazit odpověď serveru
                if resp.text:
                    st.code(resp.text)
            else:
                st.error(f"❌ Chyba při odesílání: HTTP {resp.status_code}")
                st.code(resp.text)
        except Exception as e:
            st.error(f"❌ Výjimka při odeslání: {e}")

# Info
st.caption(
    "Pozn.: Obrázky v JSONu jsou base64. Pokud bude payload příliš velký, zvaž uložení obrázků do úložiště (Drive/S3) a posílej jen URL.")
