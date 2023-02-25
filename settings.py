from dotenv import load_dotenv
import os

load_dotenv()


BOT_TOKEN = os.getenv("BOT_TOKEN")
COMMAND_SYMBOL = os.getenv("COMMAND_SYMBOL")
AWS_ACCESS_KEY = os.getenv("AWS_ACCESS_KEY")
AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")
AWS_TABLE = os.getenv("AWS_TABLE")
NET_NAME=os.getenv("NET_NAME")

STARTING_COINS=10
DANGER_PLAYER_MIN = 5
DANGER_LENGTH_SECONDS = 10000
DANGER_LENGTH_HOURS = 6
TEXT_CHANNEL="danger-dollar"

