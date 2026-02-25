import streamlit as st
import fitz
import io

# Configuración visual avanzada
st.set_page_config(page_title="Soliplast - TCC Homecenter", page_icon="🏷️", layout="wide")

# Estilo Soliplast
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
        font-size: 0.8em;
        border-top: 1px solid #eee;
        margin-top: 50px;
    }
    </style>
    """, unsafe_allow_html=True)

st.title("🏷️ Optimizador de Etiquetas TCC")
st.subheader("Cliente: Homecenter | Formato: 100mm x 50mm")

col_left, col_right = st.columns([2, 1])

with col_left:
    uploaded_file = st.file_uploader("Cargar PDF original de TCC", type="pdf")

if uploaded_file:
    with st.spinner('Procesando y contando etiquetas...'):
        doc_original = fitz.open(stream=uploaded_file.read(), filetype="pdf")
        pdf_stickers = fitz.open()
        
        # 1. Lógica para detectar la Remesa
        texto_p1 = doc_original[0].get_text()
        remesa = "SinRemesa"
        for linea in texto_p1.split('\n'):
            if "REMESA" in linea.upper():
                remesa = "".join(filter(str.isdigit, linea)) or "SinRemesa"
        
        # Medidas para 100mm x 50mm
        ancho_final = 283.46
        alto_final = 141.73
        
        for pag in doc_original:
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

        # 2. Conteo total de stickers procesados
        total_stickers = len(pdf_stickers)

        if total_stickers > 0:
            output = io.BytesIO()
            pdf_stickers.save(output)
            
            # 3. Construcción del nombre del archivo según tu solicitud
            # Formato: # Remesa - Homecenter - # stickers
            nombre_archivo = f"{remesa} - Homecenter - {total_stickers} stickers.pdf"
            
            with col_right:
                st.success("✅ Procesamiento completado")
                
                # Indicador visual del número de stickers
                st.metric(label="Stickers a Imprimir", value=f"{total_stickers} unidades")
                
                st.info(f"**Archivo:** {nombre_archivo}")
                
                st.download_button(
                    label="📥 DESCARGAR PARA IMPRESIÓN",
                    data=output.getvalue(),
                    file_name=nombre_archivo,
                    mime="application/pdf"
                )

# Pie de página
st.markdown(f"""
    <div class="footer-custom">
        <b>Soliplast S.A.</b><br>
        Eficiencia en Despachos: Formato 100x50 optimizado.
    </div>
    """, unsafe_allow_html=True)
  

