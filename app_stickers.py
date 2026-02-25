import streamlit as st
import fitz
import io
import os

# 1. Configuración visual y Nombre de la pestaña
st.set_page_config(page_title="Soliplast - Homecenter", page_icon="🏷️", layout="wide")

# Estilo Soliplast mejorado
st.markdown("""
    <style>
    .stButton>button {
        width: 100%;
        border-radius: 8px;
        background-color: #004a99;
        color: white;
        height: 3em;
        font-weight: bold;
    }
    .stButton>button:hover { background-color: #003366; color: white; border: none; }
    h1 { color: #004a99; }
    .footer-custom {
        text-align: center;
        padding: 20px;
        color: #666;
        font-size: 0.9em;
        border-top: 1px solid #eee;
        margin-top: 50px;
    }
    </style>
    """, unsafe_allow_html=True)

# 3. Cambio de Nombre Principal
st.title("🏷️ Procesador de Guias TCC - Homecenter")
st.subheader("Formato optimizado: 100mm x 50mm")

# Contenedor central para la carga de archivos
col_left, col_right = st.columns([2, 1])

with col_left:
    uploaded_file = st.file_uploader("Cargar PDF original de TCC", type="pdf")

if uploaded_file:
    with st.spinner('Procesando etiquetas...'):
        doc_original = fitz.open(stream=uploaded_file.read(), filetype="pdf")
        pdf_stickers = fitz.open()
        
        # Lógica para detectar la Remesa
        texto_p1 = doc_original[0].get_text()
        remesa = "SinRemesa"
        for linea in texto_p1.split('\n'):
            if "REMESA" in linea.upper():
                remesa = "".join(filter(str.isdigit, linea)) or "SinRemesa"
        
        # Conversión mm a puntos para 100x50mm
        ancho_final = 283.46
        alto_final = 141.73
        
        for pag in doc_original:
            # Áreas de recorte estándar de TCC
            areas = [
                fitz.Rect(0, 0, 612, 264),    
                fitz.Rect(0, 264, 612, 528),  
                fitz.Rect(0, 528, 612, 792)   
            ]
            
            for rect in areas:
                if len(pag.get_text("text", clip=rect).strip()) > 5:
                    n_pag = pdf_stickers.new_page(width=ancho_final, height=alto_final)
                    target_rect = fitz.Rect(0, 0, ancho_final, alto_final)
                    n_pag.show_pdf_page(target_rect, doc_original, pag.number, clip=rect)

        total_stickers = len(pdf_stickers)

        if total_stickers > 0:
            output = io.BytesIO()
            pdf_stickers.save(output)
            
            # Nombre del archivo solicitado: # Remesa - Homecenter - # stickers
            nombre_archivo = f"{remesa} - Homecenter - {total_stickers} stickers.pdf"
            
            with col_right:
                st.success("✅ Procesamiento Exitoso")
                # Mostramos la métrica solo del archivo actual
                st.metric(label="Stickers Detectados", value=f"{total_stickers} und")
                
                st.download_button(
                    label="📥 DESCARGAR PARA IMPRESIÓN",
                    data=output.getvalue(),
                    file_name=nombre_archivo,
                    mime="application/pdf"
                )

# 4. Cambio de Pie de Página
st.markdown("""
    <div class="footer-custom">
        <b>Soliplast S.A.</b>
    </div>
    """, unsafe_allow_html=True)
  



