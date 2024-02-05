import os
import PyPDF2
import requests
from django.conf import settings

def get_pdf_text(pdf_path: os.path) -> tuple:
    """ Get text from specific page from PDF file
    
    Args:
        pdf_path (os.path): Path to PDF file
    
    Returns:
        tuple:
            str: Text from PDF file
    """
    
    # Read PDF file
    with open(pdf_path, 'rb') as file:
        pdf_reader = PyPDF2.PdfFileReader(file)

        # Extract text from specific page
        page = pdf_reader.getPage(0)
        text = page.extractText()
    
        return text


def split_pdf(input_path: os.path, output_folder: os.path):
    """ Split pdf file into multiple files
    
    Args:
        input_path (os.path): Path to PDF file
        output_folder (os.path): Path to output folder
    """
    
    # Download file from aws s3
    if "misojo.s3" in input_path:
        res = requests.get(input_path)
        file_base = input_path.split("/")[-1]
        input_path = os.path.join(settings.MEDIA_ROOT, file_base)
        with open(input_path, 'wb') as file:
            file.write(res.content)
    
    with open(input_path, 'rb') as file:
        pdf_reader = PyPDF2.PdfFileReader(file)
        total_pages = pdf_reader.numPages

        for page_number in range(total_pages):
            pdf_writer = PyPDF2.PdfFileWriter()
            pdf_writer.addPage(pdf_reader.getPage(page_number))

            output_path = f"{output_folder}/{page_number + 1}.pdf"
            with open(output_path, 'wb') as output_file:
                pdf_writer.write(output_file)


if __name__ == "__main__":
    current_folder = os.path.dirname(os.path.abspath(__file__))
    parent_folder = os.path.dirname(current_folder)
    pdf_file = os.path.join(parent_folder, 'sample.pdf')
    pdf_text, extracted = get_pdf_text(pdf_file, 1)
    print(pdf_text)