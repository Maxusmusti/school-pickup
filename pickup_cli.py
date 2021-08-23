import sys
import os
import psycopg2
from datetime import datetime

class Database:
    def __init__(self, conn):
        self.conn = conn
        self.keys = set()

    @staticmethod
    def init_db():
        DATABASE_URL = os.environ["DATABASE_URL"]
        conn = psycopg2.connect(DATABASE_URL, sslmode='require')
        return Database(conn)

    def get_log_list(self):
        sql = """SELECT * FROM logs"""
        try:
            cur = self.conn.cursor()
            cur.execute(sql)
            self.conn.commit()
            data = cur.fetchall()
            cur.close()
            return data
        except Exception as e:
            print('failed to create: ' + str(e))

    def insert_verify_data(self, phone_number, pfn, pln, cfn, cln, grade):
        sql = f"""INSERT INTO verify (phone_number, parent_first_name, parent_last_name, child_first_name, child_last_name, class)
                    VALUES ('{phone_number}', '{pfn}', '{pln}', '{cfn}', '{cln}', '{grade}')"""

        try:
            cur = self.conn.cursor()
            cur.execute(sql)
            self.conn.commit()
            cur.close()
            #print(sql)

        except Exception as e:
            print('failed to insert: ' + str(e))

    def delete_verify_data(self, number=None):
        sql = "DELETE FROM verify"
        if number:
            sql += f" WHERE phone_number='{number}'"
        try:
            cur = self.conn.cursor()
            cur.execute(sql)
            self.conn.commit()
            cur.close()
            print(f"Removed: {number}")

        except Exception as e:
            print('failed to delete: ' + str(e))

if len(sys.argv) == 2:
    if sys.argv[1] == "help":
        print("Options:\n    print_logs\n    logs_to_file\n    insert\n    delete")

    elif sys.argv[1] == "print_logs":
        db = Database.init_db()
        print(db.get_log_list())

    elif sys.argv[1] == "logs_to_file":
        db = Database.init_db()
        filename = input("Filename (including '.txt'): ")

        if filename == '':
            filename = datetime.now().strftime("%Y-%m-%d-LOGS.txt")

        outfile = open(filename, 'w')
        data = db.get_log_list()

        for log in data:
            log = list(log)
            log[0] = log[0].strftime("%m/%d/%Y, %H:%M:%S")
            outfile.write(str(log) + '\n')
        outfile.close()
        print("Complete!")
        
    elif sys.argv[1] == "insert":
        db = Database.init_db()
        number = input("Phone Number (Must be in format +1XXXXXXXXXX): ")
        pfn = input("Parent First Name: ")
        pln = input("Parent Last Name: ")
        cfn = input("Child First Name: ")
        cln = input("Child Last Name: ")
        grade = None
        while grade not in ['01', '02', '03', '04', '05', '06', '07', '08', 'EK', 'K', 'PRE3', 'PRE4', 'EPRE4', 'INF', 'OLD INF', 'TOD']:
            grade = input("Grade ('01'-'08', EK/K, PRE3, EPRE4, PRE4, INF, OLD INF, TOD): ")
        option = input(f"Are you sure you want to insert (number:{number}, pfn:{pfn}, pln:{pln}, cfn:{cfn}, cln:{cln}, grade:{grade})? If so, type 'YES': ")
        if option == 'YES':
            db.insert_verify_data(number, pfn, pln, cfn, cln, grade)
            print("Action complete")
        else:
            print("Insert aborted")
    
    elif sys.argv[1] == "delete":
        db = Database.init_db()
        number = input("Phone Number to remove (Must be in format +1XXXXXXXXXX, type 'all' instead to wipe numbers): ")
        if number and number[0] == '+' and number[1:].isdigit() and len(number) == 12:
            db.delete_verify_data(number)
        elif number == "all":
            option = input(f"Are you sure you want to delete everything? (TYPE 'YES' if so)")
            if option == 'YES':
                db.delete_verify_data()
                print("Database wiped")
            else:
                print("Database wipe aborted")
        else:
            print("No valid input, nothing removed")
            
    else:
        print("Invalid option, run with 'help' for valid option list")
else:
    print("only one option allowed, run with 'help' for valid option list")
