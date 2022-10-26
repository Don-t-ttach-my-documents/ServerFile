import sqlite3
import secrets
class DBHandler:
    def __init__(self, pathDB, nameTable):
        self.pathDB = pathDB
        self.conn = sqlite3.connect(pathDB)
        self.cursor = self.conn.cursor()
        self.nameTable = nameTable
        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS """+self.nameTable+""" (
            token TEXT PRIMARY KEY,
            pathToFile TEXT NOT NULL
            )
        """)
        self.conn.commit()
        self.conn.close()

    def addPath(self, path):
        token = secrets.token_urlsafe()
        while (self.getDataWithKey(token) is not None):
            token = secrets.token_urlsafe()
        self.addData({"token":token, "pathToFile":path})

        return token

    def addData(self, data):
        self.conn = sqlite3.connect(self.pathDB)
        self.cursor = self.conn.cursor()
        print("INSERT INTO "+self.nameTable+" VALUES(:token, :pathToFile)")
        self.cursor.execute("INSERT INTO "+self.nameTable+" VALUES(:token, :pathToFile)", data)
        self.conn.commit()
        self.conn.close()

    def getData(self):
        self.conn = sqlite3.connect(self.pathDB)
        self.cursor = self.conn.cursor()
        self.cursor.execute("""SELECT * FROM """+self.nameTable)
        res = self.cursor.fetchall()
        self.conn.close()
        return res

    def getDataWithKey(self, key):
        self.conn = sqlite3.connect(self.pathDB)
        self.cursor = self.conn.cursor()
        self.cursor.execute("SELECT pathToFile FROM "+self.nameTable+" WHERE token=\""+key+"\"")
        res = self.cursor.fetchone()
        self.conn.close()
        return res

        

    def removeTable(self):
        self.conn = sqlite3.connect(self.pathDB)
        self.cursor = self.conn.cursor()
        self.cursor.execute("DROP TABLE "+self.nameTable)
        self.conn.commit()
        self.conn.close()
