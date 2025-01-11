from dotenv import load_dotenv
from .historical import HistoricalClient
from .trading import TradingClient


class DatabaseClient:
    def __init__(self):
        load_dotenv()

        self.historical = HistoricalClient()
        self.trading = TradingClient()
        # self.api_key = api_key
