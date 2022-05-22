from flask import Flask, jsonify, make_response, render_template, request
from pony import orm

DB = orm.Database()

app = Flask(__name__)


class Item(DB.Entity):
    name = orm.Required(str, unique=True)
    category = orm.Required(str)
    price = orm.Required(float)


DB.bind(provider="sqlite", filename="database.sqlite", create_db=True)
DB.generate_mapping(create_tables=True)


def add_item(json_request):
    try:
        name = json_request["name"]
        category = json_request["category"]
        price = json_request["price"]
        with orm.db_session:
            Item(name=name, category=category, price=price)
            response = {"response": "Success"}
            return response
    except Exception as e:
        return {"response": "Fail", "error": e}


def get_all_items():
    try:
        with orm.db_session:
            db_querry = orm.select(x for x in Item)[:]
            results_list = []
            for r in db_querry:
                results_list.append(r.to_dict())
            response = {"response": "Success", "data": results_list}
            return response
    except Exception as e:
        return {"response": "Fail", "error": e}


@app.route('/')
def home():
    return render_template('home.html')


@app.route('/register', methods=["GET"])
def register():
    response = get_all_items()
    if response["response"] == "Success":
        return make_response(render_template("register.html", items=response["data"]), 200)
    else:
        return make_response(jsonify(response), 400)


@app.route('/manager', methods=["POST", "GET"])
def manager():
    if request.method == "POST":
        try:
            json_request = {}
            for key, value in request.form.items():
                if value == "":
                    json_request[key] = None
                else:
                    json_request[key] = value
        except Exception as e:
            response = {"response": str(e)}
            return make_response(jsonify(response), 400)

        response = add_item(json_request)

        if response["response"] == "Success":
            return make_response(render_template("manager.html"), 200)
        else:
            return make_response(jsonify(response), 400)
    return render_template('manager.html')


if __name__ == "__main__":
    app.run(port=8080)
