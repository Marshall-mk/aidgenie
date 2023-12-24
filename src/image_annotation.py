import os
import numpy as np
import pandas as pd
from glob import glob
from PIL import Image
import streamlit as st
from streamlit_img_label import st_img_label
from streamlit_drawable_canvas import st_canvas
from streamlit_extras.dataframe_explorer import dataframe_explorer
from streamlit_img_label.manage import ImageManager, ImageDirManager


# segmentation section
def run_seg(img_dir):
    """
    Runs segmentation on images in the given directory.
    :param img_dir: directory containing images to segment
    """
    # Initialize variables
    st.set_option("deprecation.showfileUploaderEncoding", False)
    try:
        idm = ImageDirManager(img_dir)
    except FileNotFoundError:
        st.error("The specified image directory does not exist. If the error persists, please refresh the page.")

    if "files" not in st.session_state:
        st.session_state["files"] = idm.get_all_files()
        st.session_state["annotation_files"] = idm.get_exist_annotation_files()
        st.session_state["image_index"] = 0
    else:
        idm.set_all_files(st.session_state["files"])
        idm.set_annotation_files(st.session_state["annotation_files"])

    def refresh():
        st.session_state["files"] = idm.get_all_files()
        st.session_state["annotation_files"] = idm.get_exist_annotation_files()
        st.session_state["image_index"] = 0

    def next_image():
        image_index = st.session_state["image_index"]
        if image_index < len(st.session_state["files"]) - 1:
            st.session_state["image_index"] += 1
        else:
            st.warning("This is the last image.")

    def previous_image():
        image_index = st.session_state["image_index"]
        if image_index > 0:
            st.session_state["image_index"] -= 1
        else:
            st.warning("This is the first image.")

    def next_annotate_file():
        image_index = st.session_state["image_index"]
        next_image_index = idm.get_next_annotation_image(image_index)
        if next_image_index:
            st.session_state["image_index"] = idm.get_next_annotation_image(image_index)
        else:
            st.warning("All images are annotated.")
            next_image()

    def go_to_image():
        file_index = st.session_state["files"].index(st.session_state["file"])
        st.session_state["image_index"] = file_index

    # Sidebar: show status
    column_1, column_3 = st.columns(2)
    n_files = len(st.session_state["files"])
    n_annotate_files = len(st.session_state["annotation_files"])
    st.sidebar.write("Segmentation Annotation info:")
    st.sidebar.write("Total files:", n_files)
    st.sidebar.write("Total annotate files:", n_annotate_files)
    st.sidebar.write("Remaining files:", n_files - n_annotate_files)

    column_3.selectbox(
        "Files",
        st.session_state["files"],
        index=st.session_state["image_index"],
        on_change=go_to_image,
        key="file",
    )
    col1, col2 = column_3.columns(2)
    with col1:
        st.button(label="Previous image", on_click=previous_image, key="seg_prev_image")
        st.button(label="Refresh", on_click=refresh, key="seg_refresh")
    with col2:
        st.button(label="Next image", on_click=next_image, key="seg_next_image")
        st.button(
            label="Next need annotate",
            on_click=next_annotate_file,
            key="seg_next_ann_image",
        )

    # Specify canvas parameters in application
    drawing_mode = column_3.selectbox(
        "Drawing tool:", ("point", "freedraw", "line", "rect", "circle", "transform")
    )
    stroke_width = column_3.slider("Stroke width: ", 1, 25, 3)
    if drawing_mode == "point":
        point_display_radius = column_3.slider("Point display radius: ", 1, 25, 3)

    stroke_color = column_3.color_picker("Stroke color hex: ", "#eee")
    bg_color = column_3.color_picker("Background color hex: ")
    realtime_update = column_3.checkbox("Update in realtime", True)
    img_file_name = idm.get_image(st.session_state["image_index"])
    img_path = os.path.join(img_dir, img_file_name)
    im = ImageManager(img_path)
    image = im.get_img()
    # Get the size of the image
    img_width, img_height = image.size
    file_name, file_extension = os.path.splitext(img_file_name)
    with column_1:
        if image is not None:
            # Create a canvas component
            canvas_result = st_canvas(
                fill_color="rgba(255, 165, 0, 0.3)",  # Fixed fill color with some opacity
                stroke_width=stroke_width,
                stroke_color=stroke_color,
                background_color=bg_color,
                background_image=image or None,
                update_streamlit=realtime_update,
                height=img_height,
                width=img_width,
                drawing_mode=drawing_mode,
                point_display_radius=point_display_radius
                if drawing_mode == "point"
                else 0,
                key=f"canvas_{st.session_state['image_index']}",
            )

            # Do something interesting with the image data and paths
            if canvas_result.image_data is not None:
                st.image(
                    canvas_result.image_data
                )  # width=img_width, use_column_width=True
                # Create a save button
                if st.button("Save Mask", key="seg_mask"):
                    # Save the result as the original name + mask
                    result = Image.fromarray((canvas_result.image_data))

                    result.save(os.path.join("../data", file_name + "_mask.png"))

                    st.success("Result saved as " + file_name + "_mask.png")
                    st.session_state["annotation_files"].append(file_name + "_mask.png")
    dataframe_segmentation(img_dir, file_name)  #


