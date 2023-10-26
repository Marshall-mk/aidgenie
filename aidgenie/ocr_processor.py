import pdfminer
import textwrap
import pdfminer.high_level
import matplotlib.pyplot as plt
from pdfminer.layout import LAParams

# import torch
# from PIL import Image
# from donut import DonutModel
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


# def ocrpdf(file_path, question):
#     pretrained_model = DonutModel.from_pretrained("naver-clova-ix/donut-base-finetuned-docvqa")
#     input_img = Image.open(file_path)
#     #input_img = Image.fromarray(file_path)
#     task_name = "docvqa"
#     task_prompt = "<s_docvqa><s_question>{user_input}</s_question><s_answer>"
#     user_prompt = task_prompt.replace("{user_input}", question)
#     if torch.cuda.is_available():
#         pretrained_model.half()
#         device = torch.device("cuda")
#         pretrained_model.to(device)
#     else:
#         pretrained_model.encoder.to(torch.bfloat16)
#     pretrained_model.eval()
#     output = pretrained_model.inference(input_img, prompt=user_prompt)["predictions"][0]
# c = ocrpdf("../data/hamzah_report.jpg", "What is the conclusion")


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
        pass
    # Analyze
    result = model(doc)
    # result.show(doc)
    # synthetic_pages = result.synthesize()
    # plt.imshow(synthetic_pages[0]); plt.axis('off'); plt.show()
    return result.export()


# json_output = ocrpdf("../data/hamzah_report.jpg")
# print(json_output)


# inferenceModel.py
# import cv2
# import typing
# import numpy as np

# from mltu.inferenceModel import OnnxInferenceModel
# from mltu.utils.text_utils import ctc_decoder, get_cer

# class ImageToWordModel(OnnxInferenceModel):
#     def __init__(self, char_list: typing.Union[str, list], *args, **kwargs):
#         super().__init__(*args, **kwargs)
#         self.char_list = char_list

#     def predict(self, image: np.ndarray):
#         image = cv2.resize(image, self.input_shape[:2][::-1])

#         image_pred = np.expand_dims(image, axis=0).astype(np.float32)

#         preds = self.model.run(None, {self.input_name: image_pred})[0]

#         text = ctc_decoder(preds, self.char_list)[0]

#         return text

# if __name__ == "__main__":
#     import pandas as pd
#     from tqdm import tqdm
#     from mltu.configs import BaseModelConfigs

#     configs = BaseModelConfigs.load("Models/03_handwriting_recognition/202212290905/configs.yaml")

#     model = ImageToWordModel(model_path=configs.model_path, char_list=configs.vocab)

#     df = pd.read_csv("Models/03_handwriting_recognition/202212290905/val.csv").values.tolist()

#     accum_cer = []
#     for image_path, label in tqdm(df):
#         image = cv2.imread(image_path)

#         prediction_text = model.predict(image)

#         cer = get_cer(prediction_text, label)
#         print(f"Image: {image_path}, Label: {label}, Prediction: {prediction_text}, CER: {cer}")

#         accum_cer.append(cer)

#     print(f"Average CER: {np.average(accum_cer)}")
