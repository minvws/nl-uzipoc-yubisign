from app.bootstrap import ApplicationBootstrapper
from dotenv import load_dotenv


if __name__ == "__main__":
    load_dotenv()

    ApplicationBootstrapper().start()
