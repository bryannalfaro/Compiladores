#create server for YAPL using Flask
from flask import Flask

app = Flask(__name__)

@app.route('/')
def hello_world():
    return 'Hello, World!'

@app.route('/yapl_compile')
def yapl_compile():
    return 'yapl_compile'

if __name__ == '__main__':
    app.run(debug=True)


