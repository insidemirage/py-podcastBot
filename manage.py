import os
import argparse
import sys
import json
import sqlite3


def get_folder() -> str:
    return os.path.dirname(os.path.abspath(__file__))


def drop_db_handler(dbname) -> bool:
    path = f"{get_folder()}/{dbname}.db"
    if os.path.isfile(path):
        os.remove(path)
        return True
    else:
        print("No db file")
        return False


def create_db_handler(dbname) -> bool:
    path = f"{get_folder()}/{dbname}.db"
    try:
        sqlite3.connect(path)
        return True
    except sqlite3.Error:
        return False


def setup_handler() -> bool:
    """Creates new json settings file
    :return:
    """
    print("Creating settings.json file")
    path = f"{get_folder()}/settings.json"
    try:
        file = open(path, "w+")
    except PermissionError:
        raise PermissionError("Change permissions to the folder")

    token = input("Input your token:")
    proxy = input("Input proxy(or press Enter)")
    result = {}

    if len(token) > 10:
        result["token"] = token

    if proxy.strip():
        result["proxy"] = proxy.strip()

    json.dump(result, file)

    return True


def load_json_settings() -> dict:
    path = f"{get_folder()}/settings.json"
    if os.path.isfile(path):
        print("File exists")
        file = open(path, "r").read()
        result = json.loads(file)
        return result
    else:
        print("No settings file found. use setup command to create")
        return {}


def set_handler(settings: dict) -> bool:
    settings_file = load_json_settings()
    if settings_file is {}:
        return False
    if settings_file.get("proxy") and settings.get("proxy"):
        settings_file.update({"proxy": settings.get("proxy")})
    if settings_file.get("token") and settings.get("token"):
        settings_file.update({"token": settings.get("token")})

    print(settings_file)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Manage bot settings")
    commands_parser = parser.add_subparsers(help="Command for manage token/proxy")
    parser_set = commands_parser.add_parser("set", help="Adds proxy or token")
    parser_set.add_argument("-p", help="set the proxy, usage: set/drop -p [proxy_link]", dest="proxy", type=str)
    parser_set.add_argument("-t", help="set the token, usage: set/drop -t [token]", dest="token", type=str)
    parser_set.set_defaults(which="set")
    parser_dropbd = commands_parser.add_parser("drop", help="Drops database")
    parser_dropbd.add_argument("dbname", dest="dbname")
    parser_dropbd.set_defaults(which="dropdb")
    parser_createdb = commands_parser.add_parser("createbd")
    parser_createdb.add_argument("dbname", dest="dbname")
    parser_createdb.set_defaults(which="createdb")
    args = parser.parse_args()
    # if args.which is "set":
    #     result = {"proxy": args.proxy, "token": args.token}
    # print(load_json_settings())
    # setup_handler()
    create_db_handler("123")