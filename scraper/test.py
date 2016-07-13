import json
import asyncio
from core import *
from requests import exceptions
import sqlite3

INSERT_STATEMENT = "INSERT INTO newer_schools(school_id, school_json) VALUES(?, ?)"


def get_all_details():
    with open("schools-without-payments.json") as details_file:
        return json.load(details_file)


async def get_all_schools(excluding_ids, db_conn):
    await school_session.start()
    all_details = [details for details in get_all_details() if int(
        details["id"]) not in excluding_ids]
    school_tasks = [add_school(details, db_conn) for details in all_details]
    await asyncio.wait(school_tasks)
    print("Done.")



async def add_school(details, conn):
    try:
        school_page = await find_school(details)
        payments = await get_school_payments(school_page)
        school = dict(details, payments=payments)
        conn.execute(INSERT_STATEMENT, (int(school["id"]), json.dumps(school)))
        print("Inserted school")
    except exceptions.ConnectionError:
        print("Pff, a connection error, who cares.")

if __name__ == '__main__':
    db_conn = sqlite3.connect("schools.db", isolation_level=None)
    excluded_ids_rows = db_conn.execute(
        "SELECT school_id FROM newer_schools;").fetchall()
    excluded_ids = {row[0] for row in excluded_ids_rows}
    loop = asyncio.get_event_loop()
    loop.run_until_complete(get_all_schools(excluded_ids, db_conn))
