import requests
from typing import List
from mbn import BufferStore
from .utils import iso_to_unix, load_url
import json


class RetrieveParams:
    def __init__(
        self, symbols: List[str], start_ts: str, end_ts: str, schema: str
    ):
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


class HistoricalClient:
    def __init__(self, api_url: str = ""):
        if not api_url:
            api_url = load_url("HISTORICAL_URL")

        self.api_url = f"{api_url}/historical"
        # self.api_key = api_key

    def list_instruments(self):
        url = f"{self.api_url}/instruments/list"

        response = requests.get(url)

        if response.status_code != 200:
            raise ValueError(
                f"Instrument list retrieval failed: {response.text}"
            )
        return response.json()

    def create_records(self, data: List[int]):
        """
        Stream loading main used for testing.
        """

        url = f"{self.api_url}/mbp/create"

        response = requests.post(url, json=data, stream=True)

        if response.status_code != 200:
            raise ValueError(f"Error while creating records : {response.text}")

        last_response = None  # Variable to store the last parsed JSON object

        # Read the streamed content in chunks
        for chunk in response.iter_content(chunk_size=None):
            if chunk:  # filter out keep-alive chunks
                try:
                    chunk_data = json.loads(chunk.decode("utf-8"))
                    last_response = chunk_data  # Keep updating with the latest parsed response
                except json.JSONDecodeError as e:
                    print(f"Failed to parse chunk as JSON: {e}")

        # Return the last response
        return last_response

    def get_records(self, params: RetrieveParams):
        url = f"{self.api_url}/mbp/get"

        data = params.to_dict()
        response = requests.get(url, json=data, stream=True)

        if response.status_code != 200:
            raise ValueError(
                f"Instrument list retrieval failed: {response.text}"
            )

        bin_data = bytearray()

        # Read the streamed content in chunks

        # Read the streamed content in chunks
        for chunk in response.iter_content(chunk_size=None):
            if chunk:  # filter out keep-alive or non-binary chunks
                if b"Finished streaming all batches" in chunk:
                    continue
                bin_data.extend(chunk)

        return BufferStore(bytes(bin_data))
