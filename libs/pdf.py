import os
import PyPDF2


def get_pdf_text(pdf_path: os.path, page_num: int) -> tuple:
    """ Get text from specific page from PDF file
    
    Args:
        pdf_path (os.path): Path to PDF file
        page (int): Page number to extract text from
    
    Returns:
        tuple:
            str: Text from PDF file
            bool: True if page exists, False otherwise
    """
    
    page_num -= 1
    
    # Read PDF file
    with open(pdf_path, 'rb') as file:
        pdf_reader = PyPDF2.PdfFileReader(file)
        num_pages = pdf_reader.numPages
        
        # Validate page number
        if page_num >= num_pages:
            return "", False

        # Extract text from specific page
        page = pdf_reader.getPage(page_num)
        text = page.extractText()
    
        return text, True


if __name__ == "__main__":
    current_folder = os.path.dirname(os.path.abspath(__file__))
    parent_folder = os.path.dirname(current_folder)
    pdf_file = os.path.join(parent_folder, 'sample.pdf')
    pdf_text, extracted = get_pdf_text(pdf_file, 1)
    print(pdf_text)