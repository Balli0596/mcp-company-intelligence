from fastapi import FastAPI, HTTPException
import mysql.connector
import pymysql

from fastapi import HTTPException
from pymysql.cursors import DictCursor
app = FastAPI()
@app.get("/")
def home():
    return {
        "message": "Welcome to AI Company API 🚀",
        "endpoints": {
            "client": "/client/{cid}",
            "director": "/director/{din}"
        }
    }
# 🔹 DB Connection
def get_connection():
    return pymysql.connect(
        host='192.168.1.18',
        user='appuser',
        password='1234',
        database='taskmanagement',
        port=3306,
        cursorclass=DictCursor
    )
# 🔹 Reusable fetch function
def fetch_all(cursor, table, cid):
    cursor.execute(f"SELECT * FROM {table} WHERE cid = %s LIMIT 1", (cid,))
    return cursor.fetchall()

# 🔥 MAIN API
@app.get("/client/{cid}")
def get_full_client_profile(cid: int):
    conn = get_connection()
    cursor = conn.cursor()

    try:
        # 🔹 Client
        cursor.execute("SELECT * FROM clients WHERE id = %s LIMIT 1", (cid,))
        client = cursor.fetchone()

        if not client:
            raise HTTPException(status_code=404, detail="Client not found")

        # 🔹 Authorized Capital
        authorized = {
            "main": fetch_all(cursor, "auth_capital_details", cid),
            "equity": fetch_all(cursor, "equity_details", cid),
            "preference": fetch_all(cursor, "preference_details", cid),
        }

        # 🔹 Issued Capital
        issued = {
            "main": fetch_all(cursor, "iss_capital_details", cid),
            "equity": fetch_all(cursor, "equityissued_details", cid),
            "preference": fetch_all(cursor, "preferenceissued_details", cid),
        }

        # 🔹 Subscribed Capital
        subscribed = {
            "main": fetch_all(cursor, "sub_capital_details", cid),
            "equity": fetch_all(cursor, "equitysubscribed_details", cid),
            "preference": fetch_all(cursor, "preferencesubscribed_details", cid),
        }

        # 🔹 Paid Capital
        paid = {
            "main": fetch_all(cursor, "paid_capital_details", cid),
            "equity": fetch_all(cursor, "equitypaidup_details", cid),
            "preference": fetch_all(cursor, "preferencepaidup_details", cid),
        }

        return {
            "client": client,
            "authorized_capital": authorized,
            "issued_capital": issued,
            "subscribed_capital": subscribed,
            "paid_capital": paid
        }

    finally:
        cursor.close()
        conn.close()
@app.get("/related-details/{cin}")
def get_related_party_details(cin: str):

    conn = get_connection()
    cursor = conn.cursor(DictCursor)

    try:
        query = """
        SELECT
            c.company_name,
            c.cin,
            r.*
        FROM clients c
        JOIN related_party_entity r
            ON c.cin = r.cin
        WHERE c.cin = %s
        """

        cursor.execute(query, (cin.upper(),))
        related_details = cursor.fetchall()

        if not related_details:
            raise HTTPException(
                status_code=404,
                detail="No related party details found"
            )

        return {
            "company_name": related_details[0]["company_name"],
            "cin": cin,
            "total_connections": len(related_details),
            "related_party_details": related_details
        }

    finally:
        cursor.close()
        conn.close()
@app.get("/company/{company_name}")
def get_company_name(
    company_name: str,
    professionalid: int = 3   # default value
):
    conn = get_connection()
    cursor = conn.cursor(DictCursor)

    try:
        query = """
            SELECT *
            FROM clients
            WHERE company_name LIKE %s
            AND professionalid = %s
            ORDER BY com_type DESC
        """

        search_value = f"%{company_name.upper()}%"

        cursor.execute(query, (search_value, professionalid))

        company = cursor.fetchall()

        if not company:
            raise HTTPException(
                status_code=404,
                detail="Company not found"
            )

        return {
            "professionalid_used": professionalid,
            "company": company
        }

    finally:
        cursor.close()
        conn.close()

@app.get("/director/{din}")
def get_full_director_profile(din: int):
    conn = get_connection()
    cursor = conn.cursor(DictCursor)   # ✅ FIXED

    try:
        cursor.execute(
            """SELECT 
    d.*,
    rpe.*,
    c.*
FROM director_details d
LEFT JOIN related_party_entity rpe 
    ON d.din = rpe.din
LEFT JOIN clients c 
    ON rpe.cin = c.cin
WHERE d.din = %s
LIMIT 3;""",
            (din,)
        )
        director = cursor.fetchall()

        if not director:
            raise HTTPException(status_code=404, detail="Director not found")

        return {
            "director": director,
        }

    finally:
        cursor.close()
        conn.close()
        # SELECT COUNT(*) FROM clients c JOIN related_party_entity r ON c.cin = r.cin;