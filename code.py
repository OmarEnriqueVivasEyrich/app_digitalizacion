import streamlit as st
from PIL import Image
import pytesseract
from pdf2image import convert_from_path
from fpdf import FPDF
import tempfile

# Título de la aplicación
st.title("Extracción de texto de PDF con OCR")

# Subir archivo PDF
uploaded_file = st.file_uploader("Selecciona un archivo PDF", type=["pdf"])

def extraer_texto_con_ocr(pdf_path):
    """Convierte las páginas del PDF en imágenes y extrae el texto con Tesseract OCR."""
    # Convertir el PDF a imágenes
    paginas = convert_from_path(pdf_path, dpi=300)
    textos = []
    
    # Extraer texto de cada página usando Tesseract
    for i, pagina in enumerate(paginas):
        texto = pytesseract.image_to_string(pagina)
        textos.append(f"Página {i+1}:\n{texto.strip()}\n")
    
    return textos

def generar_pdf_con_texto(textos):
    """Genera un archivo PDF con el texto extraído."""
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.set_font("Arial", size=12)
    
    for texto in textos:
        pdf.add_page()
        pdf.multi_cell(0, 10, texto)
    
    # Guardar el archivo PDF
    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.pdf')
    pdf.output(temp_file.name)
    return temp_file.name

if uploaded_file is not None:
    # Guardar el archivo PDF temporalmente
    with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as temp_pdf:
        temp_pdf.write(uploaded_file.getbuffer())
        temp_pdf_path = temp_pdf.name
    
    st.write("El archivo PDF ha sido cargado con éxito. Procesando...")

    # Extraer texto con OCR
    textos_extraidos = extraer_texto_con_ocr(temp_pdf_path)

    # Mostrar el texto extraído
    st.subheader("Texto Extraído:")
    for texto in textos_extraidos:
        st.write(texto)

    # Generar un archivo PDF con el texto extraído
    output_pdf_path = generar_pdf_con_texto(textos_extraidos)

    # Proporcionar un enlace para descargar el archivo PDF generado
    with open(output_pdf_path, "rb") as file:
        st.download_button(
            label="Descargar el PDF con el texto extraído",
            data=file,
            file_name="texto_extraido.pdf",
            mime="application/pdf"
        )
