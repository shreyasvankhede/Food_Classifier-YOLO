import sqlite3
class UserDB:
    def __init__(self,username):
        self.username=username
        self.conn=sqlite3.connect(f"data/Users/{self.username}.sqlite")
        self.cursor=self.conn.cursor()

    def create_db(self):
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS meals(
               item_id INTEGER PRIMARY KEY AUTOINCREMENT,
               meal_type INTEGER,
               meal_time DATETIME DEFAULT CURRENT_TIMESTAMP,
               dish_name TEXT,
               quantity_g REAL
               )
               ;""")
        self.cursor.execute("""
CREATE TABLE IF NOT EXISTS user_profile (
    Name TEXT PRIMARY KEY,
    age INTEGER,
    gender TEXT,
    weight REAL,
    height REAL,
    activity_level TEXT
);""")

        self.conn.commit()
        self.conn.close()
        


"""

food_ai_project/
│
├── app.py                     ← Login / Landing page
├── auth_manager.py
├── user_logic.py
│
├── pages/
│   ├── 1_Food_Detection.py
│   ├── 2_Daily_Report.py
│   ├── 3_Meal_History.py
│
├── data/
│   ├── foods.db
│   ├── users.db
│
└── model/
    └── auth.sqlite

"""