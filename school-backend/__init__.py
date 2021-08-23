from flask import Flask, jsonify, render_template, request, send_from_directory
from flask_cors import CORS
import datetime
from pytz import timezone
import json
import os
import _thread
import requests
import psycopg2
from twilio.twiml.messaging_response import MessagingResponse, Message
from twilio.rest import Client


class Database:
    def __init__(self, conn):
        self.conn = conn
        self.eastern = timezone("US/Eastern")
        self.db_url = os.environ["DATABASE_URL"]

    @staticmethod
    def init_db():
        DATABASE_URL = os.environ["DATABASE_URL"]
        conn = psycopg2.connect(DATABASE_URL, sslmode="require")
        return Database(conn)

    def get_full_list(self):
        sql = """SELECT * FROM logs 
                 LEFT JOIN completed ON (logs.phone_number, logs.child_first_name, logs.child_last_name)=(completed.phone_number, completed.child_first_name, completed.child_last_name) 
                 WHERE completed.phone_number is NULL ORDER BY date_time ASC"""

        try:
            cur = self.conn.cursor()
            cur.execute(sql)
            self.conn.commit()
            data = cur.fetchall()
            cur.close()
            print(data)
            return data

        except Exception as e:
            print("failed to create: " + str(e))
            cur.close()
            self.conn = psycopg2.connect(self.db_url, sslmode="require")

    def validate(self, number):
        sql = f"SELECT * FROM verify WHERE phone_number='{number}'"
        try:
            cur = self.conn.cursor()
            cur.execute(sql)
            self.conn.commit()
            data = cur.fetchall()
            cur.close()

            if data:
                print(data)
                return data
            else:
                print("NOTHING")
                return None

        except Exception as e:
            print("failed to select: " + str(e))
            cur.close()
            self.conn = psycopg2.connect(self.db_url, sslmode="require")

    def completed(self, number):
        sql = f"SELECT * FROM completed WHERE phone_number='{number}'"
        try:
            cur = self.conn.cursor()
            cur.execute(sql)
            self.conn.commit()
            data = cur.fetchall()
            cur.close()

            sql = f"SELECT * FROM logs WHERE phone_number='{number}'"
            cur = self.conn.cursor()
            cur.execute(sql)
            self.conn.commit()
            logs = cur.fetchall()
            cur.close()

            if len(data) == len(logs):
                print(f"Already completed: {data}")
                return data
            else:
                return None

        except Exception as e:
            print("failed to select: " + str(e))
            cur.close()
            self.conn = psycopg2.connect(self.db_url, sslmode="require")

    def indiv_comp(self, number, cfn, cln):
        sql = f"SELECT * FROM completed WHERE (phone_number, child_first_name, child_last_name)=('{number}','{cfn}','{cln}')"
        try:
            cur = self.conn.cursor()
            cur.execute(sql)
            self.conn.commit()
            data = cur.fetchall()
            cur.close()
            if data:
                print(f"Already completed: {data}")
                return data
        except Exception as e:
            print("failed to select: " + str(e))
            cur.close()
            self.conn = psycopg2.connect(self.db_url, sslmode="require")
        return None

    def insert_completed(self, number, cfn, cln):
        if db.indiv_comp(number, cfn, cln):
            return 0

        sql = f"INSERT INTO completed (phone_number, child_first_name, child_last_name) VALUES ('{number}', '{cfn}', '{cln}')"
        try:
            cur = self.conn.cursor()
            cur.execute(sql)
            self.conn.commit()
            cur.close()
            return 1

        except Exception as e:
            print("failed to select: " + str(e))
            cur.close()
            self.conn = psycopg2.connect(self.db_url, sslmode="require")
            return 0

    def load_log_data(self, number, pfn, pln, cfn, cln, gd, msg):
        date_time = str(datetime.datetime.now().astimezone(self.eastern))
        sql = f"SELECT * FROM logs WHERE (phone_number, child_first_name, child_last_name)=('{number}', '{cfn}', '{cln}')"
        try:
            cur = self.conn.cursor()
            cur.execute(sql)
            self.conn.commit()
            data = cur.fetchall()
            cur.close()

            if data:
                sql = f"UPDATE logs SET date_time = '{date_time}', message = '{msg}' WHERE phone_number='{number}'"

                try:
                    cur = self.conn.cursor()
                    cur.execute(sql)
                    self.conn.commit()
                    cur.close()
                    return 1

                except Exception as e:
                    print("failed to select: " + str(e))
                    cur.close()
                    self.conn = psycopg2.connect(self.db_url, sslmode="require")
                    return 0

        except Exception as e:
            print("failed to select: " + str(e))
            cur.close()
            self.conn = psycopg2.connect(self.db_url, sslmode="require")
            return 0

        phone_number = number
        parent_first_name = pfn
        parent_last_name = pln
        child_first_name = cfn
        child_last_name = cln
        grade = gd
        message = msg
        sql = f"""INSERT INTO logs (date_time, phone_number, parent_first_name, parent_last_name, child_first_name, child_last_name, class, message)
                  VALUES ('{date_time}', '{phone_number}', '{parent_first_name}', '{parent_last_name}', '{child_first_name}', '{child_last_name}', '{grade}', '{message}')"""

        try:
            cur = self.conn.cursor()
            cur.execute(sql)
            self.conn.commit()
            cur.close()
            print("Inserted")

        except Exception as e:
            print("failed to insert: " + str(e))
            cur.close()
            self.conn = psycopg2.connect(self.db_url, sslmode="require")

    def check_reset(self):
        today = datetime.datetime.now().astimezone(self.eastern)
        sql = "SELECT date_time FROM logs ORDER BY date_time DESC LIMIT 1"
        try:
            cur = self.conn.cursor()
            cur.execute(sql)
            self.conn.commit()
            data = cur.fetchall()
            if data:
                if not today.date() == data[0][0].date():
                    return -1
            return 1
            cur.close()
        except Exception as e:
            print("failed to select: " + str(e))
            cur.close()
            self.conn = psycopg2.connect(self.db_url, sslmode="require")
            return 0

    def reset(self):
        sql = "DELETE FROM completed"
        try:
            cur = self.conn.cursor()
            cur.execute(sql)
            self.conn.commit()
            cur.close()
            print("Deleted")
        except Exception as e:
            print("failed to delete: " + str(e))
            cur.close()
            self.conn = psycopg2.connect(self.db_url, sslmode="require")
        sql = "DELETE FROM logs"
        try:
            cur = self.conn.cursor()
            cur.execute(sql)
            self.conn.commit()
            cur.close()
            print("Deleted")
        except Exception as e:
            print("failed to delete: " + str(e))
            cur.close()
            self.conn = psycopg2.connect(self.db_url, sslmode="require")


