import streamlit as st
import fitz
import io

# Configuración visual avanzada
st.set_page_config(page_title="Procesador Soliplast", page_icon="🏷️", layout="wide")

# CSS para estilo Soliplast (Azul y Gris)
st.markdown("""
    <style>
    .stButton>button {
        width: 100%;
        border-radius: 8px;
        background-color: #004a99;
        color: white;
    }
    .stButton>button:hover { background-color: #003366; color: white; border: none; }
    h1 { color: #004a99; }
    footer { visibility: hidden; }
    .footer-custom {
        text-align: center;
        padding: 20px;
        color: #666;
        font-size: 0.9em;
    }
    </style>
    """, unsafe_allow_html=True)

# Encabezado
st.title("🏷️ Procesador de Stickers Soliplast")
st.caption("Herramienta de optimización logística para guías TCC")
st.divider()

col_left, col_right = st.columns([2, 1])

with col_left:
    uploaded_file = st.file_uploader("Sube el PDF de guías TCC", type="pdf")

if uploaded_file:
    with st.spinner('Procesando...'):
        doc_original = fitz.open(stream=uploaded_file.read(), filetype="pdf")
        pdf_stickers = fitz.open()
        
        # Lógica de remesa
        texto_p1 = doc_original[0].get_text()
        remesa = "SinRemesa"
        for linea in texto_p1.split('\n'):
            if "REMESA" in linea.upper():
                remesa = "".join(filter(str.isdigit, linea)) or "SinRemesa"
        
        for pag in doc_original:
            areas = [fitz.Rect(0, 0, 612, 264), fitz.Rect(0, 264, 612, 528), fitz.Rect(0, 528, 612, 792)]
            for rect in areas:
                if len(pag.get_text("text", clip=rect).strip()) > 2:
                    n_pag = pdf_stickers.new_page(width=283, height=141)
                    n_pag.show_pdf_page(n_pag.rect, doc_original, pag.number, clip=rect)

        if len(pdf_stickers) > 0:
            output = io.BytesIO()
            pdf_stickers.save(output)
            
            with col_right:
                st.subheader("📊 Resumen")
                st.info(f"Remesa: {remesa}")
                st.metric("Stickers Generados", len(pdf_stickers))
                
                st.download_button(
                    label="📥 DESCARGAR PARA IMPRESIÓN",
                    data=output.getvalue(),
                    file_name=f"TCC - {remesa} - SOLIPLAST.pdf",
                    mime="application/pdf"
                )

# Pie de página personalizado
st.markdown("""
    <div class="footer-custom">
        Desarrollado con Inteligencia Artificial por <b>Edwin Torrecilla</b> para <b>Soliplast S.A.</b>
    </div>
    """, unsafe_allow_html=True)