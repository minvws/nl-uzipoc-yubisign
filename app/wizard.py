import logging
from app.bootstrap import ApplicationBootstrapper
from dotenv import load_dotenv


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    load_dotenv()

    ApplicationBootstrapper().start()
