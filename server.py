from flask import Flask, render_template

app = Flask(__name__)


@app.route('/')
def home():
    return render_template('home.html')


@app.route('/register')
def register():
    items = [{id: 0, 'name': 'milk', 'category': 'dairy', 'price': 9.99},
             {id: 1, 'name': 'cheese', 'category': 'dairy', 'price': 4.99},
             {id: 2, 'name': 'soda', 'category': 'beverage', 'price': 6.99},
             {id: 3, 'name': 'flour', 'category': 'grain', 'price': 2.99},
             {id: 4, 'name': 'pork steak', 'category': 'meat', 'price': 24.99},
             {id: 4, 'name': 'pork steak', 'category': 'meat', 'price': 24.99},
             {id: 4, 'name': 'pork steak', 'category': 'meat', 'price': 24.99},
             {id: 4, 'name': 'pork steak', 'category': 'meat', 'price': 24.99},
             {id: 4, 'name': 'pork steak', 'category': 'meat', 'price': 24.99},
             {id: 4, 'name': 'pork steak', 'category': 'meat', 'price': 24.99},
             ]
    return render_template('register.html', items=items)


@app.route('/manager')
def manager():
    return render_template('manager.html')


if __name__ == "__main__":
    app.run(port=8080)
