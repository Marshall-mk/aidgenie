import json
import textwrap
import warnings
import streamlit as st
st.set_page_config(layout="wide")
from streamlit_option_menu import option_menu
from ocr_processor import pdf_2_text, ocrpdf
from image_converter import ImageConverter
from streamlit_extras.colored_header import colored_header
from arxiv_paper import search_arxiv, arxiv_2_file
from image_annotation import run_cls, run_seg, dataframe_annotation
from utils import about, features, chunk_text, mission, vision, contact
from dicom_viewer_and_annon import anonymize_dicom_file, dicom_viewer
warnings.filterwarnings("ignore")

def try_out():
    #  headings and tabs creation
    ConvertStoreTab, DicomExTab, AnonGenTab, OCRTab, PapersTab, ImgAnnotationTab = st.tabs(["Convert and Store Image Datasets", "Dicom Image Explorer and Anonymizer", 
                                        "Anonymize Reports and Generate Tags", " Extract Reports from Docs", "Research Here/Check Out Papers", "Annonate Images and Generate Datasets"])

    # ConvertStoreTab: Here is the entry point for image processing
    with ConvertStoreTab:
        image_path = st.file_uploader("Upload an Image", key='ConvertStoreTab_image')
        
        if image_path is not None:
            image_converter = ImageConverter(image_path.name)
            option = st.selectbox('What format would you like?',
                                        ('None','JPG',  'PNG', 'H5', 'HDF5'))
            # Image Dataset Conversion           
            if option == 'JPG':
                image_converter.convert_to_jpg()
                st.success('Image Converted to JPEG!')

            elif option == 'PNG':
                image_converter.convert_to_png()
                st.success('Image Converted to PNG!')

            elif option == 'H5':
                image_converter.convert_to_h5()
                st.success('Image Converted to H5!')

            elif option == 'HDF5':
                image_converter.convert_to_hdf5()
                st.success('Image Converted to HDF5!')
            
            elif option == 'None':
                pass
    
    # DicomExTab: Here is the entry point for dicom image explorer
    with DicomExTab:
        DcmAnonTab, DcmViewTab, = st.tabs(["Dicom Image Anonymization", "Dicom Viewer",])
        # DcmAnonTab: Here is the entry point for dicom image annonymization
        with DcmAnonTab:
            dicom_file = st.file_uploader("Upload a DICOM file", key="dicom_annon")
            if dicom_file is not None: 
                # Anonymize DICOM file
                anonymized_dicom_dataset = anonymize_dicom_file(dicom_file)
                desired_file_name = st.text_input("Enter the desired file name for the anonymized DICOM file, press enter to save: ")
                if st.button("Save anonymized dicom file"):
                    # Add the .dcm extension if not provided
                    if desired_file_name is not None:
                        if not desired_file_name.endswith('.dcm'):
                            desired_file_name += '.dcm'
                            # Save the anonymized DICOM file
                            anonymized_dicom_dataset.save_as(f'../data/{desired_file_name}')
                            st.success('Anonymized Dicom file Saved!')
            # DcmViewTab: Here is the entry point for dicom image viewer
        with DcmViewTab:
            dicom_file = st.file_uploader("Upload a DICOM file", key="dicom_viewer")
            if dicom_file is not None:
                dicom_viewer(dicom_file)
    
    # AnonGenTab: Here is the entry point for report anonymization and conversion
    with AnonGenTab:
        st.write('wait a minute')
    
    # OCRTab: Here is the entry point Pdf and Scanned report conversion
    with OCRTab:
        PDF2TextTab, SR2TTab, = st.tabs(["Convert Pdf Reports to Text Files", "Convert Scanned Reports to Text Files",])
        # pdf file to text file
        with PDF2TextTab:
            # st.write("Upload Pdf Report")        
            file = st.file_uploader("Select PDF file", key="PDF2TextTab_file")
            
            if file:
                path = f'../data/{file.name}'
                doc = pdf_2_text(path)                
                texts = chunk_text(doc)
                all_sum_texts = []
                for text in texts:
                    #sum_text = summerizer(text)
                    all_sum_texts.append(text)
                st.text(textwrap.fill(' '.join(all_sum_texts), 150))
                # Save the text to a .txt file
                filename = st.text_input("Enter desired filename for the text file: ", key="filename")
                if filename:
                    with open(f"../data/{filename}.txt", "w") as f:
                        f.write(' '.join(all_sum_texts))
                    st.success(f"Text saved to {filename}.txt")

                
        # Scanned document to text file
        with SR2TTab:
            file = st.file_uploader("Select PDF or Image file", key="SR2TTab_file")
            if file:
                path = f'../data/{file.name}'
                json_output = ocrpdf(path)   
                # texts = chunk_text(json_output)
                # all_sum_texts = []
                # for text in texts:
                #     #sum_text = summerizer(text)
                #     all_sum_texts.append(text)
                # st.text(textwrap.fill(' '.join(all_sum_texts), 150))
                st.text(json_output)
                # Save json_output as a json file
                json_filename = st.text_input("Enter desired filename for the json file: ", key="json_filename")
                if json_filename:
                    with open(f"../data/{json_filename}.json", "w") as f:
                        f.write(json.dumps(json_output))                       
                    st.success(f"Json saved to {json_filename}.json")
                
    # PapersTab: Here is the entry point for paper search
    with PapersTab:
        st.write('Use Keywords to Search for the Latest Research Papers Here.')
        #arxiv pdfs
        topic = st.text_input("Enter the keywords for the topic: ", key="PapersTab_topic")
            
        if topic:
            df = search_arxiv(topic)
            st.dataframe(df, use_container_width=True)
            url_and_name = st.text_input('Enter url and name of desired paper to download',
            help="Copy url from the table above and entire a desired file name, separate the url and name using a comma.",key="topic_url")

            if url_and_name:
                url = url_and_name.split(',')[0]
                filename = url_and_name.split(',')[1]
                text = arxiv_2_file(url, filename)
                #text = summerizer(text)
                st.success(text)

    # ImgAnnotationTab: Here is the entry point for image annotation
    with ImgAnnotationTab:
        clsTab, segTab = st.tabs(["CLS Annotation", "Seg Annotation"])
        # segmentation annotation
        with segTab:
            path = st.text_input('Enter the path to image folder',key="segTab_path")
            if path:
                run_seg(f"../data/{path}")
        # classification annotation
        with clsTab:
            custom_labels = ["", "lesion", "positive", "negative", "tumor", None]
            path = st.text_input('Enter the path to image folder', key="clsTab_path")
            if path:
                select_label, report = run_cls(f"../data/{path}", custom_labels)
                dataframe_annotation(f'../data/{path}/*.jpeg', custom_labels, select_label, report)



