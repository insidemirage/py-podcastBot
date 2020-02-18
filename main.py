import config
import os
from multiprocessing import Queue
from bot import bot_main


def setup() -> dict:
    token: str = ""
    proxy = ""
    token = config.api.get("BOT_TOKEN")
    if token is None:
        print("BOT_TOKEN not found in config.py \n Trying to find it in env")
        token = os.environ.get("BOT_TOKEN")
        if token is None:
            raise Exception("Token not found")
    proxy = config.api.get("PROXY")

    if proxy is None or len(proxy) < 1:
        print("Proxy not declared")
        proxy = None

    return {"proxy": proxy, "token": token}


def main():
    settings = setup()
    queue = Queue()
    bot_main(queue, settings)


if __name__ == "__main__":
    main()