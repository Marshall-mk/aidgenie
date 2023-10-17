import os
import requests
import arxiv
import pandas as pd
import streamlit as st
from streamlit_extras.dataframe_explorer import dataframe_explorer

def search_arxiv(query):
    """
    This function searches the arXiv database for papers based on the provided query.
    It returns a DataFrame containing the title, date, id, summary, and URL of each paper.

    Parameters:
    query (str): The search query.

    Returns:
    df (DataFrame): DataFrame containing the search results.
    """
    if st.toggle("Sort by Date"):
       search = arxiv.Search(
        query = query,
        max_results = 300,
        sort_by = arxiv.SortCriterion.SubmittedDate,
        sort_order = arxiv.SortOrder.Descending
        )
    else: 
        search = arxiv.Search(
            query = query,
            max_results = 300,
            sort_by = arxiv.SortCriterion.Relevance,#.SubmittedDate,
            sort_order = arxiv.SortOrder.Descending
            )

    all_data = []
    for result in search.results():
        temp = ["","","","",""]
        temp[0] = result.title
        temp[1] = result.published
        temp[2] = result.entry_id
        temp[3] = result.summary
        temp[4] = result.pdf_url
        all_data.append(temp)


    column_names = ['Title','Date','Id','Summary','URL']
    df = pd.DataFrame(all_data, columns=column_names)
    filtered_df = dataframe_explorer(df, case=False)

    # print("Number of papers extracted : ",df.shape[0])
    return filtered_df
def arxiv_2_file(url, filename):
    """
    Downloads a PDF from a given URL and saves it to a file.

    Parameters:
    url (str): The URL of the PDF.
    filename (str): The name of the file to save the PDF as.

    Returns:
    res (str): A message indicating whether the download was successful.
    """
    filename = filename+'.pdf'
    response = requests.get(url, stream=True)
    folder_path = "../data/"
    file_path = os.path.join(folder_path, filename)

    with open(file_path, "wb") as f:
        for chunk in response.iter_content(chunk_size=1024):
            if chunk:  # filter out keep-alive new chunks
                f.write(chunk)

    if os.path.exists(file_path):
        res = "PDF file downloaded successfully."
    else:
        res = "Failed to download the PDF file."

    return res



# def arxiv_2_file(url, filename):
#     """
#     This function downloads a PDF from a given URL and saves it to a file.

#     Parameters:
#     url (str): The URL of the PDF.
#     filename (str): The name of the file to save the PDF as.

#     Returns:
#     res (str): A message indicating whether the download was successful.
#     """
#     url = url
#     filename = filename+'.pdf'
#     response = requests.get(url)
#     # specify the desired folder path
#     folder_path = "../data/"
#     # join the folder path and filename
#     file_path = os.path.join(folder_path, filename)
#     msg = st.toast('Connecting to server...')
#     if response.status_code == 200:
#         msg.toast('Gathering info...')
#         # YOUR_CODE
#         download_size = int(response.headers.get("content-length", 0))
#         downloaded = 0
#         chunk_size = 1024
#         for data in response.iter_content(chunk_size=chunk_size):
#             downloaded += len(data)
#         st.progress(downloaded / download_size)
#         with open(file_path, "wb") as f:
#             f.write(response.content)  
#         if downloaded == download_size:
#             msg.toast('Finished!')
#             res = "PDF file downloaded successfully."
#         else:
#             res = "Failed to download the PDF file."
#         return res

# def arxiv_2_file(url, filename):
#     """
#     This function downloads a PDF from a given URL and saves it to a file.

#     Parameters:
#     url (str): The URL of the PDF.
#     filename (str): The name of the file to save the PDF as.

#     Returns:
#     res (str): A message indicating whether the download was successful.
#     """
#     url = url
#     filename = filename+'.pdf'
#     response = requests.get(url)
#     # specify the desired folder path
#     folder_path = "../data/"
#     # join the folder path and filename
#     file_path = os.path.join(folder_path, filename)
#     if response.status_code == 200:
#         # YOUR_CODE
#         download_size = int(response.headers.get("content-length", 0))
#         downloaded = 0
#         # with open(file_path, "wb") as f:
#         #     f.write(response.content) 
#         with open(file_path, "wb") as f:
#             for chunk in response.iter_content(chunk_size=1024):
#                 if chunk:  # filter out keep-alive new chunks
#                     f.write(chunk)
#                     downloaded += len(chunk) 
#         if downloaded == download_size:
#             res = "PDF file downloaded successfully."
#         else:
#             res = "Failed to download the PDF file."
#         return res