def dataframe_segmentation(path, img_file_name):
    """
    Function to create a dataframe with image and mask file names.
    Args:
        path (str): Directory where the images are stored.
        img_file_name (str): Name of the image file.
    """
    if "result_df_seg" not in st.session_state:
        st.session_state["result_df_seg"] = pd.DataFrame.from_dict(
            {
                "image": st.session_state["files"],
                "mask": [None] * len(st.session_state["files"]),
            }
        ).copy()
    st.session_state["result_df_seg"].loc[st.session_state["image_index"], "mask"] = (
        img_file_name + "_mask.png"
    )
    filtered_df = dataframe_explorer(st.session_state["result_df_seg"], case=False)
    st.dataframe(filtered_df, use_container_width=True)
    file_name = st.text_input(
        "Enter filename for the dataframe",
        help="Write out the desired file name to save the dataframe.",
        key="seg_df",
    )
    if st.button("Save frame", key="seg_frame"):
        st.session_state["result_df_seg"].to_csv(
            f"../data/{file_name}.csv", index=False
        )
        st.success("Annotations saved successfully!")


# classification section
def run_cls(img_dir, labels):
    """
    Function to run the image classification and annotation process.
    Args:
        img_dir (str): Directory where the images are stored.
        labels (list): List of labels for the classification.
    Returns:
        select_label (str): Selected label for the current image.
        report (str): Report text input by the user.
    """
    # Initialize variables
    select_label = None
    report = None
    st.set_option("deprecation.showfileUploaderEncoding", False)
    idm = ImageDirManager(img_dir)

    if "files" not in st.session_state:
        st.session_state["files"] = idm.get_all_files()
        st.session_state["annotation_files"] = idm.get_exist_annotation_files()
        st.session_state["image_index"] = 0
    else:
        idm.set_all_files(st.session_state["files"])
        idm.set_annotation_files(st.session_state["annotation_files"])

    def refresh():
        st.session_state["files"] = idm.get_all_files()
        st.session_state["annotation_files"] = idm.get_exist_annotation_files()
        st.session_state["image_index"] = 0

    def next_image():
        image_index = st.session_state["image_index"]
        if image_index < len(st.session_state["files"]) - 1:
            st.session_state["image_index"] += 1
        else:
            st.warning("This is the last image.")

    def previous_image():
        image_index = st.session_state["image_index"]
        if image_index > 0:
            st.session_state["image_index"] -= 1
        else:
            st.warning("This is the first image.")

    def next_annotate_file():
        image_index = st.session_state["image_index"]
        next_image_index = idm.get_next_annotation_image(image_index)
        if next_image_index:
            st.session_state["image_index"] = idm.get_next_annotation_image(image_index)
        else:
            st.warning("All images are annotated.")
            next_image()

    def go_to_image():
        file_index = st.session_state["files"].index(st.session_state["file"])
        st.session_state["image_index"] = file_index

    # Sidebar: show status
    column_1, column_3 = st.columns(2)
    n_files = len(st.session_state["files"])
    n_annotate_files = len(st.session_state["annotation_files"])
    st.sidebar.write("Classification Annotation info:")
    st.sidebar.write("Total files:", n_files)
    st.sidebar.write("Total annotate files:", n_annotate_files)
    st.sidebar.write("Remaining files:", n_files - n_annotate_files)

    column_3.selectbox(
        "Files",
        st.session_state["files"],
        index=st.session_state["image_index"],
        on_change=go_to_image,
        key="file_box",
    )
    col1, col2 = column_3.columns(2)
    with col1:
        st.button(label="Previous image", on_click=previous_image, key="cls_prev_image")
        st.button(label="Refresh", on_click=refresh, key="cls_refresh")
    with col2:
        st.button(label="Next image", on_click=next_image, key="cls_next_image")
        st.button(
            label="Next need annotate",
            on_click=next_annotate_file,
            key="cls_next_ann_image",
        )

    # Main content: annotate images
    img_file_name = idm.get_image(st.session_state["image_index"])
    img_path = os.path.join(img_dir, img_file_name)
    try:
        im = ImageManager(img_path)
        img = im.get_img()
        resized_img = im.resizing_img()
        resized_rects = im.get_resized_rects()
        with column_1:
            rects = st_img_label(resized_img, box_color="red", rects=resized_rects)
    except FileNotFoundError:
        st.error("The specified image directory does not exist. If the error persists, please refresh the page.")

    def annotate():
        im.save_annotation()
        image_annotate_file_name = img_file_name.split(".")[0] + ".xml"
        if image_annotate_file_name not in st.session_state["annotation_files"]:
            st.session_state["annotation_files"].append(image_annotate_file_name)
        next_annotate_file()
    try:
        if rects:
            st.button(label="Save", on_click=annotate, key="cls_annon")
            preview_imgs = im.init_annotation(rects)

            for i, prev_img in enumerate(preview_imgs):
                prev_img[0].thumbnail((200, 200))
                col1, col2 = st.columns(2)
                with col1:
                    col1.image(prev_img[0])
                with col2:
                    default_index = 0
                    if prev_img[1]:
                        default_index = labels.index(prev_img[1])

                    select_label = col2.selectbox(
                        "Label", labels, key=f"label_{i}", index=default_index
                    )

                    im.set_annotation(i, select_label)
            report = col2.text_input("write report")
    except UnboundLocalError:
        st.error("The specified image directory does not exist. If the error persists, please refresh the page.")
    return select_label, report


