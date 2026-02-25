import sqlite3
import pandas as pd
from pathlib import Path

#path of files
BASE_DIR=Path(__file__).resolve().parent.parent
CSV_PATH = BASE_DIR / "dataset" / "food_data"/"Indian_Food_Nutrition_Processed.csv"
DB_PATH = BASE_DIR / "dataset" / "food_data"/"food_db.sqlite"

df=pd.read_csv(CSV_PATH)
df.columns = (
    df.columns
    .str.strip()
    .str.lower()
    .str.replace(" ", "_")
)

REQUIRED_COL=[
    "dish_name",
    "calories_kcal",
    "carbohydrates_g",
    "protein_g",
    "fats_g",
    "free_sugar_g",
    "fibre_g"
]

df = df[REQUIRED_COL]
