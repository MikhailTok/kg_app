from flask import Flask
from flask import render_template
from flask import url_for

app = Flask(__name__)



@app.route("/")
def index():
    return render_template("index.html")



if __name__ == '__main__':
    port = 5000
    app.run(host='0.0.0.0', port=port, debug=True)