def main():
    #st.markdown("<h2 style='text-align: center; color: blue;'>Empowering Healthcare, One Byte at a Time!</h2>", unsafe_allow_html=True)
    # st.image('utils/aidgenie.png', use_column_width=True)


    with st.sidebar:
        choice = option_menu("Main Menu", ["About", "Try out", "Features!"], 
            icons=['house', 'fire', 'minecart-loaded'], menu_icon="cast", default_index=0,
        styles={
        "container": {"padding": "0!important", "background-color": "#262730"},
        "icon": {"color": "white", "font-size": "25px"}, 
        "nav-link": {"font-size": "25px", "text-align": "left", "margin":"0px", "--hover-color": "#3739b5"},
        "nav-link-selected": {"background-color": "#1f8ff6"},})

    if choice == "About":
        st.image('../utils/aidgenie.png', use_column_width=True)
        about()
        mission()
        vision()
        contact()

    elif choice == "Try out":
        colored_header(
        label="AID GENIE: Empowering HealthCare, One Byte at a Time! ",
        description="Use the tabs below to tryout our dedicated tools",
        color_name="violet-70",)
        try_out()
        
    elif choice == "Features!":
        st.image('../utils/aidgenie.png', use_column_width=True)
        features()

if __name__ == "__main__":
    main()
