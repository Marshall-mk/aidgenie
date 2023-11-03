import h5py
import pydicom
import streamlit as st
import matplotlib.pyplot as plt
from pydicom.filereader import dcmread
from pydicom.dataelem import DataElement
from pydicom.filebase import DicomBytesIO
from pydicom.data import get_testdata_file
import cv2

st.set_option("deprecation.showPyplotGlobalUse", False)


def dicom_viewer(dicom_file):
    """
    Function to view and save slices of a DICOM file.

    Parameters:
    - dicom_file: BytesIO object containing the DICOM file data.

    Returns:
    None
    """
    # create columns
    col1, col2 = st.columns(2)
    try:
        if dicom_file is not None:
            # Load DICOM file
            file = DicomBytesIO(dicom_file.getvalue())
            dicom_dataset = pydicom.dcmread(file, force=True)

            # Check if DICOM file is a 'volume' (3D) or a single slice (2D)
            if len(dicom_dataset.pixel_array.shape) > 2:
                # If 3D volume, create a slider to move through slices
                slice_num = st.slider(
                    "Slice Number",
                    min_value=0,
                    max_value=dicom_dataset.pixel_array.shape[0] - 1,
                    value=0,
                )
                img = st.image(
                    dicom_dataset.pixel_array[slice_num],
                    caption="Showing current slice of the dicom image data",
                    clamp=True,
                )

                # Create a button to save the current image slice as a jpeg file
                if col1.button("Save slice as JPEG", key="3D_single"):
                    cv2.imwrite(
                        f'../data/{dicom_file.name.split(".")[0]}_slice_num{slice_num}.jpeg',
                        dicom_dataset.pixel_array[slice_num],
                    )
                    st.success("Slice Saved!")

                # Create a button to save all slices as individual jpeg files
                if col2.button("Save all slices as JPEG", key="3D_all"):
                    for i in range(dicom_dataset.pixel_array.shape[0]):
                        cv2.imwrite(
                            f'../data/{dicom_file.name.split(".")[0]}_slice_num{i}.jpeg',
                            dicom_dataset.pixel_array[i],
                        )
                        st.success("All Slices Saved!")

            else:
                # If 2D slice, just show the image
                img = st.image(
                    dicom_dataset.pixel_array,
                    caption="Showing the only slice of the dicom image data available",
                    clamp=True,
                )

                # Create a button to save the current image slice as a jpeg file
                if st.button("Save slice as JPEG", key="2D_single"):
                    cv2.imwrite(
                        f'../data/{dicom_file.name.split(".")[0]}.jpeg',
                        dicom_dataset.pixel_array,
                    )
                    st.success("Slice Saved!")
    except:
        st.warning("Uploaded file has a problem")


def anonymize_dicom_file(dicom_file):
    """
    Function to anonymize a DICOM file by replacing patient names,
    dates, times, and unique identifiers with anonymous or default values.

    Parameters:
    - dicom_file: BytesIO object containing the DICOM file data.

    Returns:
    - dicom_dataset: Anonymized DICOM dataset.
    """
    # Define callback
    """This function will replace all patient names, dates, 
    times, and unique identifiers in the DICOM file with anonymous or default values. 
    You can modify the callback function to anonymize other DICOM tags as needed. """

    # Read the DICOM file
    dicom_file = DicomBytesIO(dicom_file.getvalue())
    dicom_dataset = pydicom.dcmread(dicom_file, force=True)

    # Check if the DICOM file is a 'volume' (3D) or a single slice (2D)
    try:
        if len(dicom_dataset.pixel_array.shape) > 2:
            st.image(
                dicom_dataset.pixel_array[0],
                caption="dicom image data to be anonymized",
                clamp=True,
            )
        else:
            st.image(
                dicom_dataset.pixel_array,
                caption="dicom image data to be anonymized",
                clamp=True,
            )

        # Print out patient data/info contained in the DICOM image
        st.write("Patient's Name: ", dicom_dataset.PatientName)
        st.write("Patient's ID: ", dicom_dataset.PatientID)
        st.write("Patient's Birth Date: ", dicom_dataset.PatientBirthDate)
        st.write("Patient's Sex: ", dicom_dataset.PatientSex)
        st.write("Study Date: ", dicom_dataset.StudyDate)
        st.write("Modality: ", dicom_dataset.Modality)
        try:
            st.write("Manufacturer: ", dicom_dataset.Manufacturer)
            st.write("Model Name: ", dicom_dataset.ManufacturerModelName)
        except:
            st.write("Manufacturer: None")
            st.write("Model Name: None")
    except:
        st.warning("Uploaded Image has a problem")

    def callback(dataset, data_element):
        """
        Callback function to anonymize DICOM tags.

        Parameters:
        - dataset: DICOM dataset.
        - data_element: DICOM tag.

        Returns:
        None
        """
        if data_element.tag == "(0010,1010)":  # Patient's Age
            data_element.value = "000Y"
        if data_element.tag == "(0010,0040)":  # Patient's Sex
            data_element.value = ""
        if data_element.tag == "(0010,1030)":  # Patient's Weight
            data_element.value = ""
        if data_element.tag == "(0010,1040)":  # Patient's Address
            data_element.value = ""
        if data_element.VR == "PN":
            data_element.value = "Anonymous"
        if data_element.VR == "LO":
            data_element.value = "Anonymous"
        if data_element.VR == "SH":
            data_element.value = "Anonymous"
        if data_element.VR == "DA":
            data_element.value = "19010101"
        if data_element.VR == "TM":
            data_element.value = "000000.00"
        if data_element.VR == "DT":
            data_element.value = "19010101"
        if data_element.VR == "UI":
            data_element.value = "0"

    # Apply the callback function to all elements in the DICOM dataset
    dicom_dataset.walk(callback)

    return dicom_dataset
