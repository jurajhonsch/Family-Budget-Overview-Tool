# server
from flask import *
import sqlite3 as sql
import waitress
import threading

# other stuff
import logging
from uuid import uuid4
import webbrowser
import argparse
import sys
import os

# config and reports
import json
import toml

# datetime
from pandas import date_range
from dateutil.relativedelta import relativedelta
import datetime
import time


# setup logging
logging.basicConfig(
    format="%(asctime)s - %(levelname)s: %(message)s",
    datefmt="%m/%d/%Y %I:%M:%S %p",
    level=logging.DEBUG,
)
l = logging.getLogger("fbot")


parser = argparse.ArgumentParser(
    prog="Family Budget Overview Tool",
    description="The purpose of this tool is to gather manual inputs, process them, and display various statistical reports.",
)
parser.add_argument(
    "-c", "--config", default="./_config/config.toml", help="Path to config file."
)
args = parser.parse_args()

# load and update config
try:
    config = toml.load(open(args.config))
except Exception:
    l.exception(f"Specify config file.")

app = Flask(
    __name__,
    static_folder=config["server"]["static_folder"],
    template_folder=config["server"]["dynamic_folder"],
)


with sql.connect(config["server"]["database"]) as con:
    cur = con.cursor()

    cur.execute(
        "create table if not exists data (uuid text, name text, amount numeric, type text, category text, date text, comment text)"
    )
    con.commit()


@app.route("/")
def index():
    limit = request.args.get("limit", default=config["display"]["limit"], type=int)
    args = {
        "limit": limit,
        "min_amount": round(request.args.get("min-amount", default=0, type=float), 2),
        "max_amount": round(request.args.get("max-amount", default=0, type=float), 2),
        "type": request.args.get("type", default="all"),
        "category": request.args.get("category", default="all"),
        "from_date": request.args.get("from-date", default=""),
        "to_date": request.args.get("to-date", default=""),
    }

    with sql.connect(config["server"]["database"]) as con:
        cur = con.cursor()

        query = []

        if args["min_amount"] > args["max_amount"] and args["max_amount"] > 0:
            args["min_amount"], args["max_amount"] = (
                args["max_amount"],
                args["min_amount"],
            )
        if args["min_amount"] > 0:
            query.append("amount >= :min_amount")
        if args["max_amount"] > 0:
            query.append("amount <= :max_amount")
        if args["type"] != "all":
            query.append("type = :type")
        if args["category"] != "all":
            query.append("category = :category")
        if args["from_date"]:
            query.append("date >= :from_date")
        if args["to_date"]:
            query.append("date <= :to_date")

        query = " where " + " and ".join(query) if query else ""
        query = (
            "select uuid, name, amount, type, category, date, comment from data"
            + query
            + " order by date desc"
        )
        query += " limit :limit" if args["limit"] > 0 else ""

        data = cur.execute(query, args).fetchall()

    has_data = bool(data)

    args.update(
        {
            "all_data": data,
            "has_data": has_data,
            "categories": config["display"]["categories"],
            "defaults_items": zip(
                config["defaults"].keys(),
                map(lambda x: x.items(), config["defaults"].values()),
            ),
        }
    )

    return render_template("index.html", **args)


@app.route("/chart")
def chart():
    chart_type = request.args.get("chart-type", default="")
    chart_type = (
        chart_type.title()
        if chart_type in ("epoch", "compare", "detail")
        else "Compare"
    )

    type = request.args.get("type", default="expense")
    category = request.args.get("category", default="all")
    from_date = request.args.get("from-date")
    to_date = request.args.get("to-date")

    return render_template(
        "chart.html",
        chart_type=chart_type,
        type=type,
        category=category,
        from_date=from_date,
        to_date=to_date,
        categories=config["display"]["categories"],
    )


