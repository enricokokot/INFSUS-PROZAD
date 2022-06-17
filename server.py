from flask import Flask, jsonify, make_response, render_template, request
from pony import orm
from datetime import datetime

DB = orm.Database()

app = Flask(__name__)


class Item(DB.Entity):
    name = orm.Required(str, unique=True)
    category = orm.Required(str)
    price = orm.Required(float)
    amount = orm.Required(int)


class Receipt(DB.Entity):
    time = orm.Required(str, unique=True)
    items = orm.Required(orm.StrArray)
    amounts = orm.Required(orm.IntArray)
    total_price = orm.Required(float)


class DailyTraffic(DB.Entity):
    date = orm.Required(str)
    total_traffic = orm.Required(float)


DB.bind(provider="sqlite", filename="database.sqlite", create_db=True)
DB.generate_mapping(create_tables=True)


def add_item(json_request):
    try:
        name = json_request["name"]
        category = json_request["category"]
        price = json_request["price"]
        amount = json_request["amount"]
        with orm.db_session:
            Item(name=name, category=category, price=price, amount=amount)
            db_querry = orm.select(x for x in Item)[:]
            results_list = []
            for r in db_querry:
                results_list.append(r.to_dict())
            response = {"response": "Success", "data": results_list}
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


def update_item(json_request):
    try:
        name = json_request["name"]
        new_name = json_request["new name"]
        category = json_request["category"]
        price = json_request["price"]
        amount = json_request["amount"]
        with orm.db_session:
            item = Item.get(name=name)
            if (new_name):
                item.name = new_name
            if (price):
                item.price = price
            if (category):
                item.category = category
            if (amount):
                item.amount = amount
            db_querry = orm.select(x for x in Item)[:]
            results_list = []
            for r in db_querry:
                results_list.append(r.to_dict())
            response = {"response": "Success", "data": results_list}
            return response
    except Exception as e:
        return {"response": "Fail", "error": e}


def sell_items(json_request):
    try:
        with orm.db_session:
            sold_items = []
            total_cost = 0
            amount_sold = []
            current_time = datetime.now()
            for item_name, sold_amount in json_request.items():
                if (int(sold_amount) > 0):
                    item = Item.get(name=item_name)
                    item.amount -= int(sold_amount)
                    sold_items.append(item.name)
                    amount_sold.append(int(sold_amount))
                    total_cost += int(sold_amount) * item.price
            Receipt(time=str(current_time),
                    items=sold_items,
                    amounts=amount_sold,
                    total_price=total_cost)
            existing_traffic = DailyTraffic.get(date=str(current_time.date()))
            if (existing_traffic):
                existing_traffic.total_traffic += total_cost
            else:
                DailyTraffic(date=str(current_time.date()),
                             total_traffic=total_cost)
            db_querry = orm.select(x for x in Item)[:]
            results_list = []
            for r in db_querry:
                results_list.append(r.to_dict())
            response = {"response": "Success", "data": results_list}
            return response
    except Exception as e:
        return {"response": "Fail", "error": e}


def delete_item(item_to_delete):
    try:
        with orm.db_session:
            item = Item.get(name=item_to_delete)
            item.delete()
            db_querry = orm.select(x for x in Item)[:]
            results_list = []
            for r in db_querry:
                results_list.append(r.to_dict())
            response = {"response": "Success", "data": results_list}
            return response
    except Exception as e:
        return {"response": "Fail", "error": e}


def get_all_receipts():
    try:
        with orm.db_session:
            db_querry = orm.select(x for x in Receipt)[:]
            results_list = []
            for r in db_querry:
                results_list.append(r.to_dict())
            response = {"response": "Success", "data": results_list}
            return response
    except Exception as e:
        return {"response": "Fail", "error": e}


def get_all_daily_traffic():
    try:
        with orm.db_session:
            db_querry = orm.select(x for x in DailyTraffic)[:]
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


@app.route('/register', methods=["GET", "POST"])
def register():
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

        response = sell_items(json_request)

        if response["response"] == "Success":
            return make_response(render_template("register.html", items=response["data"]), 200)
        else:
            return make_response(jsonify(response), 400)
    else:
        response = get_all_items()
        if response["response"] == "Success":
            return make_response(render_template("register.html", items=response["data"]), 200)
        else:
            return make_response(jsonify(response), 400)


@app.route('/manager', methods=["POST", "GET", "PATCH", "DELETE"])
def manager():
    if request.form.get("_method") == "PATCH":
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

        response = update_item(json_request)

        if response["response"] == "Success":
            return make_response(render_template("manager.html", items=response["data"], receipts=get_all_receipts()["data"]), 200)
        else:
            return make_response(jsonify(response), 400)

    elif request.form.get("_method") == "DELETE":
        try:
            item_to_delete = request.form.get("name")
        except Exception as e:
            response = {"response": str(e)}
            return make_response(jsonify(response), 400)
        response = delete_item(item_to_delete)
        if response["response"] == "Success":
            return make_response(render_template("manager.html", items=response["data"], receipts=get_all_receipts()["data"]), 200)
        else:
            return make_response(jsonify(response), 400)

    elif request.method == "POST":
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
            return make_response(render_template("manager.html", items=response["data"], receipts=get_all_receipts()["data"]), 200)
        else:
            return make_response(jsonify(response), 400)

    else:
        response = get_all_items()
        response2 = get_all_receipts()
        response3 = get_all_daily_traffic()
        if response["response"] == "Success" and response2["response"] == "Success" and response3["response"] == "Success":
            items_data = response["data"]
            receipts_data = response2["data"]
            daily_traffic = response3["data"]
            days = []
            traffic = []
            for day in daily_traffic[-5:]:
                days.append(day["date"])
                traffic.append(day["total_traffic"])
            return make_response(render_template("manager.html", items=items_data, receipts=receipts_data, days=days, traffic=traffic), 200)
        else:
            return make_response(jsonify(response), 400)


if __name__ == "__main__":
    app.run(port=8080)
