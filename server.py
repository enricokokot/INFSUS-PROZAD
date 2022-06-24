import math
import string
import random
from flask import Flask, jsonify, make_response, redirect, render_template, request, url_for
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


class ReceiptFile(DB.Entity):
    receiptNumber = orm.PrimaryKey(int, auto=True)
    receiptId = orm.Required(str)
    file = orm.Required(str)


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
            generate_receipt(str(current_time))
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
        print("erradadada " + str(e))
        return {"response": "Fail", "error": str(e)}


def generate_receipt(receipt_time):
    try:
        def round_up(n, decimals=0):
            multiplier = 10 ** decimals
            return Decimal(math.ceil(n * multiplier) / multiplier)

        zki = generate_zki()
        jir = generate_jir()

        this_receipt = Receipt.get(time=receipt_time)
        item_names = this_receipt.items
        item_amounts = this_receipt.amounts
        item_prices = []
        item_tax = []
        categories_for_B = ["newspaper", "agriculture"]
        categories_for_D = ["bread", "milk",
                            "children", "book", "magazine", "medicine"]
        with orm.db_session:
            for item in item_names:
                item_prices.append(Item.get(name=item).price)
                try:
                    item_category = Item.get(name=item).category
                    if item_category in categories_for_D:
                        item_tax.append("D")
                    elif item_category in categories_for_B:
                        item_tax.append("B")
                    else:
                        item_tax.append("A")
                except Exception as e:
                    print(e)
            # TODO: find out why this makes ids available
            db_querry = orm.select(
                x for x in Receipt if x.time == receipt_time)[:]
            print(db_querry)
        total = 0
        total_for_A = 0
        total_for_B = 0
        total_for_D = 0
        for amount, price, tax in zip(item_amounts, item_prices, item_tax):
            added_amount = amount * price
            total += added_amount
            if tax == "D":
                total_for_D += added_amount
            elif tax == "B":
                total_for_B += added_amount
            else:
                total_for_A += added_amount

        with open('receipt.txt', 'w', encoding="utf-8") as f:
            f.write('                  SPAR HRVATSKA d.o.o.')
            f.write('\n          Slavonska avenija 50, 10000 Zagreb')
            f.write('\n            MB: 1527100 OIB: 46108893754')
            f.write('\n               SPAR SUPERMARKET Labin')
            f.write('\n               Pulska 2C, 52220 Labin')
            f.write('\n')
            f.write('\n')
            f.write('\n*****************************************************')
            f.write('\n                      OTVORENO')
            f.write('\n                PON-SUB  7:00 - 21:00')
            f.write('\n                NEDJELJA 8:00 - 21:00')
            f.write('\n')
            f.write('\n           SPAR - supermarket za svaki dan')
            f.write('\n=====================================================')
            f.write('\nNaziv artikla')
            f.write('\nKoličina          Cijena              Iznos         P')
            f.write('\n-----------------------------------------------------')
            for item, amount, price, tax in zip(item_names,
                                                item_amounts,
                                                item_prices,
                                                item_tax):
                f.write('\n')
                f.write(item)
                f.write('\n')
                for _ in range(7 - len(str(amount))):
                    f.write(' ')
                f.write(str(amount))
                f.write(' x')
                for _ in range(14 - len(str(price))):
                    f.write(' ')
                f.write(str(price))
                f.write(' =')
                for _ in range(18 - len(str(amount*price))):
                    f.write(' ')
                f.write(str(amount*price))
                f.write('         ')
                f.write(tax)
            f.write('\n-----------------------------------------------------')
            f.write('\nUkupno kn')
            for _ in range(34 - len(str(total))):
                f.write(' ')
            f.write(str(total))
            f.write('\n=====================================================')
            f.write('\nPRIMLJENO   Gotovina')
            for _ in range(23 - len(str((round_up(total))) + ".00")):
                f.write(' ')
            f.write(str(round_up(total)) + ".00")
            f.write('\nVRAĆENO     kn')
            for _ in range(29 - len(str(round_up(total) - total))):
                f.write(' ')
            f.write(str(round_up(total) - total))
            f.write('\n')
            f.write('\nP  PDV(%)    Osnovica      Iznos')
            f.write('\n-----------------------------------------------------')
            if "A" in item_tax:
                f.write('\nA   25.00')
                for _ in range(12 - len(str(round(total_for_A * Decimal(0.75), 2)))):
                    f.write(' ')
                f.write(str(round(total_for_A * Decimal(0.75), 2)))
                for _ in range(11 - len(str(round(total_for_A * Decimal(0.25), 2)))):
                    f.write(' ')
                f.write(str(round(total_for_A * Decimal(0.25), 2)))
            if "B" in item_tax:
                f.write('\nB   13.00')
                for _ in range(12 - len(str(round(total_for_B * Decimal(0.87), 2)))):
                    f.write(' ')
                f.write(str(round(total_for_B * Decimal(0.87), 2)))
                for _ in range(11 - len(str(round(total_for_B * Decimal(0.13), 2)))):
                    f.write(' ')
                f.write(str(round(total_for_B * Decimal(0.13), 2)))
            if "D" in item_tax:
                f.write('\nD    5.00')
                for _ in range(12 - len(str(round(total_for_D * Decimal(0.95), 2)))):
                    f.write(' ')
                f.write(str(round(total_for_D * Decimal(0.95), 2)))
                for _ in range(11 - len(str(round(total_for_D * Decimal(0.05), 2)))):
                    f.write(' ')
                f.write(str(round(total_for_D * Decimal(0.05), 2)))
            f.write('\n-----------------------------------------------------')
            f.write('\nBroj računa:')
            f.write(' ')
            f.write(str(this_receipt.get_pk()))
            f.write("/870272/102")
            f.write('\nZKI:')
            f.write(zki)
            f.write('\n')
            f.write('\nJIR:')
            f.write(jir)
            f.write('\n')
            f.write('\n')
            f.write('\n')
            f.write('\nLabin                                ')
            f.write(datetime.strptime(this_receipt.time,
                    "%Y-%m-%d %H:%M:%S.%f").strftime("%d.%m.%Y %H:%M"))
            f.write('\nBlagajna 102 Trans 8388 Blagajnik 10231')
            f.write('\n')
            f.write('\n*****************************************************')
            f.write('\n                   NAJLJEPŠE HVALA')
            f.write('\n                    NA POVJERENJU')
            f.write('\n*********************www.spar.hr*********************')
            f.write('\n')
            f.write('\n')
        with open('receipt.txt', encoding="utf-8") as f:
            with orm.db_session:
                ReceiptFile(receiptId=receipt_time, file=f.read())
    except Exception as e:
        print(str(e))
        return {"response": "Fail", "error": str(e)}


