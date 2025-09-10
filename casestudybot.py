import streamlit as st
import requests
from docx import Document
import io

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

# Tlačítko pro stažení šablony
st.subheader("4. Stáhni si šablonu prezentace")
st.markdown("[📥 Stáhnout ZIP se šablonami](https://drive.google.com/file/d/1-O8hJTC18m3w_t1Jd6OyA07uhQhs7Ycn/view?usp=sharing)")

# Pomocná funkce pro parsování DOCX na JSON strukturu
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
        if para.style.name.startswith("Heading"):
            current_heading = mapping.get(text, None)
        elif current_heading:
            if current_heading not in data:
                data[current_heading] = text
            else:
                data[current_heading] += "\n" + text

    return data

# Tlačítko pro odeslání
template_selected = template.lower()

if st.button("📤 Zpracovat případovou studii"):
    if not docx_file:
        st.error("Nejprve prosím nahraj .docx soubor.")
    else:
        with st.spinner("Zpracovávám dokument..."):
            parsed_data = parse_docx_to_json(docx_file.getvalue())
            st.success("✅ Data byla úspěšně načtena.")
            st.json(parsed_data)
