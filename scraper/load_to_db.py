import sqlite3
import json

SCHOOL_JSON_COLUMN_IDX = 2
CLASS_NAME_TO_NUMERIC = {
    "א": 1,
    "ב": 2,
    "ג": 3,
    "ד": 4,
    "ה": 5,
    "ו": 6,
    "ז": 7,
    "ח": 8,
    "ט": 9,
    "י": 10,
    "יא": 11,
    "יב": 12
}
SCHOOL_JSON_PATH = "../data/schools.json"
SCHOOL_DB_PATH = "../data/schools.db"
SCHOOL_DB_SCHMEA = """
CREATE TABLE IF NOT EXISTS school (
    "id" INTEGER PRIMARY KEY,
    "name" VARCHAR(100),
    "city" VARCHAR(30),
    "supervision" VARCHAR(20),
    "level" VARCHAR(20),
    "sector" VARCHAR(10),
    "is_approved" INTEGER
);
CREATE TABLE IF NOT EXISTS school_payment (
    "id" INTEGER PRIMARY KEY AUTOINCREMENT,
    "school_id" INTEGER,
    "class" INTEGER,
    "clause" VARCHAR(100),
    "type" VARCHAR(100),
    "price" REAL
);
"""

conn = sqlite3.connect(SCHOOL_DB_PATH)


def create_db():
    conn.executescript(SCHOOL_DB_SCHMEA)
    conn.commit()


def get_all_schools():
    with open(SCHOOL_JSON_PATH) as school_json_file:
        return json.load(school_json_file)


def insert_school(school_dict):
    school_row = (int(school_dict["id"]),
                  school_dict["name"], school_dict["city"],
                  school_dict["supervision"], school_dict["level"],
                  school_dict["sector"], int(school_dict["is_approved"]))
    conn.execute(
        'INSERT INTO school(id, name, city, supervision, level, sector, is_approved) VALUES(?, ?, ?, ?, ?, ?, ?);', school_row)


def insert_school_payments(school_dict):
    payments = school_dict["payments"]
    school_id = int(school_dict["id"])
    payment_row = ()
    for payment in payments:
        clause_name, clause_payments = payment.popitem()
        for clause_payment in clause_payments:
            payment_row = (school_id, CLASS_NAME_TO_NUMERIC[
                           clause_payment["class"]], clause_name, clause_payment["type"], float(clause_payment["price"]))
            conn.execute(
                'INSERT INTO school_payment(school_id, class, clause, type, price) VALUES (?, ?, ?, ?, ?)', payment_row)


def main():
    create_db()
    all_schools = get_all_schools()
    for school in all_schools:
        insert_school(school)
        insert_school_payments(school)
    conn.commit()

if __name__ == '__main__':
    main()
