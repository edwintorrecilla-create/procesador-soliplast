import streamlit as st
import fitz
import io
import pandas as pd
from datetime import datetime
import os

# Configuración visual
st.set_page_config(page_title="Soliplast - TCC Reportes", page_icon="📊", layout="wide")

# Nombre del archivo de base de datos local
DB_FILE = "historial_stickers_soliplast.csv"

# Función para guardar en el historial
def registrar_en_historial(remesa, cantidad):
    nueva_fila = {
        "Fecha": datetime.now().strftime("%Y-%m-%d"),
        "Hora": datetime.now().strftime("%H:%M:%S"),
        "Remesa": remesa,
        "Cliente": "Homecenter",
        "Cantidad": cantidad
    }
    df_nuevo = pd.DataFrame([nueva_fila])
    
    if not os.path.isfile(DB_FILE):
        df_nuevo.to_csv(DB_FILE, index=False, encoding='utf-8-sig')
    else:
        df_nuevo.to_csv(DB_FILE, mode='a', header=False, index=False, encoding='utf-8-sig')

# Estilo Soliplast
st.markdown("""
    <style>
    .stButton>button { width: 100%; border-radius: 8px; background-color: #004a99; color: white; font-weight: bold; }
    .stMetric { background-color: #f0f2f6; padding: 15px; border-radius: 10px; border-left: 5px solid #004a99; }
    h1 { color: #004a99; }
    </style>
    """, unsafe_allow_html=True)

st.title("🏷️ Optimizador y Reportador TCC")
st.subheader("Control de Despachos Soliplast S.A.")

col_left, col_right = st.columns([2, 1])

# --- LÓGICA DE PROCESAMIENTO ---
with col_left:
    uploaded_file = st.file_uploader("Cargar PDF de TCC", type="pdf")

    if uploaded_file:
        with st.spinner('Procesando...'):
            doc_original = fitz.open(stream=uploaded_file.read(), filetype="pdf")
            pdf_stickers = fitz.open()
            
            # Detectar Remesa
            texto_p1 = doc_original[0].get_text()
            remesa = "SinRemesa"
            for linea in texto_p1.split('\n'):
                if "REMESA" in linea.upper():
                    remesa = "".join(filter(str.isdigit, linea)) or "SinRemesa"
            
            # Formato 100x50mm
            ancho_final, alto_final = 283.46, 141.73
            
            for pag in doc_original:
                areas = [fitz.Rect(0, 0, 612, 264), fitz.Rect(0, 264, 612, 528), fitz.Rect(0, 528, 612, 792)]
                for rect in areas:
                    if len(pag.get_text("text", clip=rect).strip()) > 5:
                        n_pag = pdf_stickers.new_page(width=ancho_final, height=alto_final)
                        n_pag.show_pdf_page(fitz.Rect(0, 0, ancho_final, alto_final), doc_original, pag.number, clip=rect)

            total_actual = len(pdf_stickers)
            
            if total_actual > 0:
                output = io.BytesIO()
                pdf_stickers.save(output)
                nombre_archivo = f"{remesa} - Homecenter - {total_actual} stickers.pdf"
                
                # --- GUARDAR EN EXCEL (CSV) ---
                # Evitar duplicados si se refresca la página
                if "ultimo_procesado" not in st.session_state or st.session_state.ultimo_procesado != remesa:
                    registrar_en_historial(remesa, total_actual)
                    st.session_state.ultimo_procesado = remesa

                st.success(f"✅ ¡Listo! {total_actual} stickers registrados para la remesa {remesa}.")
                st.download_button(
                    label=f"📥 DESCARGAR PDF: {nombre_archivo}",
                    data=output.getvalue(),
                    file_name=nombre_archivo,
                    mime="application/pdf"
                )

# --- SECCIÓN DE REPORTES (COLUMNA DERECHA) ---
with col_right:
    st.markdown("### 📈 Reporte Acumulado")
    
    if os.path.exists(DB_FILE):
        df_historial = pd.read_csv(DB_FILE)
        total_dia = df_historial[df_historial['Fecha'] == datetime.now().strftime("%Y-%m-%d")]['Cantidad'].sum()
        
        st.metric(label="Stickers Procesados Hoy", value=f"{total_dia} und")
        
        st.write("---")
        st.write("**Historial Reciente:**")
        st.dataframe(df_historial.tail(5), use_container_width=True)
        
        # Botón para descargar el Excel completo
        csv_buffer = io.StringIO()
        df_historial.to_csv(csv_buffer, index=False, encoding='utf-8-sig')
        st.download_button(
            label="📊 Descargar Reporte Excel (CSV)",
            data=csv_buffer.getvalue(),
            file_name=f"Reporte_Soliplast_{datetime.now().strftime('%m_%Y')}.csv",
            mime="text/csv"
        )
    else:
        st.info("Aún no hay datos registrados hoy.")

st.markdown("""<div style='text-align: center; color: #666; margin-top: 50px;'>Desarrollado para Edwin Torrecilla - Soliplast S.A.</div>""", unsafe_allow_html=True)
  


