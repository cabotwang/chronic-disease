import streamlit as st
from PIL import Image
import os
from deta import Deta
from pathlib import Path
import tempfile

deta = Deta(st.secrets["deta_key"])
st.title("File Upload Tutorial")

menu = ["Image", "Dataset", "DocumentFiles", "About"]
choice = st.sidebar.selectbox("Menu", menu)


def load_image(image_file):
    img = Image.open(image_file)
    return img

if choice == "Image":
    st.subheader("Image")
    image_file = st.file_uploader("Upload Images",
                                  type=["png", "jpg", "jpeg"])
    if image_file is not None:
        # TO See details
        file_details = {"filename": image_file.name, "filetype": image_file.type,
                        "filesize": image_file.size}
        with tempfile.NamedTemporaryFile(delete=False) as tmp_file:
            fp = Path(tmp_file.name)
            fp.write_bytes(image_file.getvalue())
        st.image(load_image(image_file), width=250)
        # photos = deta.Drive("photos")
        # photos.put(image_file.name, path=fp)

    show = st.button('显示图片')
    if show:
        photos = deta.Drive("photos")
        list1 = photos.list()
        for value in list1.values():
            res = photos.get(value[0])
            image = Image.open(res)
            st.image(image)
            print(value)
