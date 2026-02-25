import streamlit as st
import fitz
import io

# 1. Configuración de la página
st.set_page_config(page_title="Soliplast - Homecenter", page_icon="🏷️", layout="wide")

# Estilo CSS Personalizado
st.markdown("""
    <style>
    .stButton>button {
        width: 100%;
        border-radius: 8px;
        background-color: #004a99;
        color: white;
        height: 3.5em;
        font-weight: bold;
        font-size: 1.1em;
    }
    .stButton>button:hover { background-color: #003366; color: white; border: none; }
    h1 { color: #004a99; margin-bottom: 5px; }
    .stMetric { background-color: #f8f9fa; padding: 10px; border-radius: 10px; border: 1px solid #eee; }
    .footer-custom {
        text-align: center;
        padding: 25px;
        color: #888;
        font-size: 0.9em;
        border-top: 1px solid #eee;
        margin-top: 60px;
    }
    </style>
    """, unsafe_allow_html=True)

# 2. Encabezado de la Aplicación (Solo texto)
st.title("Procesador de Guías TCC - Homecenter")
st.markdown("### Soliplast S.A.")
st.caption("Herramienta de optimización para etiquetas térmicas de 100mm x 50mm")
st.divider()

# Layout Principal
col_left, col_right = st.columns([2, 1])

with col_left:
    uploaded_file = st.file_uploader("Subir PDF de Guías TCC", type="pdf")

if uploaded_file:
    with st.spinner('Procesando PDF...'):
        # Leer PDF original
        doc_original = fitz.open(stream=uploaded_file.read(), filetype="pdf")
        pdf_stickers = fitz.open()
        
        # --- EXTRACCIÓN DE REMESA ---
        texto_p1 = doc_original[0].get_text()
        remesa_num = "SinRemesa"
        for linea in texto_p1.split('\n'):
            if "REMESA" in linea.upper():
                # Extraemos solo dígitos de la línea donde dice REMESA
                remesa_limpia = "".join(filter(str.isdigit, linea))
                if remesa_limpia:
                    remesa_num = remesa_limpia
                break
        
        # Medidas en puntos (100mm x 50mm)
        ancho_pt = 283.46 
        alto_pt = 141.73  
        
        # --- PROCESAMIENTO DE GUÍAS ---
        for pag in doc_original:
            areas = [
                fitz.Rect(0, 0, 612, 264),    
                fitz.Rect(0, 264, 612, 528),  
                fitz.Rect(0, 528, 612, 792)   
            ]
            for rect in areas:
                if len(pag.get_text("text", clip=rect).strip()) > 5:
                    n_pag = pdf_stickers.new_page(width=ancho_pt, height=alto_pt)
                    # Ajustamos el contenido al 100% de la etiqueta de 10x5
                    n_pag.show_pdf_page(fitz.Rect(0, 0, ancho_pt, alto_pt), doc_original, pag.number, clip=rect)

        total_final = len(pdf_stickers)

        if total_final > 0:
            # Guardar en memoria
            output = io.BytesIO()
            pdf_stickers.save(output)
            
            # NOMBRE DE ARCHIVO: # Remesa - Homecenter - # stickers
            nombre_archivo_final = f"{remesa_num} - Homecenter - {total_final} stickers.pdf"
            
            with col_right:
                st.success("✅ Procesamiento Exitoso")
                st.metric(label="Stickers Generados", value=f"{total_final} unidades")
                
                # Descarga con el nombre de archivo dinámico
                st.download_button(
                    label="📥 DESCARGAR PDF PARA IMPRESIÓN",
                    data=output.getvalue(),
                    file_name=nombre_archivo_final,
                    mime="application/pdf"
                )

# 3. Pie de Página
st.markdown("""
    <div class="footer-custom">
        <b>Soliplast S.A.</b>
    </div>
    """, unsafe_allow_html=True)




