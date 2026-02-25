import streamlit as st
import fitz
import io
import os

# 1. Configuración visual
st.set_page_config(page_title="Soliplast - Homecenter", page_icon="🏷️", layout="wide")

# Estilo CSS para el logo y la interfaz
st.markdown("""
    <style>
    .stButton>button {
        width: 100%;
        border-radius: 8px;
        background-color: #004a99;
        color: white;
        height: 3.5em;
        font-weight: bold;
    }
    .stButton>button:hover { background-color: #003366; color: white; border: none; }
    h1 { color: #004a99; margin-bottom: 0; }
    .footer-custom {
        text-align: center;
        padding: 20px;
        color: #666;
        font-size: 0.9em;
        border-top: 1px solid #eee;
        margin-top: 50px;
    }
    .logo-img {
        display: flex;
        align-items: center;
        gap: 20px;
    }
    </style>
    """, unsafe_allow_html=True)

# Encabezado con LOGO (si existe el archivo logo.png)
col_logo, col_titulo = st.columns([1, 4])
with col_logo:
    if os.path.exists("logo.png"):
        st.image("logo.png", width=150)
    else:
        st.info("Coloca 'logo.png' en la carpeta.")

with col_titulo:
    st.title("Procesador de Guías TCC - Homecenter")
    st.caption("Optimización Logística | Formato 100mm x 50mm")

st.divider()

# Contenedor central
col_left, col_right = st.columns([2, 1])

with col_left:
    uploaded_file = st.file_uploader("Cargar PDF original de TCC", type="pdf")

if uploaded_file:
    with st.spinner('Procesando etiquetas...'):
        # Leer el documento
        doc_original = fitz.open(stream=uploaded_file.read(), filetype="pdf")
        pdf_stickers = fitz.open()
        
        # --- LÓGICA DE NOMBRE DE ARCHIVO Y REMESA ---
        texto_p1 = doc_original[0].get_text()
        remesa_num = "SinRemesa"
        
        for linea in texto_p1.split('\n'):
            if "REMESA" in linea.upper():
                # Extraemos solo los números
                solo_numeros = "".join(filter(str.isdigit, linea))
                if solo_numeros:
                    remesa_num = solo_numeros
                break
        
        # Medidas para 100x50mm
        ancho_final, alto_final = 283.46, 141.73
        
        # Procesar páginas
        for pag in doc_original:
            areas = [
                fitz.Rect(0, 0, 612, 264),    
                fitz.Rect(0, 264, 612, 528),  
                fitz.Rect(0, 528, 612, 792)   
            ]
            for rect in areas:
                if len(pag.get_text("text", clip=rect).strip()) > 5:
                    n_pag = pdf_stickers.new_page(width=ancho_final, height=alto_final)
                    n_pag.show_pdf_page(fitz.Rect(0, 0, ancho_final, alto_final), doc_original, pag.number, clip=rect)

        total = len(pdf_stickers)

        if total > 0:
            # Preparamos el archivo de salida
            output = io.BytesIO()
            pdf_stickers.save(output)
            
            # NOMBRE DE ARCHIVO SOLICITADO: # Remesa - Homecenter - # stickers
            nombre_final = f"{remesa_num} - Homecenter - {total} stickers.pdf"
            
            with col_right:
                st.success("✅ Procesamiento Exitoso")
                st.metric(label="Stickers Detectados", value=f"{total} und")
                
                # El botón ahora usa el nombre dinámico garantizado
                st.download_button(
                    label=f"📥 DESCARGAR: {nombre_final}",
                    data=output.getvalue(),
                    file_name=nombre_final,
                    mime="application/pdf"
                )

# Pie de Página simplificado
st.markdown("""
    <div class="footer-custom">
        <b>Soliplast S.A.</b>
    </div>
    """, unsafe_allow_html=True)



