import sqlite3 as sql
from tabulate import tabulate
from toml import load
import logging


import argparse
from os.path import basename
import sys
import time

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
print("           Family Budget Overview Tool v1.2 Beta          ")
print("     This project is created by Juraj Honsch (c) 2022     ")
print()

# setup logging
logging.basicConfig(format="%(asctime)s - %(levelname)s: %(message)s",
                    datefmt='%m/%d/%Y %I:%M:%S %p', level=logging.INFO)
l = logging.getLogger("app")

parser = argparse.ArgumentParser(
    description="Utility to play with fbot database.")
parser.add_argument("-c", "--config", nargs="?", type=str,
                    default="./_config/config.toml", help="Path to config file.")
parser.add_argument("-d", "--database", nargs="?", type=str,
                    default="./_config/database.db", help="Path to database file.")
args = parser.parse_args()


try:
    file = load(open(args.config))["server"]["database"]
except Exception:
    try:
        file = args.database
    except Exception:
        l.exception("Cannot find database file. Specify options.")
        input()
        sys.exit(1)

try:
    prompt = basename(file)

    con = sql.connect(file)
    cur = con.cursor()
except Exception:
    l.exception("Error while opening database.")
    input()
    sys.exit(1)

print("Welcome to fbot database terminal!")
print(f"Sqlite version: {sql.sqlite_version}")
print()
print("If you want to know more info about fbot table,\ntype 'pragma table_info(data)' into terminal.")

while True:
    try:
        print()
        print("What do you want to do?")
        print()
        print("0: Exit")
        print("1: Rename category")
        print("2: Create structure")
        print("3: Run terminal")
        print()
        choice = input("Your selection: ")
    except KeyboardInterrupt:
        break

    if choice == "0":
        break
    elif choice == "1":
        try:
            old_name = input("Enter your category old name: ").strip()
            new_name = input("Enter your category new name: ").strip()

            cur.execute("update data set category = ? where category = ?",
                        (new_name, old_name))
            con.commit()

            print("Renamed successfully!")
            print("Note that you will need to edit config.toml file.")
        except KeyboardInterrupt:
            pass
        except Exception:
            logging.exception("Error while renaming category.")
    elif choice == "2":
        try:
            cur.execute(
                "create table if not exists data (uuid text, name text, amount numeric, type text, category text, date text, comment text)")
            con.commit()
            print("Succesfully created structure.")
        except Exception:
            logging.exception("Error while creating structure.")
    elif choice == "3":
        while True:
            try:
                query = input(f"({prompt}::sqlite3)$ ")

                t1 = time.time()

                cur.execute(query)
                if query := cur.fetchall():
                    t2 = time.time()

                    print(tabulate(query, tablefmt="grid"))
                    print(f"Result: {len(query)} rows; Took {t2-t1} seconds;")

                con.commit()
            except KeyboardInterrupt:
                break
            except Exception:
                logging.exception("Error while running query.")

print("\nBye!")
con.close()