def generate_zki():
    return ''.join(random.SystemRandom().choice(string.ascii_lowercase + string.digits) for _ in range(36))


def generate_jir():
    chars = string.ascii_lowercase + string.digits
    first_row = ''.join(random.SystemRandom().choice(chars) for _ in range(8))
    second_row = ''.join(random.SystemRandom().choice(chars) for _ in range(4))
    third_row = ''.join(random.SystemRandom().choice(chars) for _ in range(4))
    fourth_row = ''.join(random.SystemRandom().choice(chars) for _ in range(4))
    fifth_row = ''.join(random.SystemRandom().choice(chars) for _ in range(12))
    return first_row + "-" + second_row + "-" + third_row + "-" + fourth_row + "-" + fifth_row


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

    elif request.method == "POST" and request.form.get("mission") == "redirect":
        try:
            receiptId = request.form.get("receipt")
            return redirect(url_for('manager_receipt', receiptId=receiptId))
        except Exception as e:
            print(e)

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


@app.route('/manager/receipt', methods=["GET"])
def manager_receipt():
    receiptId = request.args["receiptId"]
    with orm.db_session:
        if (not ReceiptFile.get(receiptId=receiptId)):
            generate_receipt(receiptId)
        receipt = ReceiptFile.get(receiptId=receiptId).file
        with open('new_receipt.txt', 'w', encoding="utf-8") as f:
            f.write(receipt)
            return render_template("receipt.html", receiptId=receipt)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
