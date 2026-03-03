import sqlite3

DB_PATH = "data/food_db.sqlite"

def update_food_database():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    print("Connected to database.")

    # EXACT mapping from model class → desired DB name
    rename_map = {
        "burger": "vegetable burger",
        "chai": "Hot tea(Garam Chai)",
        "chapati": "Chapati/Roti",
        "chole_bhature": "Bhatura",
        "dal_makhani": "Dal makhani",
        "dhokla": "Khaman (dhokla)",
        "fried_rice": "Chinese fried rice",
        "idli": "Idli",
        "kadai-paneer": "Kadhai Paneer",
        "kulfi": "Kulfi",
        "masala_dosa": "Masala dosa",
        "naan": "Naan",
        "pakode": "Onion pakora/pakoda (Pyaaz ke pakode)",
        "pav_bhaji": "Pav bhaji",
        "pizza": "Pizza",
        "roll": "Cabbage rolls (dry) ((Pattagobhi rolls) (dry))",
        "samosa": "Potato samosa (Aloo ka samosa)"
    }

    for old_name, new_name in rename_map.items():
        cursor.execute("""
            UPDATE foods_master
            SET dish_name = ?
            WHERE dish_name = ?
        """, (new_name, old_name))

    print("Exact renaming complete.")

    # Insert Jalebi if not exists
    cursor.execute("SELECT 1 FROM foods_master WHERE dish_name = 'Jalebi'")
    if not cursor.fetchone():
        cursor.execute("""
            INSERT INTO foods_master
            (dish_name, calories_kcal, carbohydrates_g, protein_g, fats_g,
             free_sugar_g, fibre_g, sodium_mg, calcium_mg, iron_mg,
             vitamin_c_mg, folate_ug)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            "Jalebi",
            300.0,
            62.36,
            4.19,
            4.31,
            42.77,
            1.0,
            146.0,
            131.0,
            0.72,
            1.4,
            0.0
        ))
        print("Inserted Jalebi.")

    # Insert Momos if not exists
    cursor.execute("SELECT 1 FROM foods_master WHERE dish_name = 'Momos (Veg)'")
    if not cursor.fetchone():
        cursor.execute("""
            INSERT INTO foods_master
            (dish_name, calories_kcal, carbohydrates_g, protein_g, fats_g,
             free_sugar_g, fibre_g, sodium_mg, calcium_mg, iron_mg,
             vitamin_c_mg, folate_ug)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            "Momos (Veg)",
            178.0,
            30.0,
            6.0,
            4.0,
            2.0,
            2.0,
            300.0,
            20.0,
            1.5,
            2.0,
            10.0
        ))
        print("Inserted Momos (Veg).")

    conn.commit()
    conn.close()

    print("Database update complete.")


if __name__ == "__main__":
    update_food_database()
    