import sqlite3
import json
import glob
import re
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
SCHOOL_JSON_PATH_PATTERN = "../data/schools-*.json"
YEAR_PATTERN = re.compile("\d{4}")
SCHOOL_DB_PATH = "../data/schools.db"
SCHOOL_DB_SCHMEA = """
CREATE TABLE IF NOT EXISTS school (
    "id" INTEGER,
    "name" VARCHAR(100),
    "city" VARCHAR(30),
    "supervision" VARCHAR(20),
    "level" VARCHAR(20),
    "sector" VARCHAR(10),
    "is_approved" INTEGER,
    "year" INTEGER,
    PRIMARY KEY (id, year)
);
CREATE TABLE IF NOT EXISTS school_payment (
    "id" INTEGER PRIMARY KEY AUTOINCREMENT,
    "school_id" INTEGER,
    "class" INTEGER,
    "clause" VARCHAR(100),
    "type" VARCHAR(100),
    "price" REAL,
    "year" INTEGER
);
"""

conn = sqlite3.connect(SCHOOL_DB_PATH)


def create_db():
    conn.executescript(SCHOOL_DB_SCHMEA)
    conn.commit()


def _load_json(json_path):
    with open(json_path) as json_file:
        return json.load(json_file)


def get_all_schools():
    # returns a list of tuples, each tuple is
    # (year, school), for multiyear support
    for json_path in glob.iglob(SCHOOL_JSON_PATH_PATTERN):
        print(json_path, YEAR_PATTERN)
        year = YEAR_PATTERN.search(json_path).group()
        schools = _load_json(json_path)
        for school in schools:
            yield school, int(year)


def insert_school(school_dict, year):
    school_row = (int(school_dict["id"]),
                  school_dict["name"], school_dict["city"],
                  school_dict["supervision"], school_dict["level"],
                  school_dict["sector"], int(school_dict["is_approved"]),
                  year)
    conn.execute(
        'INSERT INTO school(id, name, city, supervision, level, sector, is_approved, year) VALUES(?, ?, ?, ?, ?, ?, ?, ?);', school_row)


def insert_school_payments(school_dict, year):
    payments = school_dict["payments"]
    school_id = int(school_dict["id"])
    payment_row = ()
    for payment in payments:
        clause_name, clause_payments = payment.popitem()
        for clause_payment in clause_payments:
            payment_row = (school_id, CLASS_NAME_TO_NUMERIC[clause_payment["class"]],
                           clause_name, clause_payment["type"],
                           float(clause_payment["price"]), year
                           )
            conn.execute(
                'INSERT INTO school_payment(school_id, class, clause, type, price, year) VALUES (?, ?, ?, ?, ?, ?)', payment_row)


def main():
    create_db()
    for school, year in get_all_schools():
        print(year)
        insert_school(school, year)
        insert_school_payments(school, year)
    conn.commit()

if __name__ == '__main__':
    main()
