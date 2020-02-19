import os
import argparse
import sys
import json
import sqlite3


# TODO configure
def configure_query(delimiter=",",type="str", **kwargs) -> str:
    pass


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


def remove_user_from_bd(username = None, id=None) -> bool:
    """Removes user from db

    :param username: -- name of the user
    :param id: -- id of the user
    :return: True/False
    """
    query = "DELETE FROM users WHERE"
    if username and id:
        query += f" username='{username}' AND id={id}"
    elif username:
        query += f" username='{username}'"
    elif id:
        query += f" id={id}"
    else:
        print("Need args")
        return False
    print(query)
    dbname = get_config()["result"]["database"]
    connection = connect_db(dbname)
    cursor = connection.cursor()
    cursor.execute(query)
    connection.commit()
    cursor.execute("SELECT * FROM users")
    print(cursor.fetchall())
    return True


def change_user_settings(**keys) -> bool:
    """Changes user info

    :param username: - user login
    :param key: -- user password
    :param status: -- 0 or 1 | user or admin
    :return:
    """
    query = "UPDATE users SET "
    for i, values in enumerate(keys):
        if i == 0 and keys[values] is not None:
            query += f"{values}='{keys[values]}'"
            print("here")
            continue
        elif i != 0:
            query += f","
        if values == "status":
            if int(keys[values]) != 1 or int(keys[values]) != 0:
                return False
            else:
                query += f"{values}={keys[values]}"
        elif keys[values]:
            query += f"{values}='{keys[values]}'"
            print("ti kek realna")
    print(query)
    # dbname = get_config()["result"]["database"]
    # connection = connect_db(dbname)
    # cursor = connection.cursor()
    # cursor.execute(query)
    # connection.commit()
    # cursor.execute("SELECT * FROM users")
    # print(cursor.fetchall())
    return True

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
    users = dict()
    # Add user
    users["add"] = subparsers.add_parser("add_user")
    users["add"].add_argument("username")
    users["add"].add_argument("password")
    users["add"].add_argument("status")
    users["add"].set_defaults(add_user=add_user_to_db)
    # Remove user
    users["remove"] = subparsers.add_parser("remove_user")
    users["remove"].add_argument("--username", dest="removeuname")
    users["remove"].add_argument("--id", dest="removeid")
    users["remove"].set_defaults(remove_user=True)
    # Change user info
    users["change"] = subparsers.add_parser("change_user")
    users["change"].add_argument("--username", dest="change_name")
    users["change"].add_argument("--password", dest="change_pass")
    users["change"].add_argument("--status", dest="change_status")
    users["change"].set_defaults(change_user=True)
    args = parser.parse_args()

    # TODO don't pass function to the args or call it from args
    if "createsettings" in args:
        setup_handler()
    elif "add_user" in args:
        add_user_to_db(args.username, args.password, args.status)
    elif "remove_user" in args:
        print(args)
        remove_user_from_bd(username=args.removeuname, id=args.removeid)
    elif "change_user" in args:
        change_user_settings(username=args.change_name, password=args.change_pass, status=args.change_status)

if __name__ == "__main__":
    create_parser()
