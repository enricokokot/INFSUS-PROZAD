from flask import Flask, jsonify, make_response, render_template, request
from pony import orm
from datetime import datetime
from decimal import Decimal

DB = orm.Database()

app = Flask(__name__)


class Item(DB.Entity):
    name = orm.Required(str, unique=True)
    category = orm.Required(str)
    price = orm.Required(Decimal)
    amount = orm.Required(int)


class Receipt(DB.Entity):
    time = orm.Required(str, unique=True)
    items = orm.Required(orm.StrArray)
    amounts = orm.Required(orm.IntArray)
    total_price = orm.Required(Decimal)


class DailyTraffic(DB.Entity):
    date = orm.Required(str)
    total_traffic = orm.Required(Decimal)


class DetailedDailyTraffic(DB.Entity):
    date = orm.Required(str)
    items = orm.Required(orm.StrArray)
    amounts = orm.Required(orm.IntArray)
    prices = orm.Required(orm.FloatArray)


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
            items_in_cart = 0
            sold_items = []
            total_cost = 0
            amount_sold = []
            current_time = datetime.now()
            for item_name, sold_amount in json_request.items():
                if not sold_amount == "Choose amount":
                    item = Item.get(name=item_name)
                    item.amount -= int(sold_amount)
                    sold_items.append(item.name)
                    amount_sold.append(int(sold_amount))
                    total_cost += int(sold_amount) * item.price
                    items_in_cart += 1
            if (not items_in_cart):
                raise Exception("No items in cart")
            Receipt(time=str(current_time),
                    items=sold_items,
                    amounts=amount_sold,
                    total_price=total_cost)
            item_prices = []
            for sold_item in sold_items:
                item_prices.append(float(Item.get(name=sold_item).price))
            existing_day = DetailedDailyTraffic.get(
                date=str(current_time.date()))
            if (not existing_day):
                DetailedDailyTraffic(date=str(current_time.date()),
                                     items=sold_items,
                                     amounts=amount_sold,
                                     prices=item_prices)
            else:
                items_already_sold = existing_day.items
                for sold_item in sold_items:
                    if sold_item in items_already_sold:
                        index_of_existing_item = items_already_sold.index(
                            sold_item)
                        existing_day.amounts[index_of_existing_item] += amount_sold[sold_items.index(
                            sold_item)]
                    else:
                        items_already_sold.append(sold_item)
                        existing_day.amounts.append(
                            amount_sold[sold_items.index(sold_item)])
                        existing_day.prices.append(
                            item_prices[sold_items.index(sold_item)])
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
        return {"response": "Fail", "error": str(e)}


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