account_sid = os.environ["ACCOUNT_SID"]
auth_token = os.environ["AUTH_TOKEN"]

app = Flask(__name__, static_folder="../school-todo/build")
CORS(app)

db = Database.init_db()
day = None


@app.route("/sms", methods=["POST"])
def inbound_sms():
    from_number = request.form["From"]
    to_number = request.form["To"]

    body = request.form["Body"].replace("'", "")

    data = db.validate(from_number)

    response = MessagingResponse()

    def _populate_kids(data):
        for child in data:
            db.load_log_data(
                child[0], child[1], child[2], child[3], child[4], child[5], body
            )

    if data:
        global day
        if (
            not day
            or not day.date()
            == datetime.datetime.now().astimezone(timezone("US/Eastern")).date()
        ):
            reset_time = db.check_reset()
            day = datetime.datetime.now().astimezone(timezone("US/Eastern"))
            if reset_time < 0:
                db.reset()

        if not db.completed(from_number):
            response.message("Thanks! Your child's pickup info has been updated.")
            _thread.start_new_thread(_populate_kids, (data,))
        else:
            response.message(
                "Sorry, but your daily pickup has been marked as complete by the front-desk for today. Please pickup manually if this was a mistake, and let them know at the front!"
            )
    else:
        response.message(
            "Sorry, but this number is not registered in our system. If you wish to fix this, please leave your number with the front desk"
        )

    print(from_number)
    print(to_number)
    print(body)
    return str(response)


@app.route("/api/getlist", methods=["GET"])
def get_sorted_list():
    def _reset():
        db.reset()

    return json.dumps(db.get_full_list(), default=str)


@app.route("/api/done", methods=["POST"])
def mark_as_complete():
    data = request.get_json(force=True)
    phone = data["phone"]
    print("data")
    child_first = data["childFirst"]
    child_last = data["childLast"]
    if db.insert_completed(phone, child_first, child_last):
        return {"status": True}
    return {"status": False}


# Serve React App
@app.route("/", defaults={"path": ""})
@app.route("/<path:path>")
def serve(path):
    print(app.static_folder + "/" + path)
    if path != "" and os.path.exists(app.static_folder + "/" + path):
        return send_from_directory(app.static_folder, path)
    else:
        return send_from_directory(app.static_folder, "index.html")


if __name__ == "__main__":
    app.run(use_reloader=True, port=5000, threaded=True)
