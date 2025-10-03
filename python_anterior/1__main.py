from flask import Flask


app = Flask(__name__)


@app.route('/')
def index():
    return "hola"


@app.route('/nosotros')
def nosotros():
    return "hola nosotros"



if __name__=='__main__':
    app.run(debug=True, host='0.0.0.0', port=8080)