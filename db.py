import sqlite3
import os

def create_database():
    conn = sqlite3.connect('history.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS history (
              
              id INTEGER PRIMARY KEY,

              user_id INTERGER,

              dialogue_id INTEGER,
              question_id INTEGER,

              model TEXT,
              
              question TEXT NOT NULL,
              picture TEXT,

              answer TEXT,
              answer_picture TEXT,

              date datetime default current_timestamp)''')
    conn.commit()
    conn.close()


if __name__ == '__main__':

    if not os.path.exists('./uploads'):
        os.makedirs('./uploads')

    create_database()