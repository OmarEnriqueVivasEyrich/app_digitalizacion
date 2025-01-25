import streamlit as st
from transformers import DonutProcessor, VisionEncoderDecoderModel
from pdf2image import convert_from_path
from fpdf import FPDF
import torch

# Verificar si se tiene PyTorch disponible
if not torch.cuda.is_available():
    st.warning("No se está utilizando GPU, el proceso puede ser más lento.")

# Cargar el modelo Donut preentrenado
@st.cache_resource
def cargar_modelo():
    processor = DonutProcessor.from_pretrained("naver-clova-ix/donut-base")
    model = VisionEncoderDecoderModel.from_pretrained("naver-clova-ix/donut-base")
    return processor, model

processor, model = cargar_modelo()

def extraer_texto_con_modelo(ruta_pdf):
    """
    Convierte cada página del PDF a imágenes y usa Donut para extraer texto.
    """
    # Convertir las páginas del PDF a imágenes
    paginas = convert_from_path(ruta_pdf, dpi=300)
    textos = []

    for i, pagina in enumerate(paginas, start=1):
        # Convertir la página a un tensor compatible con Donut
        pixel_values = processor(pagina, return_tensors="pt").pixel_values

        # Generar la predicción con el modelo
        output = model.generate(pixel_values)

        # Decodificar el texto extraído y almacenarlo
        texto = processor.batch_decode(output, skip_special_tokens=True)[0]
        textos.append(f"Página {i}:\n{texto.strip()}\n")

    return textos

def generar_pdf_con_texto(textos, ruta_pdf_salida):
    """
    Genera un nuevo archivo PDF con el texto extraído.
    """
    # Crear el objeto PDF
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.set_font("Arial", size=12)

    # Agregar las páginas con el texto extraído
    for texto in textos:
        pdf.add_page()
        pdf.multi_cell(0, 10, texto)

    # Guardar el archivo PDF generado
    pdf.output(ruta_pdf_salida)
    return ruta_pdf_salida

# Título de la aplicación
st.title("Extracción de texto de PDF con Donut")

# Cargar el archivo PDF de entrada
uploaded_file = st.file_uploader("Selecciona un archivo PDF", type=["pdf"])

if uploaded_file is not None:
    # Guardar el archivo subido temporalmente
    with open("temp.pdf", "wb") as f:
        f.write(uploaded_file.getbuffer())

    st.write("El archivo PDF ha sido cargado con éxito. Procesando...")

    # Extraer el texto utilizando el modelo Donut
    textos_extraidos = extraer_texto_con_modelo("temp.pdf")

    # Mostrar el texto extraído en la interfaz de Streamlit
    st.subheader("Texto Extraído:")
    for texto in textos_extraidos:
        st.write(texto)

    # Generar un archivo PDF con el texto extraído
    output_pdf_path = "texto_extraido.pdf"
    ruta_pdf_salida = generar_pdf_con_texto(textos_extraidos, output_pdf_path)

    # Proporcionar un enlace para descargar el archivo PDF generado
    with open(ruta_pdf_salida, "rb") as file:
        st.download_button(
            label="Descargar el PDF con el texto extraído",
            data=file,
            file_name="texto_extraido.pdf",
            mime="application/pdf"
        )
