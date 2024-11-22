from flask import Flask
from flask import render_template
from flask import url_for
from flask import request
from flask import session
from flask import send_from_directory
import base64
import os

from db_queries import sql_request, write_to_db

from PIL import Image
import io
import time
from dotenv import load_dotenv
load_dotenv()

from openai import OpenAI

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ['SECRET_KEY']
app.config['UPLOAD_FOLDER'] = os.path.join(app.root_path, 'uploads')

client = OpenAI(
    api_key=os.environ['API_KEY'],
    base_url=os.environ['BASE_URL'],
)


@app.route('/admin')
def admin():
    return render_template('admin.html', history=sql_request('SELECT * FROM history'))

@app.route("/")
@app.route("/<dialogue_id>")
def index(dialogue_id=None):

    user_id = session.get("user_id")
    content = None
    history = None

    if user_id is None:
        max_userid = sql_request(f"SELECT max(user_id) from history")[0][0]
        user_id = 1 if not max_userid else max_userid + 1
        session["user_id"] = user_id

    else:
        history = sql_request(f"""SELECT distinct dialogue_id from history where user_id = {user_id}""")

        if dialogue_id is None:
            dialogue_id = sql_request(f"SELECT max(dialogue_id) from history where user_id = {user_id}")[0][0]
        if dialogue_id:
            content = sql_request(f"""SELECT    id,
                                                user_id,
                                                dialogue_id,
                                                question_id,
                                                model,
                                                question,
                                                case when picture is not null then '/uploads/' || picture else picture end as picture,
                                                answer,
                                                answer_picture
                                        from history
                                        where user_id = {user_id} and dialogue_id = {dialogue_id} order by question_id ASC""")
            
        
        print(history)

    return render_template("index.html", dialogue=content, history=history)


@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)
        
 
# MODEL = "gpt-3.5-turbo"

# response = client.chat.completions.create(
#     model=MODEL,
#    messages=[
#     {"role": "system", "content": "You are a helpful assistant."},
#     {"role": "user", "content": "Who won the world series in 2020?"},
#     {"role": "assistant", "content": "The Los Angeles Dodgers won the World Series in 2020."},
#     {"role": "user", "content": "Where was it played?"}
#   ],
#     temperature=0,
#     )

def encode_image(image):
    return base64.b64encode(image).decode('utf-8')


def read_image(path):
    with open(f'./uploads/{path}', 'rb')as image_file:
        base64_image = encode_image(image_file.read())
    return base64_image


def get_content(content, model):
    prepared_content = []
    for item in content:

        user_content = []
        user_content.append({'type': 'text', 'text': item[5]})

        if item[6] and model == '4.0':
            user_content.append({"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{read_image(item[6])}", "detail": "low"}})

        user = {"role": "user", "content": user_content}
        assistant = {"role": "assistant", "content": [{'type': 'text', 'text': item[7]}]}
        prepared_content.extend([user, assistant])
    return prepared_content


@app.route('/question', methods=['POST'])
def question():
    question = request.form.get('text')
    image = request.files.get('image')
    model = request.form.get('model')
    new_dialogue = int(request.form.get('new_dialogue'))

    user_id = session.get("user_id")

    picture_name = None


    dialogue_id = sql_request(f"SELECT max(dialogue_id) from history where user_id = {user_id}")[0][0]

    if new_dialogue:

        if dialogue_id:
            dialogue_id += 1
            question_id = 1
        else:
            dialogue_id, question_id = 1, 1
        content = []

    elif dialogue_id is None:
        content = []
        dialogue_id, question_id = 1, 1

    else:
        content = sql_request(f"SELECT * from history where user_id = {user_id} and dialogue_id = {dialogue_id} order by question_id ASC")

        if content:
            question_id = max([i[3] for i in content if i[3]]) + 1
            content = get_content(content, model)
        else:
            question_id = 1

    current_content = [{"type": "text", "text": question}]


    if image and model == '4.0':
        image = image.read()

        base64_image = encode_image(image)

        image_stream = io.BytesIO(image)
        image_stream = Image.open(image_stream)

        picture_name = f'user_id_{user_id}_dialogue_id_{dialogue_id}_question_id_{question_id}.png'
        image_stream.save(f'./uploads/{picture_name}', 'PNG')

        image = [{"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{base64_image}", "detail": "low"}}]
        current_content += image

    current_content = [{"role": "user", "content": current_content}]
    content += current_content

    
    # MODEL = 'gpt-4o-mini-2024-07-18' if model == '4.0' else "gpt-3.5-turbo"
    # chat_completion = client.chat.completions.create(
    #     model=MODEL,
    #     messages=content,
    #     temperature=0,
    #     )
    # answer = chat_completion.choices[0].message.content


    time.sleep(1)
    answer = 'Ответ бота'



    write_to_db(user_id, dialogue_id, question_id, model, question, picture_name, answer, None)

    return {'answer': answer}


if __name__ == '__main__':
    port = 5000
    app.run(host='0.0.0.0', port=port, debug=True)
