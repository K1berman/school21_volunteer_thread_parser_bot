import os
from dotenv import load_dotenv


load_dotenv()

TOKEN = os.getenv("TOKEN")
URL = os.getenv("URL")
LOGIN = os.getenv("ROCKET21_LOGIN")
PASSWORD = os.getenv("ROCKET21_PASSWORD")
TG_USER_ID = os.getenv("TG_USER_ID")