import sqlite3



def sql_request(sql):
    conn = sqlite3.connect('history.db')
    c = conn.cursor()
    c.execute(sql)
    out = c.fetchall()
    conn.close()
    return out


def write_to_db(user_id, dialogue_id, question_id, model, question, picture, answer, answer_picture):
    fields = (user_id, dialogue_id, question_id, model, question, picture, answer, answer_picture)
    conn = sqlite3.connect('history.db')
    c = conn.cursor()
    c.execute("INSERT INTO history (user_id, dialogue_id, question_id, model, question, picture, answer, answer_picture) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",  fields)
    conn.commit()
    conn.close()