@app.route("/chart-data")
def chart_data():
    status = {"status": "ok"}

    try:
        chart_type = request.args.get("chart-type", default="")
        type = request.args.get("type", default="expense")
        category = request.args.get("category", default="all")
        from_date = request.args.get("from-date", default="")
        to_date = request.args.get("to-date", default="")

        options = {
            "theme_primary": config["theme"]["dark"],
            "theme_medium": config["theme"]["primary"],
            "font_size": config["theme"]["font_size"],
        }

        if chart_type == "epoch" or chart_type == "":

            options["chart_type"] = config["chart"]["epoch"]

            with sql.connect(config["server"]["database"]) as con:
                cur = con.cursor()

                query = ["type = :type"]

                if from_date:
                    query.append("date >= :from_date")
                else:
                    cur.execute(
                        "select date from data where type = :type order by date asc limit 1",
                        {"type": type},
                    )
                    from_date = cur.fetchone()

                    assert from_date, "No data!"

                    from_date = from_date[0]

                if to_date:
                    query.append("date <= :to_date")
                else:
                    cur.execute(
                        "select date from data where type = :type order by date desc limit 1",
                        {"type": type},
                    )
                    to_date = cur.fetchone()

                    assert to_date, "No data!"

                    to_date = to_date[0]

                query = " where " + " and ".join(query) if query else ""
                query = (
                    "select category, amount, date from data"
                    + query
                    + " order by date asc"
                )

                cur.execute(
                    query,
                    {
                        "type": type,
                        "from_date": from_date,
                        "to_date": to_date,
                    },
                )

            data = []
            catsIndex = {}

            months = [
                datetime.datetime.fromisoformat(str(x).rsplit("-", 1)[0] + "-01")
                for x in date_range(
                    start=from_date,
                    end=datetime.datetime.fromisoformat(to_date)
                    + relativedelta(months=1),
                    freq="m",
                )
            ]

            for category, amount, date in cur:
                date = datetime.datetime.fromisoformat(date.rsplit("-", 1)[0] + "-01")

                if category not in catsIndex:
                    catsIndex[category] = len(data)
                    color = config["display"]["colors"][
                        config["display"]["categories"].index(category)
                        % len(config["display"]["colors"])
                    ]

                    data.append(
                        {
                            "label": category,
                            "backgroundColor": color,
                            "borderColor": color,
                            "data": [0],
                        }
                    )

                dataset = data[catsIndex[category]]["data"]
                current = months[len(dataset) - 1]

                if date > current:
                    dataset.extend(
                        [None] * len(date_range(start=current, end=date, freq="m"))
                    )
                    dataset[-1] = 0
                dataset[-1] += amount

            months = [x.strftime("%Y-%m") for x in months]

            status = {
                "status": "ok",
                "data": {
                    "data": {"labels": months, "datasets": data},
                    "options": options,
                },
            }
        elif chart_type == "compare":

            options["chart_type"] = config["chart"]["compare"]

            with sql.connect(config["server"]["database"]) as con:
                cur = con.cursor()

                query = ["type = :type"]

                if from_date:
                    query.append("date >= :from_date")

                if to_date:
                    query.append("date <= :to_date")

                query = " where " + " and ".join(query) if query else ""
                query = "select category, amount from data" + query

                cur.execute(
                    query, {"type": type, "from_date": from_date, "to_date": to_date}
                )

            data = {"labels": [], "datasets": [{"data": [], "backgroundColor": []}]}
            catsIndex = {}

            for category, amount in cur:
                if category not in catsIndex:
                    catsIndex[category] = len(data["labels"])
                    data["datasets"][0]["data"].append(0)

                    data["labels"].append(category)

                    color = config["display"]["colors"][
                        config["display"]["categories"].index(category)
                        % len(config["display"]["colors"])
                    ]
                    data["datasets"][0]["backgroundColor"].append(color)

                data["datasets"][0]["data"][catsIndex[category]] += amount

            assert len(data["labels"]), "No data"

            status = {"status": "ok", "data": {"data": data, "options": options}}

        elif chart_type == "detail":

            assert category != "all", "Select category"

            options["chart_type"] = config["chart"]["detail"]

            with sql.connect(config["server"]["database"]) as con:
                cur = con.cursor()

                query = ["type = :type", "category = :category"]

                if from_date:
                    query.append("date >= :from_date")
                else:
                    cur.execute(
                        "select date from data where category = :category and type = :type order by date asc limit 1",
                        {"category": category, "type": type},
                    )
                    from_date = cur.fetchone()

                    assert from_date, "No data!"

                    from_date = from_date[0]

                if to_date:
                    query.append("date <= :to_date")
                else:
                    cur.execute(
                        "select date from data where category = :category and type = :type order by date desc limit 1",
                        {"category": category, "type": type},
                    )
                    to_date = cur.fetchone()

                    assert to_date, "No data!"

                    to_date = to_date[0]

                query = " where " + " and ".join(query) if query else ""
                query = "select amount, date from data" + query + " order by date asc"

                cur.execute(
                    query,
                    {
                        "type": type,
                        "category": category,
                        "from_date": from_date,
                        "to_date": to_date,
                    },
                )

            days = list(
                map(
                    lambda x: x.strftime("%Y-%m-%d"),
                    date_range(start=from_date, end=to_date, freq="d"),
                )
            )
            data = [0] * len(days)

            color = config["display"]["colors"][
                config["display"]["categories"].index(category)
                % len(config["display"]["colors"])
            ]

            from_date = datetime.datetime.fromisoformat(from_date)

            for amount, date in cur:
                date = datetime.datetime.fromisoformat(date)
                data[(date - from_date).days] += amount

            status = {
                "status": "ok",
                "data": {
                    "data": {
                        "labels": days,
                        "datasets": [
                            {
                                "label": category,
                                "backgroundColor": color,
                                "borderColor": color,
                                "data": data,
                            }
                        ],
                    },
                    "options": options,
                },
            }
        else:
            status = {
                "status": "error",
                "description": "Invalid chart-type argument in get request. Valid values are 'epoch', 'compare'.",
            }
    except Exception as e:
        status = {"status": "error", "description": str(e)}
        logging.exception("Error while compiling chart data.")

    return json.dumps(status)