def dataframe_annotation(path, custom_labels, select_label, report):
    """
    Function to annotate the dataframe with the selected label and report.
    Args:
        path (str): Path to the dataframe.
        custom_labels (list): List of custom labels for the classification.
        select_label (str): Selected label for the current image.
        report (str): Report text input by the user.
    """
    if "result_df_cls" not in st.session_state:
        st.session_state["result_df_cls"] = pd.DataFrame.from_dict(
            {
                "image": st.session_state["files"],
                "label_idx": [0] * len(st.session_state["files"]),
                "Report": None,
            }
        ).copy()
    st.session_state["result_df_cls"].loc[
        st.session_state["image_index"], "label_idx"
    ] = custom_labels.index(select_label)
    st.session_state["result_df_cls"]["Label"] = st.session_state["result_df_cls"][
        "label_idx"
    ].apply(lambda x: custom_labels[x])
    st.session_state["result_df_cls"]["Report"].loc[
        st.session_state["image_index"]
    ] = report
    filtered_df = dataframe_explorer(st.session_state["result_df_cls"], case=False)
    st.dataframe(filtered_df, use_container_width=True)
    file_name = st.text_input(
        "Enter filename for the dataframe",
        help="Write out the desired file name to save the dataframe.",
        key="cls_df",
    )
    if st.button("Save frame", key="cls_frame"):
        st.session_state["result_df_cls"].to_csv(
            f"../data/{file_name}.csv", index=False
        )
        st.success("Annotations saved successfully!")
