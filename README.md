# BhojanAI - Indian Food Detection and Calorie Tracking System

A full-stack calorie tracker built for Indian cuisine. It combines a custom-trained YOLOv8 food detection model with a nutrition database and a complete meal logging system including user authentication, fuzzy food search, and historical reporting.

![Python](https://img.shields.io/badge/Python-3.10-blue)
![YOLOv8](https://img.shields.io/badge/YOLOv8-Ultralytics-purple)
![PyTorch](https://img.shields.io/badge/PyTorch-ML%20Backend-orange)
![Streamlit](https://img.shields.io/badge/Streamlit-UI-red)
![SQLite](https://img.shields.io/badge/SQLite-Database-lightgrey)
---
## Screenshots

<img width="1920" height="1080" alt="Screenshot 2026-03-04 195146" src="https://github.com/user-attachments/assets/5334e4cc-9c3c-4a30-8363-74965d948bd3" />

<img width="1920" height="1080" alt="Screenshot 2026-03-04 195224" src="https://github.com/user-attachments/assets/aa79a6da-85cd-47fb-a9b2-cb64fb65128e" />

<img width="1390" height="877" alt="Screenshot 2026-03-04 232559" src="https://github.com/user-attachments/assets/8b8a6b98-426e-450c-8702-393744d4ea8b" />

https://github.com/user-attachments/assets/ca1b4333-c38f-49ec-9b14-bffc8ab2967c

<img width="1464" height="863" alt="Screenshot 2026-03-04 232506" src="https://github.com/user-attachments/assets/b57386b2-29e8-45bc-9df3-ee251fe23ad7" />


<img width="1522" height="1064" alt="Screenshot 2026-03-04 213038" src="https://github.com/user-attachments/assets/3bed56fb-da81-4f3c-b603-1ed8d353d0f3" />


## Background

Most calorie tracking apps don't work well for Indian food. You search for "chole bhature" or "masala dosa" and either get no results or something completely wrong.

For this project, images were sourced from the [Indian Food Classification dataset on Kaggle](https://www.kaggle.com/datasets/theeyeschico/indian-food-classification), manually sorted per food class, and labeled with bounding boxes to train a YOLOv8 model from scratch. Nutrition data (calories, carbs, protein, fats, fibre, sugar) was sourced from the [Anuvaad Indian Diet Data Portal](https://www.anuvaad.org.in/indian-diet-data-portal/) and cleaned before being loaded into SQLite.

---

## Model Performance

| Metric | Score |
|---|---|
| Overall mAP@0.5 | 0.806 |
| Overall mAP@0.5:0.95 | 0.503 |
| Inference Speed | ~12ms per image (CPU) |
| Validation Images | 300 |
| Total Instances | 528 |

### Per-Class Results

| Food Class | mAP@0.5 | Food Class | mAP@0.5 |
|---|---|---|---|
| Burger | 0.995 | Masala Dosa | 0.986 |
| Dal Makhani | 0.988 | Chole Bhature | 0.984 |
| Kadai Paneer | 0.995 | Dhokla | 0.960 |
| Chai | 0.983 | Fried Rice | 0.848 |
| Chapati | 0.778 | Pakode | 0.844 |
| Pav Bhaji | 0.844 | Jalebi | 0.641 |
| Samosa | 0.851 | Pizza | 0.760 |
| Paani Puri | 0.763 | Roll | 0.793 |
| Naan | 0.650 | Momos | 0.485 |
| Kulfi | 0.581 | Idli | 0.386 |

Classes like idli (0.386), momos (0.485), and kulfi (0.581) score lower because they had fewer than 15 training images each. Adding more training data for these classes is the most straightforward way to improve them.

---

## Features

### User Authentication
- Registration and login with SHA-256 password hashing
- Session management using Streamlit session state
- Each user gets their own isolated SQLite database

### User Profile
- Collects age, gender, weight, height, and activity level on signup
- Profile data stored for BMR-based calorie target calculation (planned feature)

### Food Detection
- Camera input captured directly inside the app
- Image passed to the custom YOLOv8 model for inference
- Detected food classes counted and displayed for user confirmation
- User can correct any wrong detections before the food gets logged

### Nutrition Database
- Per-100g nutrition values for each food item (calories, carbs, protein, fats, sugar, fibre)
- Values automatically scaled based on the quantity entered
- Database built from Anuvaad portal data after cleaning and removing inconsistent entries

### Fuzzy Food Search
- Built using RapidFuzz with partial ratio matching
- Works with typos and partial names, so searching "dosa" still returns masala dosa and related items

### Meal Logging
- Meals split into Breakfast, Lunch, Dinner, and Snacks
- Each log entry stores dish name, quantity in grams, all macro values, and timestamp
- Logs are editable after entry using st.data_editor() with live recalculation

### Reports
- Browse past meal history by date
- Daily calorie and macro summary
- Past entries are editable

---

## Dataset and Training

Images came from the [Indian Food Classification dataset on Kaggle](https://www.kaggle.com/datasets/theeyeschico/indian-food-classification). The dataset had images grouped by food class, but required manual separation and cleanup before it was ready for detection training (classification datasets don't come with bounding box labels).

Steps taken to prepare the dataset:

1. Downloaded and sorted images per food class
2. Drew bounding box annotations manually for all 20 categories
3. Split into train, val, and test sets in YOLO label format
4. Trained YOLOv8n on Google Colab using GPU runtime

```
dataset/
├── images/
│   ├── train/
│   ├── val/
│   └── test/
└── labels/
    ├── train/
    ├── val/
    └── test/
```

Training command used:
```bash
yolo detect train data=data.yaml model=yolov8n.pt epochs=50 imgsz=640
```

---

## Tech Stack

| Layer | Technology |
|---|---|
| Object Detection | YOLOv8 (Ultralytics) |
| ML Runtime | PyTorch |
| Image Processing | Pillow, OpenCV |
| Frontend | Streamlit (multi-page) |
| Database | SQLite |
| Fuzzy Search | RapidFuzz |
| Data Handling | Pandas, NumPy |
| Authentication | hashlib (SHA-256) |
| Training | Google Colab (T4 GPU) |

---

## Project Structure

```
bhojanai/
│
├── front.py                  # Landing / login page
├── app.py                    # App entry point
├── Auth.py                   # Authentication logic
├── calorie_counter.py        # Core calorie & macro calculations
├── database.py               # Database connection & queries
├── navbar.py                 # Shared navigation bar component
├── update.py                 # Data update utilities
├── preprocess_data.py        # Food data preprocessing
├── model_train.py            # YOLO model training script
├── requirements.txt          # Python dependencies
│
├── pages/
│   ├── Food_Detection.py     # Food logging (search + camera scan)
│   └── report.py             # Daily reports & macro breakdown
│
├── data/
│   ├── food_db.sqlite        # Food nutrition database
│   └── Users/                # Per-user data storage
│
└── model/
    ├── auth.sqlite            # User authentication database
    └── food_model.pt          # Trained YOLO food detection model
```


---

## Setup

```bash
git clone https://github.com/shreyasvankhede/BhojanAI.git
cd bhojanai
pip install -r requirements.txt
streamlit run app.py
```

**requirements.txt**
```
streamlit
ultralytics
torch
torchvision
opencv-python
Pillow
pandas
numpy
rapidfuzz
```

---

## What's Planned Next

- BMR-based daily calorie targets using the stored user profile
- More training data for idli, momos, and kulfi to bring their mAP up
- Expanding to 50+ food categories
- FastAPI backend to replace Streamlit session logic
- On-device inference with TFLite or ONNX for mobile
- Weekly and monthly nutrition trend charts

---

## Author

**Shreyas Vankhede**