@app.route("/update-row", methods=["POST"])
def updateRow():
    status = {"status": "ok"}

    try:
        data = {
            "uuid": request.form.get("uuid"),
            "name": request.form.get("name"),
            "amount": request.form.get("amount"),
            "type": request.form.get("type"),
            "category": request.form.get("category"),
            "date": request.form.get("date"),
            "comment": request.form.get("comment"),
        }

        with sql.connect(config["server"]["database"]) as con:
            cur = con.cursor()

            cur.execute(
                "update data set name=:name, amount=:amount, category=:category, date=:date, comment=:comment where uuid=:uuid",
                data,
            )

            con.commit()
    except Exception as e:
        status = {"status": "error", "description": str(e)}
        logging.exception("Error updating row.")

    return json.dumps(status)


@app.route("/delete-row", methods=["POST"])
def deleteRow():
    status = {"status": "ok"}

    try:
        data = {"uuid": request.form.get("uuid")}

        with sql.connect(config["server"]["database"]) as con:
            cur = con.cursor()

            cur.execute("delete from data where uuid=:uuid", data)

            con.commit()
    except Exception as e:
        status = {"status": "error", "description": str(e)}
        logging.exception("Error deleting row.")

    return json.dumps(status)


@app.route("/add-row", methods=["POST"])
def addRow():
    status = {"status": "ok"}

    try:
        data = {
            "uuid": uuid4().hex,
            "name": request.form.get("name"),
            "amount": request.form.get("amount"),
            "type": request.form.get("type"),
            "category": request.form.get("category"),
            "date": request.form.get("date"),
            "comment": request.form.get("comment"),
        }

        with sql.connect(config["server"]["database"]) as con:
            cur = con.cursor()

            cur.execute(
                "insert into data (uuid, name, amount, type, category, date, comment) values (:uuid, :name, :amount, :type, :category, :date, :comment)",
                data,
            )

            con.commit()
    except Exception as e:
        status = {"status": "error", "description": str(e)}
        logging.exception("Error adding row.")

    return json.dumps(status)


@app.route("/theme.css")
def theme():
    return Response(
        render_template("theme.css", **config["theme"]), mimetype="text/css"
    )


timestamp = time.time()  # timestamp


@app.after_request
def after_request(response):
    global timestamp

    timestamp = time.time()

    return response


@app.route("/keep-alive", methods=["post"])
def keep_alive():
    return json.dumps({"status": "ok"})


print("       ___           ___           ___           ___      ")
print("      /\  \         /\  \         /\  \         /\  \     ")
print("     /::\  \       /::\  \       /::\  \        \:\  \    ")
print("    /:/\:\  \     /:/\:\  \     /:/\:\  \        \:\  \   ")
print("   /::\~\:\  \   /::\~\:\__\   /:/  \:\  \       /::\  \  ")
print("  /:/\:\ \:\__\ /:/\:\ \:|__| /:/__/ \:\__\     /:/\:\__\ ")
print("  \/__\:\ \/__/ \:\~\:\/:/  / \:\  \ /:/  /    /:/  \/__/ ")
print("       \:\__\    \:\ \::/  /   \:\  /:/  /    /:/  /      ")
print("        \/__/     \:\/:/  /     \:\/:/  /     \/__/       ")
print("                   \::/__/       \::/  /                  ")
print("                    ~~            \/__/                   ")
print("                                                          ")
print("           Family Budget Overview Tool v1.1 Beta          ")
print("     This project is created by Juraj Honsch (c) 2022     ")
print()


def server_thread():
    waitress.serve(app, host=config["server"]["host"], port=config["server"]["port"])


t1 = threading.Thread(target=server_thread, daemon=True)

t1.start()

if config["server"]["browser"] != False:
    url = "http://{}:{}/".format(config["server"]["host"], config["server"]["port"])

    l.info("Opening browser at " + url)

    if config["server"]["browser"]:
        try:
            webbrowser.get(config["server"]["browser"]).open_new_tab(url)
        except:
            l.error("Error opening browser. Copy link to your browser.")
    else:
        webbrowser.open_new_tab(url)

if config["server"]["exit_on_close"]:
    while True:
        try:
            time.sleep(config["server"]["idle_interval"])
        except KeyboardInterrupt:
            break

        if time.time() - timestamp > config["server"]["idle_interval"]:
            break

    l.info("App closed by inactivity. Bye!")
    sys.exit()

try:
    t1.join()
except KeyboardInterrupt:
    pass

l.info("App closed. Bye!")
