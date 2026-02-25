import sqlite3
from rapidfuzz import process, fuzz
from PIL import Image
from ultralytics import YOLO
from collections import Counter
from datetime import datetime
import hashlib


# -------------------------
# GLOBAL CONFIG
# -------------------------
DB_PATH = "data/food_db.sqlite"

# Load model ONLY once
MODEL = YOLO("model/best.pt")


DATE = datetime.now().strftime("%Y-%m-%d")


class MealType:
    BREAKFAST = 0
    LUNCH = 1
    DINNER = 2
    SNACKS = 3


# -------------------------
# USER CLASS = CALORIE TRACKER ENGINE
# -------------------------
class User:
    
    def __init__(self, username):
        self.name = username
        self.hash_name=hashlib.sha256(username.encode()).hexdigest()
        self.USER_PATH = f"data/{self.hash_name}.sqlite"

    # -------------------------
    # FOOD LOOKUP
    # -------------------------
    def get_food_info(self, food):
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        cursor.execute("""
            SELECT calories_kcal, carbohydrates_g, protein_g,
                   fats_g, free_sugar_g, fibre_g
            FROM foods_master
            WHERE dish_name = ?
        """, (food,))

        result = cursor.fetchone()
        conn.close()

        return result

    # -------------------------
    # FUZZY SEARCH
    # -------------------------
    def get_all_food_names(self):
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        cursor.execute("SELECT dish_name FROM foods_master")
        foods = [row[0] for row in cursor.fetchall()]

        conn.close()
        return foods

    def suggest_similar_foods(self, query, limit=5):
        foods = self.get_all_food_names()

        matches = process.extract(
            query,
            foods,
            scorer=fuzz.partial_ratio,
            limit=limit
        )

        return [name for name, score, _ in matches]

    # -------------------------
    # CREATE MEAL
    # -------------------------
    def create_meal(self):
        conn = sqlite3.connect(self.USER_PATH)
        cursor = conn.cursor()

        cursor.execute("INSERT INTO meals DEFAULT VALUES")
        meal_id = cursor.lastrowid

        conn.commit()
        conn.close()

        return meal_id

    # -------------------------
    # CALCULATION (PER 100g → quantity)
    # -------------------------
    def calculate_nutrition(self, nutrition, quantity):
        # DB values are per 100g
        return tuple(x * quantity / 100 for x in nutrition)

    # -------------------------
    # ADD FOOD TO MEAL
    # -------------------------
    def add_food_to_meal(self, meal_id, food, quantity=100):
        nutrition = self.get_food_info(food)

        if nutrition is None:
            print("Food not found")
            return

        cal, carb, protein, fats, sugar, fibre = self.calculate_nutrition(nutrition, quantity)

        conn = sqlite3.connect(self.USER_PATH)
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO meal_items
            (meal_id, dish_name, quantity_g,
             calories, carbs, protein, fats, fibre, sugar)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            meal_id,
            food,
            quantity,
            cal,
            carb,
            protein,
            fats,
            fibre,
            sugar
        ))

        conn.commit()
        conn.close()

    # -------------------------
    # CALCULATE SINGLE MEAL TOTAL
    # -------------------------
    def calculate_meal_cals(self, meal_id, date=DATE):
        conn = sqlite3.connect(self.USER_PATH)
        cursor = conn.cursor()

        cursor.execute("""
            SELECT SUM(mi.calories), SUM(mi.carbs), SUM(mi.protein),
                   SUM(mi.fats), SUM(mi.fibre), SUM(mi.sugar)
            FROM meal_items mi
            JOIN meals m ON mi.meal_id = m.meal_id
            WHERE mi.meal_id = ? AND DATE(m.meal_time) = ?
        """, (meal_id, date))

        result = cursor.fetchone()
        conn.close()

        return tuple(x or 0 for x in result)

    # -------------------------
    # DAILY TOTAL
    # -------------------------
    def calculate_daily_macros(self, date=DATE):
        conn = sqlite3.connect(self.USER_PATH)
        cursor = conn.cursor()

        cursor.execute("""
            SELECT SUM(mi.calories), SUM(mi.carbs), SUM(mi.protein),
                   SUM(mi.fats), SUM(mi.fibre), SUM(mi.sugar)
            FROM meal_items mi
            JOIN meals m ON mi.meal_id = m.meal_id
            WHERE DATE(m.meal_time) = ?
        """, (date,))

        result = cursor.fetchone()
        conn.close()

        return tuple(x or 0 for x in result)

    # -------------------------
    # EDIT / DELETE ENTRY
    # -------------------------
    def change_entry(self, item_id, new_quantity=None, delete_entry=False):
        conn = sqlite3.connect(self.USER_PATH)
        cursor = conn.cursor()

        if delete_entry:
            cursor.execute("DELETE FROM meal_items WHERE item_id=?", (item_id,))
            conn.commit()
            conn.close()
            return "Entry deleted"

        cursor.execute("""
            SELECT dish_name, quantity_g
            FROM meal_items
            WHERE item_id = ?
        """, (item_id,))

        row = cursor.fetchone()

        if row is None:
            conn.close()
            return "Item not found"

        dish_name, old_quantity = row

        nutrition = self.get_food_info(dish_name)
        cal, carb, protein, fats, sugar, fibre = self.calculate_nutrition(nutrition, new_quantity)

        cursor.execute("""
            UPDATE meal_items
            SET quantity_g=?, calories=?, carbs=?, protein=?, fats=?, fibre=?, sugar=?
            WHERE item_id=?
        """, (
            new_quantity,
            cal,
            carb,
            protein,
            fats,
            fibre,
            sugar,
            item_id
        ))

        conn.commit()
        conn.close()

        return "Entry updated"
    def get_meal_entries(self,date=DATE):
        conn=sqlite3.connect(self.USER_PATH)
        cursor=conn.cursor()

        cursor.execute("""
            SELECT 
            """)

    # -------------------------
    # YOLO DETECTION (USES GLOBAL MODEL)
    # -------------------------
    def detect_food(self, img):
        if img is None:
            return None

        image = Image.open(img).convert("RGB")

        results = MODEL.predict(
            image,
            imgsz=640,
            conf=0.5,
            save=False
        )

        result = results[0]
        detected_names = [MODEL.names[int(c)] for c in result.boxes.cls]

        class_counts = Counter(detected_names)

        return class_counts, detected_names
       



       
