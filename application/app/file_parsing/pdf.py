import PyPDF2

def ingest_pdf_data(file_location):
    pdfFileObject = open(file_location, 'rb')
    pdfReader = PyPDF2.PdfReader(pdfFileObject)
    pages = pdfReader.pages
    text_total = ""
    for i, page in enumerate(pages):
        text_total += f"PAGE {i+1} \n\n "+page.extract_text()
    pdfFileObject.close()
    return text_total