def get_detailed_daily_traffic():
    try:
        with orm.db_session:
            db_querry = orm.select(
                x for x in DetailedDailyTraffic if x.date == str(datetime.now().date()))[:]
            results_list = []
            for r in db_querry:
                results_list.append(r.to_dict())
            if results_list:
                todays_traffic = results_list[0]
                items = todays_traffic["items"]
                amounts = todays_traffic["amounts"]
                amounts, items = (list(t)
                                  for t in zip(*sorted(zip(amounts, items))))
                todays_traffic["items"] = items
                todays_traffic["amounts"] = amounts
                response = {"response": "Success", "data": todays_traffic}
            else:
                response = {"response": "Success", "data": {}}
            return response
    except Exception as e:
        return {"response": "Fail", "error": str(e)}


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
        response2 = get_all_receipts()

        if response["response"] == "Success" and response2["response"] == "Success":
            return make_response(render_template("register.html",
                                                 items=response["data"],
                                                 receipts=response2["data"][-5:],
                                                 zip=zip), 200)
        elif response["error"] == "No items in cart" and response2["response"] == "Success":
            response = get_all_items()
            return make_response(render_template("register.html",
                                                 items=response["data"],
                                                 receipts=response2["data"][-5:],
                                                 zip=zip,
                                                 sentEmptyOrder=True), 200)
        else:
            return make_response(render_template("register.html",
                                                 zip=zip,
                                                 sentEmptyOrder=True), 200)
    else:
        response = get_all_items()
        response2 = get_all_receipts()
        if response["response"] == "Success" and response2["response"] == "Success":
            return make_response(render_template("register.html", items=response["data"], receipts=response2["data"][-5:], zip=zip), 200)
        else:
            return make_response(render_template("register.html", zip=zip), 200)


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

        response1 = get_all_items()
        response2 = get_all_receipts()
        response3 = get_all_daily_traffic()
        response4 = get_detailed_daily_traffic()
        if response1["response"] == "Success" and \
           response2["response"] == "Success" and \
           response3["response"] == "Success" and \
           response4["response"] == "Success":
            items_data = response1["data"]
            receipts_data = response2["data"]
            daily_traffic = response3["data"]
            detailed_daily_traffic = response4["data"]
            days = []
            traffic = []
            for day in daily_traffic[-5:]:
                days.append(day["date"])
                traffic.append(float(day["total_traffic"]))
            return make_response(render_template("manager.html",
                                                 items=items_data,
                                                 receipts=receipts_data,
                                                 days=days,
                                                 traffic=traffic,
                                                 detailed_daily_traffic=detailed_daily_traffic,
                                                 zip=zip), 200)
        else:
            return make_response(jsonify(response1), 400)

    elif request.form.get("_method") == "DELETE":
        try:
            item_to_delete = request.form.get("name")
        except Exception as e:
            response = {"response": str(e)}
            return make_response(jsonify(response), 400)
        response = delete_item(item_to_delete)
        response1 = get_all_items()
        response2 = get_all_receipts()
        response3 = get_all_daily_traffic()
        response4 = get_detailed_daily_traffic()
        if response1["response"] == "Success" and \
           response2["response"] == "Success" and \
           response3["response"] == "Success" and \
           response4["response"] == "Success":
            items_data = response1["data"]
            receipts_data = response2["data"]
            daily_traffic = response3["data"]
            detailed_daily_traffic = response4["data"]
            days = []
            traffic = []
            for day in daily_traffic[-5:]:
                days.append(day["date"])
                traffic.append(float(day["total_traffic"]))
            return make_response(render_template("manager.html",
                                                 items=items_data,
                                                 receipts=receipts_data,
                                                 days=days,
                                                 traffic=traffic,
                                                 detailed_daily_traffic=detailed_daily_traffic,
                                                 zip=zip), 200)
        else:
            return make_response(jsonify(response1), 400)

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
        response1 = get_all_items()
        response2 = get_all_receipts()
        response3 = get_all_daily_traffic()
        response4 = get_detailed_daily_traffic()
        if response1["response"] == "Success" and \
           response2["response"] == "Success" and \
           response3["response"] == "Success" and \
           response4["response"] == "Success":
            items_data = response1["data"]
            receipts_data = response2["data"]
            daily_traffic = response3["data"]
            detailed_daily_traffic = response4["data"]
            days = []
            traffic = []
            for day in daily_traffic[-5:]:
                days.append(day["date"])
                traffic.append(float(day["total_traffic"]))
            return make_response(render_template("manager.html",
                                                 items=items_data,
                                                 receipts=receipts_data,
                                                 days=days,
                                                 traffic=traffic,
                                                 detailed_daily_traffic=detailed_daily_traffic,
                                                 zip=zip), 200)
        else:
            return make_response(render_template("manager.html",
                                                 detailed_daily_traffic={},
                                                 zip=zip), 200)

    else:
        response1 = get_all_items()
        response2 = get_all_receipts()
        response3 = get_all_daily_traffic()
        response4 = get_detailed_daily_traffic()
        if response1["response"] == "Success" and \
           response2["response"] == "Success" and \
           response3["response"] == "Success" and \
           response4["response"] == "Success":
            items_data = response1["data"]
            receipts_data = response2["data"]
            daily_traffic = response3["data"]
            detailed_daily_traffic = response4["data"]
            days = []
            traffic = []
            for day in daily_traffic[-5:]:
                days.append(day["date"])
                traffic.append(float(day["total_traffic"]))
            return make_response(render_template("manager.html",
                                                 items=items_data,
                                                 receipts=receipts_data,
                                                 days=days,
                                                 traffic=traffic,
                                                 detailed_daily_traffic=detailed_daily_traffic,
                                                 zip=zip), 200)
        else:
            DB.create_tables()
            return make_response(render_template("manager.html",
                                                 detailed_daily_traffic={},
                                                 zip=zip), 200)


if __name__ == "__main__":
    app.run(port=8080)
