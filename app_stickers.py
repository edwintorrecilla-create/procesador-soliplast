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
st.caption("Herramienta de optimización logística para guías TCC (Formato 100mm x 100mm)")
st.divider()

col_left, col_right = st.columns([2, 1])

with col_left:
    uploaded_file = st.file_uploader("Sube el PDF de guías TCC", type="pdf")

if uploaded_file:
    with st.spinner('Procesando y centrando etiquetas...'):
        doc_original = fitz.open(stream=uploaded_file.read(), filetype="pdf")
        pdf_stickers = fitz.open()
        
        # Lógica de remesa
        texto_p1 = doc_original[0].get_text()
        remesa = "SinRemesa"
        for linea in texto_p1.split('\n'):
            if "REMESA" in linea.upper():
                remesa = "".join(filter(str.isdigit, linea)) or "SinRemesa"
        
        # Medidas en puntos (100mm = 283.46 pts)
        lado_sticker = 283.46 
        
        for pag in doc_original:
            # Definimos las áreas de recorte originales del PDF de TCC
            areas = [fitz.Rect(0, 0, 612, 264), fitz.Rect(0, 264, 612, 528), fitz.Rect(0, 528, 612, 792)]
            
            for rect in areas:
                # Verificamos si hay contenido en el área
                if len(pag.get_text("text", clip=rect).strip()) > 2:
                    # 1. Creamos la nueva página cuadrada de 100x100mm
                    n_pag = pdf_stickers.new_page(width=lado_sticker, height=lado_sticker)
                    
                    # 2. Calculamos la proporción para que el ancho encaje perfectamente
                    # El ancho original es 612, el nuevo es 283.46
                    escala = lado_sticker / rect.width
                    alto_proporcional = rect.height * escala
                    
                    # 3. Calculamos el margen superior para centrar verticalmente
                    # (Alto total - Alto de la imagen escalada) / 2
                    margen_superior = (lado_sticker - alto_proporcional) / 2
                    
                    # 4. Definimos el rectángulo de destino centrado
                    target_rect = fitz.Rect(0, margen_superior, lado_sticker, margen_superior + alto_proporcional)
                    
                    # 5. Insertamos la porción del PDF original en el nuevo espacio centrado
                    n_pag.show_pdf_page(target_rect, doc_original, pag.number, clip=rect)

        if len(pdf_stickers) > 0:
            output = io.BytesIO()
            pdf_stickers.save(output)
            
            with col_right:
                st.subheader("📊 Resumen")
                st.info(f"Remesa: {remesa}")
                st.metric("Stickers Generados", len(pdf_stickers))
                st.success("Formato: 100mm x 100mm (Centrado)")
                
                st.download_button(
                    label="📥 DESCARGAR PARA IMPRESIÓN",
                    data=output.getvalue(),
                    file_name=f"TCC_100x100_{remesa}.pdf",
                    mime="application/pdf"
                )

# Pie de página personalizado
st.markdown("""
    <div class="footer-custom">
        Desarrollado con Inteligencia Artificial por <b>Edwin Torrecilla</b> para <b>Soliplast S.A.</b>
    </div>
    """, unsafe_allow_html=True)
