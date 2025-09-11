import streamlit as st
import requests
import base64
import io

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

# 4) Webhook URL
st.subheader("4. Make webhook URL")
webhook_url = st.text_input("Vlož URL na Custom webhook v Make:", placeholder="https://hook.integromat.com/…")

# 5) Odeslání obsahu DOCX do Make
st.subheader("5. Odeslání dat do Make")
include_images = st.checkbox("Zahrnout obrázky do JSON (base64)")

template_selected = template.lower()

if st.button("📤 Odeslat do Make"):
    if not docx_file:
        st.error("Nejprve prosím nahraj .docx soubor.")
    elif not webhook_url:
        st.error("Zadej prosím Make webhook URL.")
    else:
        try:
            # připrav payload
            payload = {
                "template": template_selected,
                "raw_text": docx_file.getvalue().decode(errors="ignore")
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
            resp = requests.post(webhook_url, json=payload, timeout=30)
            if 200 <= resp.status_code < 300:
                st.success(f"✅ Odesláno do Make. HTTP {resp.status_code}")
                if resp.text:
                    st.code(resp.text)
            else:
                st.error(f"❌ Chyba při odesílání: HTTP {resp.status_code}")
                st.code(resp.text)
        except Exception as e:
            st.error(f"❌ Výjimka při odeslání: {e}")

st.caption("Pozn.: Streamlit pouze extrahuje binární obsah .docx (a volitelně obrázky) a posílá je do Make. Naparsování do jednotlivých proměnných proběhne v GPT modulu přímo v Make.")
