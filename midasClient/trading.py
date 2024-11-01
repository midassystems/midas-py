import requests
from typing import Dict
from .utils import load_url
from mbn import BacktestData


class TradingClient:
    def __init__(self, api_url: str = ""):
        if not api_url:
            api_url = load_url("TRADING_URL")

        self.api_url = f"{api_url}/trading"

    # self.api_key = api_key

    def create_backtest(self, data: BacktestData):
        url = f"{self.api_url}/backtest/create"

        response = requests.post(url, json=data)

        if response.status_code != 200:
            raise ValueError(
                f"Instrument list retrieval failed: {response.text}"
            )
        return response.json()

    def delete_backtest(self, id: int) -> Dict:
        url = f"{self.api_url}/backtest/delete"

        response = requests.delete(url, json=id)

        if response.status_code != 200:
            raise ValueError(
                f"Instrument list retrieval failed: {response.text}"
            )
        return response.json()

    def get_backtest(self, id: int) -> Dict:
        url = f"{self.api_url}/backtest/get?id={id}"

        response = requests.get(url)  # json=id)

        if response.status_code != 200:
            raise ValueError(
                f"Instrument list retrieval failed: {response.text}"
            )
        return response.json()
