import sqlite3
from sqlite3 import Error


class databaseConnect:
    def __init__(self, query):
        self.query = query

    def connection(self):
        try:
            self.con = sqlite3.connect('stack_overflow.db')
        except Error as error:
            print(f"Error while connecting to sqlite3 {error}")

        cursor = self.con.cursor()
        return cursor

    def closeConnect(self):
        return self.con.close()

    def execute(self):
        conn = self.connection()
        conn.execute("PRAGMA foreign_keys = ON")
        '''
        Foreign key constraints are disabled by default
        (for backwards compatibility), so must be enabled separately
        for each database connection.
        '''
        try:
            if type(self.query) == tuple:
                conn.execute(*self.query)
            else:
                conn.execute(self.query)
            output = conn.fetchall()
            return output
        except sqlite3.Error as e:
            print(f"Query cannot be executed,{e}")
        finally:
            self.con.commit()
            conn.close()
            self.closeConnect()



