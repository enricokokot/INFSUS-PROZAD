from flask import Flask, render_template

app = Flask(__name__)


@app.route('/')
def home():
    return render_template('home.html')


@app.route('/register')
def register():
    return render_template('register.html')


@app.route('/manager')
def manager():
    return render_template('manager.html')


if __name__ == "__main__":
    app.run(port=8080)
