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
            query=query,
            max_results=300,
            sort_by=arxiv.SortCriterion.SubmittedDate,
            sort_order=arxiv.SortOrder.Descending,
        )
    else:
        search = arxiv.Search(
            query=query,
            max_results=300,
            sort_by=arxiv.SortCriterion.Relevance,  # .SubmittedDate,
            sort_order=arxiv.SortOrder.Descending,
        )

    all_data = []
    for result in search.results():
        temp = ["", "", "", "", ""]
        temp[0] = result.title
        temp[1] = result.published
        temp[2] = result.entry_id
        temp[3] = result.summary
        temp[4] = result.pdf_url
        all_data.append(temp)

    column_names = ["Title", "Date", "Id", "Summary", "URL"]
    df = pd.DataFrame(all_data, columns=column_names)

    return dataframe_explorer(df, case=False)


def arxiv_2_file(url, filename):
    """
    Downloads a PDF from a given URL and saves it to a file.

    Parameters:
    url (str): The URL of the PDF.
    filename (str): The name of the file to save the PDF as.

    Returns:
    res (str): A message indicating whether the download was successful.
    """
    filename = filename + ".pdf"
    response = requests.get(url, stream=True)
    folder_path = "../data/"
    file_path = os.path.join(folder_path, filename)

    with open(file_path, "wb") as f:
        for chunk in response.iter_content(chunk_size=1024):
            if chunk:  # filter out keep-alive new chunks
                f.write(chunk)

    return (
        "PDF file downloaded successfully."
        if os.path.exists(file_path)
        else "Failed to download the PDF file."
    )
