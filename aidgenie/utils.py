import textwrap
import streamlit as st
from streamlit_extras.let_it_rain import rain

def chunk_text(text):
    return textwrap.wrap(text, 4000)

def features():
    st.subheader(":blue[Store], :blue[Convert], and :blue[Generate] paired :green[Scans] & :red[Reports] in multiple formats!")
    st.subheader(":blue[Anonymize] bulk :green[Reports] in just a few :green[Cicks!]")
    st.subheader("Generate :blue[lables/tags] from large text :red[Reports!]")
    st.subheader(":green[Annotate] Image  :blue[Datasets!]:lungs:")

def about():
    rain(
    emoji="⚕️",
    font_size=54,
    falling_speed=10,
    animation_length="infinite",)
    st.title("Problem Statement")
    st.write("""The scarcity of reliable medical data from developing countries, particularly in regions like Nigeria and other parts of Africa, 
    poses a significant challenge and contributes to bias in medical artificial intelligence (AI) systems. This challenge primarily stems from inadequate 
    data management practices and the difficulty in accessing patient records, hindering organizations that rely on such data. Addressing this problem is 
    crucial to foster unbiased and effective medical AI solutions.""")

def mission():
    st.title("Mission")
    st.write("""Our mission is to alleviate the shortage of medical data from developing countries by developing a robust platform and data 
    warehouse. We aim to empower healthcare professionals, including doctors, radiographers, radiologists, and other medical personnel, with a comprehensive 
    solution for secure and convenient storage, retrieval, and utilization of medical data. Our goal is to enhance data availability and accessibility, 
    while ensuring privacy protection through advanced anonymization techniques.""")

def vision():
    st.title("Vission")
    st.write("""Our vision is to create an inclusive global healthcare landscape where high-quality medical data from developing countries is readily
    accessible and seamlessly integrated into AI-driven healthcare solutions. We envision a future where healthcare professionals 
    can leverage our sophisticated platform to efficiently store, retrieve, and analyze patient data. By providing robust data preprocessing 
    capabilities and advanced redaction functionalities, we aim to facilitate the ethical utilization of medical data, ultimately leading to 
    improved research, accurate diagnoses, and advancements in healthcare outcomes.""")

def contact():
    st.subheader("Contact")
    st.write("""
    [Twitter](https://twitter.com/aid_genie)    [LinkedIn](https://www.linkedin.com/company/aid-genie/)    [Mail](mailto:aidgenie.ng@gmail.com)""")

# @st.cache
# def load_image(img):
#     im = Image.open(img)
#     # Preprocess here    
#     return im🎈⚕️