import pdfminer
import textwrap
import pdfminer.high_level
import matplotlib.pyplot as plt
from pdfminer.layout import LAParams

import warnings

warnings.filterwarnings("ignore")


# converts pdf to text
def pdf_2_text(file):
    """
    Converts a PDF file to text.

    Args:
        file (str): The path to the PDF file.

    Returns:
        str: The text extracted from the PDF file.
    """
    with open(file, "rb") as fp:
        text = pdfminer.high_level.extract_text(
            fp,
            codec="utf-8",
            laparams=LAParams(
                line_margin=0.5,
                word_margin=0.1,
                boxes_flow=0.5,
                detect_vertical=True,
                all_texts=True,
            ),
            maxpages=0,
        )
    return text


def chunk_text(text):
    """
    Splits a text into chunks of 4000 characters.

    Args:
        text (str): The text to be chunked.

    Returns:
        list: A list of text chunks.
    """
    return textwrap.wrap(text, 4000)


def ocrpdf(file_path):
    from doctr.io import DocumentFile
    from doctr.models import ocr_predictor

    model = ocr_predictor(pretrained=True)
    if file_path.endswith(".pdf"):
        # PDF
        doc = DocumentFile.from_pdf(file_path)
    elif (
        file_path.endswith(".png")
        or file_path.endswith(".jpg")
        or file_path.endswith(".jpeg")
    ):
        # image
        doc = DocumentFile.from_images(file_path)
    else:
        print("Upload a recognized file!")
    # Analyze
    result = model(doc)
    # result.show(doc)
    # synthetic_pages = result.synthesize()
    # plt.imshow(synthetic_pages[0]); plt.axis('off'); plt.show()
    result.show(doc)
    return result.export()
