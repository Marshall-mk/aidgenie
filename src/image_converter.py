import os
import pydicom
import h5py
from PIL import Image
import numpy as np
import streamlit as st
import warnings

warnings.filterwarnings("ignore")


class ImageConverter:
    """
    A class that contains methods for converting image datasets from one format to another.
    """

    def __init__(self, file_path: str):
        """
        Initializes the class with the file path of the image dataset.
        """
        self.file_path = f"../data/{file_path}"

    def convert_to_jpg(self) -> None:
        """
        Converts the image dataset to jpg format.
        """
        file_name = self.file_path.split("/")[-1].split(".")[0]
        if self.file_path.endswith(".dcm") or self.file_path.endswith(".DCM"):
            dicom_file = pydicom.dcmread(self.file_path)
            dicom_dataset = dicom_file.pixel_array
            # Check if DICOM file is a 'volume' (3D) or a single slice (2D)
            if len(dicom_dataset.shape) > 2:
                # If 3D volume, save all slices as individual jpeg files
                for i in range(dicom_dataset.shape[0]):
                    img = Image.fromarray(dicom_dataset[i])
                    img.save(f"../data/{file_name}_slice_num{i}.jpg")
            else:
                # If 2D slice, just save the image
                img = Image.fromarray(dicom_dataset)
                img.save(f"../data/{file_name}.jpg")

        elif self.file_path.endswith(".png"):
            # Convert png to jpg
            img = Image.open(self.file_path)
            img = img.convert("RGB")
            img.save(f"../data/{file_name}.jpg")
        elif self.file_path.endswith(".h5") or self.file_path.endswith(".hdf5"):
            # Convert h5/hdf5 to jpg
            try:
                with h5py.File(self.file_path, "r") as f:
                    img = f["image"][:]
                img = Image.fromarray(img)
                file_name = self.file_path.split("/")[-1].split(".")[0]
                img.save(f"../data/{file_name}.jpg")
            except Exception:
                st.write("Invalid Object Used")

    def convert_to_png(self) -> None:
        """
        Converts the image dataset to png format.
        """
        file_name = self.file_path.split("/")[-1].split(".")[0]
        if self.file_path.endswith(".dcm") or self.file_path.endswith(".DCM"):
            dicom_file = pydicom.dcmread(self.file_path)
            dicom_dataset = dicom_file.pixel_array
            # Check if DICOM file is a 'volume' (3D) or a single slice (2D)
            if len(dicom_dataset.shape) > 2:
                # If 3D volume, save all slices as individual jpeg files
                for i in range(dicom_dataset.shape[0]):
                    img = Image.fromarray(dicom_dataset[i])
                    img.save(f"../data/{file_name}_slice_num{i}.png")

            else:
                # If 2D slice, just save the image
                img = Image.fromarray(dicom_dataset)
                img.save(f"../data/{file_name}.png")

        elif self.file_path.endswith(".jpg"):
            # Convert jpg to png
            img = Image.open(self.file_path)
            img.save(f"../data/{file_name}.png")
        elif self.file_path.endswith(".h5") or self.file_path.endswith(".hdf5"):
            # Convert h5/hdf5 to png
            try:
                with h5py.File(self.file_path, "r") as f:
                    img = f["image"][:]
                img = Image.fromarray(img)
                # img.save(f"../data/{os.path.splitext(self.file_path)[0]}.png")
                file_name = self.file_path.split("/")[-1].split(".")[0]
                img.save(f"../data/{file_name}.png")
            except Exception:
                st.write("Invalid Object Used")

    def convert_to_h5(
        self
    ) -> None:  # sourcery skip: class-extract-method, extract-method
        """
        Converts the image dataset to h5 format.
        """
        file_name = self.file_path.split("/")[-1].split(".")[0]
        if self.file_path.endswith(".dcm") or self.file_path.endswith(".DCM"):
            # Convert dicom to h5
            ds = pydicom.dcmread(self.file_path)
            img = ds.pixel_array
            if len(img.shape) > 2:
                # If 3D volume, save all slices as individual hdf5 files
                for i in range(img.shape[0]):
                    with h5py.File(f"../data/{file_name}_slice_num{i}.h5", "w") as f:
                        f.create_dataset("image", data=img[i])
            else:
                # If 2D slice, just save the image
                with h5py.File(f"../data/{file_name}.h5", "w") as f:
                    f.create_dataset("image", data=img)

        elif self.file_path.endswith(".jpg") or self.file_path.endswith(".png"):
            filepath = self.file_path
            fin = open(filepath, "rb")
            binary_data = fin.read()
            f = h5py.File(f"../data/{file_name}.h5", "w")
            dt = h5py.special_dtype(vlen=np.dtype("uint8"))
            dset = f.create_dataset("binary_data", (100,), dtype=dt)
            dset[0] = np.fromstring(binary_data, dtype="uint8")

    def convert_to_hdf5(self) -> None:  # sourcery skip: extract-method
        """
        Converts the image dataset to h5 format.
        """
        file_name = self.file_path.split("/")[-1].split(".")[0]
        if self.file_path.endswith(".dcm") or self.file_path.endswith(".DCM"):
            # Convert dicom to h5
            ds = pydicom.dcmread(self.file_path)
            img = ds.pixel_array
            # Check if DICOM file is a 'volume' (3D) or a single slice (2D)
            if len(img.shape) > 2:
                # If 3D volume, save all slices as individual hdf5 files
                for i in range(img.shape[0]):
                    with h5py.File(f"../data/{file_name}_slice_num{i}.hdf5", "w") as f:
                        f.create_dataset("image", data=img[i])
            else:
                # If 2D slice, just save the image
                with h5py.File(f"../data/{file_name}.hdf5", "w") as f:
                    f.create_dataset("image", data=img)

        elif self.file_path.endswith(".jpg") or self.file_path.endswith(".png"):
            filepath = self.file_path
            fin = open(filepath, "rb")
            binary_data = fin.read()
            f = h5py.File(f"../data/{file_name}.hdf5", "w")
            dt = h5py.special_dtype(vlen=np.dtype("uint8"))
            dset = f.create_dataset("binary_data", (100,), dtype=dt)
            dset[0] = np.fromstring(binary_data, dtype="uint8")

    # # For full directory

    """Returns a resized num_px * num_px matrix by load img from input dir
    """

    def preprocess(self, image_path, num_px):
        print("Preprocessing Image: ", image_path)
        image = Image.open(image_path)
        print("Image Size: ", image.size)
        resized_image = image.resize((num_px, num_px))
        print("Image Size: ", resized_image.size)
        return np.array(resized_image)

    """Converts a directory full of different shaped images to a standard h5 file of parameterized dimention
    """

    def convert_dir(self, input_dir, output_file_name, dimention):
        arr = os.listdir(input_dir)
        result_arr = np.empty([len(arr), dimention, dimention, 3], dtype="int16")

        for i in range(len(arr)):
            f_path = f"{input_dir}/{arr[i]}"
            im_array = self.preprocess(f_path, dimention)
            result_arr[i] = im_array
        # convert to h5 file
        h5f = h5py.File(f"{output_file_name}.h5", "w")
        h5f.create_dataset("dataset_1", data=result_arr)


