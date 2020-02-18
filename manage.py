import os
import argparse
import sys
import json
import sqlite3


def get_config() -> dict:
    print("Loading settings.json file")
    path = f"{get_folder()}/settings.json"
    if not os.path.isfile(path):
        print("File not exists! Use setup")
        return {}

    try:
        file = open(path, "r")
    except PermissionError:
        raise PermissionError("Change permissions to the folder")

    try:
        result = json.loads(file.read())
        file.close()
        return {"result": result, "path": path}

    except json.JSONDecodeError as e:
        print(e)
        file.close()
        return {}


def get_folder() -> str:
    return os.path.dirname(os.path.abspath(__file__))


# TODO refactor set_proxy and set_token func
def set_proxy(proxy: str) -> bool:
    """Sets proxy in settings.json

    :param: proxy -- proxy link
    """
    resp = get_config()
    if not resp:
        return False
    data = resp["result"]
    path = resp["path"]
    data["proxy"] = proxy
    with open(path, "w") as file:
        json.dump(data, file, sort_keys=True, indent="")
    return True


def set_token(token):
    """Sets token in settings.json

        :param: token -- bot token
        """
    resp = get_config()
    if not resp:
        return False
    data = resp["result"]
    path = resp["path"]
    data["token"] = token
    with open(path, "w") as file:
        json.dump(data, file, sort_keys=True, indent="")
    return True


def add_user_to_db(username, password, status) -> bool:
    dbname = get_config()["result"]["database"]
    connection = connect_db(dbname)
    cursor = connection.cursor()
    cursor.execute("INSERT INTO users(username,key,status) VALUES(?,?,?)", (username, password, status,))
    connection.commit()
    cursor.execute("SELECT * FROM users")
    print(cursor.fetchall())
    return True


def remove_user_from_bd() -> bool:
    pass


def change_user_status() -> bool:
    pass


def connect_db(dbname) -> sqlite3.connect:
    """Connection to Database function
    :param dbname: -- database name
    """
    path = f"{get_folder()}/{dbname}.db"
    try:
        connect = sqlite3.connect(path)
        return connect
    except sqlite3.Error:
        return False


def drop_db(dbname: str) -> bool:
    """Removes DataBase
    :param dbname: -- name of the database
    """
    path = f"{get_folder()}/{dbname}.db"
    if os.path.isfile(path):
        os.remove(path)
        return True
    else:
        print("No db file")
        return False


def create_db(dbname) -> bool:
    """Creates DataBase with table users:
    id | username | key | status
    :param dbname: -- database name
    """
    path = f"{get_folder()}/{dbname}.db"
    try:
        connection = sqlite3.connect(path)
        print("Database created")
        cursor = connection.cursor()
        cursor.execute("""CREATE TABLE users(id integer PRIMARY KEY, username text, key text, status integer)""")
        connection.commit()
        connection.close()
        return True
    except sqlite3.Error:
        return False


def setup_handler() -> bool:
    """Creates new json settings file"""
    print("Creating settings.json file")
    path = f"{get_folder()}/settings.json"
    try:
        file = open(path, "w+")
    except PermissionError:
        raise PermissionError("Change permissions to the folder")

    token = input("Input your token: ")
    proxy = input("Input proxy(or press Enter): ")
    database = input("Input database name: ")
    result = {}

    if len(token) > 10:
        result["token"] = token

    if proxy.strip():
        result["proxy"] = proxy.strip()

    if database.strip():
        result["database"] = database.strip()
        create_db(result["database"])
    else:
        return False

    json.dump(result, file)

    return True


def create_parser() -> None:
    parser = argparse.ArgumentParser(description="Manage bot settings", prog="Bot manage")
    subparsers = parser.add_subparsers(help="Manage commands")

    """
    Create settings
    """
    create_set = subparsers.add_parser("create-settings")
    create_set.set_defaults(createsettings=setup_handler)
    # create_set.add_argument("--force", action="store_const", const=setup_handler)
    """
    Proxy commands
    """
    proxy = dict()

    # Set command
    proxy["set"] = subparsers.add_parser("set_proxy")
    proxy["set"].add_argument("proxy", action="store", help="Set proxy to bot", type=set_proxy)

    # Remove command
    proxy["remove"] = subparsers.add_parser("remove_proxy")
    proxy["remove"].add_argument("proxy", action="store", help="Removes proxy value from settings")

    """
    Token commands
    """
    token = dict()

    # Set command
    token["set"] = subparsers.add_parser("set_token")
    token["set"].add_argument("token", action="store", help="Set token of the bot", type=set_token)

    """
    Database commands
    """
    database = dict()

    # Remove DB
    database["drop"] = subparsers.add_parser("dropdb")
    database["drop"].add_argument("dbname", action="store", help="DB name", type=drop_db)

    # Create DB
    database["create"] = subparsers.add_parser("createdb")
    database["create"].add_argument("dbname", action="store", help="DB name", type=create_db)

    """
    Users
    """
    uuu = subparsers.add_parser("add_user")
    uuu.add_argument("username")
    uuu.add_argument("password")
    uuu.add_argument("status")
    uuu.set_defaults(add_user=add_user_to_db)
    args = parser.parse_args()

    # TODO don't pass function to the args or call it from args
    if "createsettings" in args:
        setup_handler()
    elif "add_user" in args:
        add_user_to_db(args.username, args.password, args.status)


if __name__ == "__main__":
    create_parser()
