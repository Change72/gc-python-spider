from methods.db_method import DB_Connection

if __name__ == '__main__':
    db = DB_Connection()
    db.open_connection()
    db.close_connection()