#   def convert_create_file(input_dir, filename, output_file):
#         filepath = input_dir + '/' + filename
#         fin = open(filepath, 'rb')
#         binary_data = fin.read()
#         new_filepath = output_file + '/' + filename[:-4] + '.h5'
#         f = h5py.File(new_filepath)
#         dt = h5py.special_dtype(vlen=np.dtype('uint8'))
#         dset = f.create_dataset('binary_data', (100, ), dtype=dt)
#         dset[0] = np.fromstring(binary_data, dtype='uint8')

#     def get_h5(self):
#         filepath = input_dir + '/' + filename
#         fin = open(filepath, 'rb')
#         binary_data = fin.read()
#         new_filepath = output_file + '/' + filename[:-4] + '.h5'
#         f = h5py.File(new_filepath)
#         dt = h5py.special_dtype(vlen=np.dtype('uint8'))
#         dset = f.create_dataset('binary_data', (100, ), dtype=dt)
#         dset[0] = np.fromstring(binary_data, dtype='uint8')

# def convert_to_h5(self) -> None:
#     """
#     Converts the image dataset to h5 format.
#     """
#     if self.file_path.endswith(".dicom"):
#         # Convert dicom to h5
#         ds = pydicom.dcmread(self.file_path)
#         img = ds.pixel_array
#         with h5py.File(os.path.splitext(self.file_path)[0] + ".h5", "w") as f:
#             f.create_dataset("image", data=img)
#     elif self.file_path.endswith(".jpg") or self.file_path.endswith(".png"):
#         # Convert jpg/png to h5
#         img = Image.open(self.file_path)
#         img = img.convert("L")
#         img = img.transpose(Image.FLIP_TOP_BOTTOM)
#         img = img.rotate(90)
#         img = img.resize((512, 512))
#         img = img.getdata()
#         img = [list(img[i:i+512]) for i in range(0, len(img), 512)]
#         img = [[int(pixel) for pixel in row] for row in img]
#         with h5py.File(os.path.splitext(self.file_path)[0] + ".h5", "w") as f:
#             f.create_dataset("image", data=img)

# def convert_to_hdf5(self) -> None:
#     """
#     Converts the image dataset to hdf5 format.
#     """
#     if self.file_path.endswith(".dicom"):
#         # Convert dicom to hdf5
#         ds = pydicom.dcmread(self.file_path)
#         img = ds.pixel_array
#         with h5py.File(os.path.splitext(self.file_path)[0] + ".hdf5", "w") as f:
#             f.create_dataset("image", data=img)
#     elif self.file_path.endswith(".jpg") or self.file_path.endswith(".png"):
#         # Convert jpg/png to hdf5
#         img = Image.open(self.file_path)
#         img = img.convert("L")
#         img = img.transpose(Image.FLIP_TOP_BOTTOM)
#         img = img.rotate(90)
#         img = img.resize((512, 512))
#         img = img.getdata()
#         print(img)
#         img[0:0+512]
#         img = [list(img[i:i+512]) for i in range(0, len(img), 512)]
#         img = [[int(pixel) for pixel in row] for row in img]
#         with h5py.File(os.path.splitext(self.file_path)[0] + ".hdf5", "w") as f:
#             f.create_dataset("image", data=img)
