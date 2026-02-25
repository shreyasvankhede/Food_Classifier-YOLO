import streamlit as st
from PIL import Image
from ultralytics import YOLO
import numpy as np
import cv2 as cv

st.title("Food detection")

model = YOLO("best.pt")
st.success("Model loaded")

mode = st.radio(
    "Choose input method:",
    ["Upload Image", "Use Camera"]
)

image_np = None

if mode == "Upload Image":
    uploaded_file = st.file_uploader(
        "Upload an image", type=["jpg", "jpeg", "png"]
    )
    if uploaded_file is not None:
        image = Image.open(uploaded_file).convert("RGB")
        image_np = np.array(image)

elif mode == "Use Camera": 
    camera_image = st.camera_input("Take a picture")
    if camera_image is not None:
        image = Image.open(camera_image).convert("RGB")
        image_np = np.array(image)

if image_np is not None:
    st.subheader("Input Image")
    st.image(image_np, use_container_width=True)

    with st.spinner("Running YOLO..."):
        results = model.predict(
            image,
            imgsz=640,
            conf=0.5,
            save=False
        )

    st.write("Detections:", len(results[0].boxes))

    annotated_img = results[0].plot()
    annotated_img=cv.cvtColor(annotated_img,cv.COLOR_BGR2RGB)
    st.subheader("Detection Result")
    st.image(annotated_img, use_container_width=True)

