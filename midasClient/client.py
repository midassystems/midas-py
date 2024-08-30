import requests
from typing import List, Dict
from mbn import BufferStore
from .utils import iso_to_unix


class RetrieveParams:
    def __init__(self, symbols: List[str], start_ts: str, end_ts: str, schema: str):
        self.symbols: List[str] = symbols
        self.start_ts = iso_to_unix(start_ts)
        self.end_ts = iso_to_unix(end_ts)
        self.schema = schema

    def to_dict(self):
        return {
            "symbols": self.symbols,
            "start_ts": self.start_ts,
            "end_ts": self.end_ts,
            "schema": self.schema,
        }


class DatabaseClient:
    def __init__(self, api_url: str = "http://127.0.0.1:8000"):
        self.api_url = api_url
        # self.api_key = api_key

    def list_instruments(self):
        url = f"{self.api_url}/market_data/instruments/list"

        response = requests.get(url)

        if response.status_code != 200:
            raise ValueError(f"Instrument list retrieval failed: {response.text}")
        return response.json()

    def create_backtest(self, data: Dict):
        url = f"{self.api_url}/trading/backtest/create"

        response = requests.post(url, json=data)

        if response.status_code != 200:
            raise ValueError(f"Instrument list retrieval failed: {response.text}")
        return response.json()

    def delete_backtest(self, id: int) -> Dict:
        url = f"{self.api_url}/trading/backtest/delete"

        response = requests.delete(url, json=id)

        if response.status_code != 200:
            raise ValueError(f"Instrument list retrieval failed: {response.text}")
        return response.json()

    def get_backtest(self, id: int) -> Dict:
        url = f"{self.api_url}/trading/backtest/get?id={id}"

        response = requests.get(url)  # json=id)

        if response.status_code != 200:
            raise ValueError(f"Instrument list retrieval failed: {response.text}")
        return response.json()

    def get_records(self, params: RetrieveParams):
        url = f"{self.api_url}/market_data/mbp/get"

        data = params.to_dict()
        response = requests.get(url, json=data, stream=True)

        if response.status_code != 200:
            raise ValueError(f"Instrument list retrieval failed: {response.text}")

        # Initialize an empty byte array to collect the streamed data
        bin_data = bytearray()

        # Read the streamed content in chunks
        for chunk in response.iter_content(chunk_size=None):
            if chunk:  # filter out keep-alive chunks
                bin_data.extend(chunk)

        return BufferStore(bytes(bin_data))
