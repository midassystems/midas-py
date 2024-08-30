import unittest
import os
import requests
from dotenv import load_dotenv
from midasClient import DatabaseClient
import json
import struct
from midasClient.client import RetrieveParams
from mbn import BufferStore

# Load url
load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

if DATABASE_URL is None:
    raise ValueError("DATABASE_URL environment variable is not set")


# Helper methods
def create_instruments(ticker: str, name: str) -> int:
    url = f"{DATABASE_URL}/market_data/instruments/create"
    data = {"ticker": ticker, "name": name}

    response = requests.post(url, json=data).json()

    id = response["data"]
    return id


def delete_instruments(id: int) -> None:
    url = f"{DATABASE_URL}/market_data/instruments/delete"

    _ = requests.delete(url, json=id).json()


def create_records(binary_data: list):
    url = f"{DATABASE_URL}/market_data/mbp/create"

    _ = requests.post(url, json=binary_data)


class TestClientMethods(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.client = DatabaseClient(str(DATABASE_URL))

    # @unittest.skip("")
    def test_list_instruments(self):
        # Setup
        id = create_instruments("AAPL8", "Apple Inc.")

        # Test
        response = self.client.list_instruments()

        # Validate
        self.assertEqual(response["code"], 200)

        # Cleanup
        delete_instruments(id)

    # @unittest.skip("")
    def test_create_backtest(self):
        # Setup
        with open("tests/data/test_data.backtest.json", "r") as f:
            data = json.load(f)

        # Test
        response = self.client.create_backtest(data)
        id = response["data"]

        # Validate
        self.assertEqual(response["code"], 200)

        # Cleanup
        self.client.delete_backtest(id)

    # @unittest.skip("")
    def test_get_backtest(self):
        # Setup
        with open("tests/data/test_data.backtest.json", "r") as f:
            data = json.load(f)

        # Create backtest
        response = self.client.create_backtest(data)
        id = response["data"]

        # Test
        response = self.client.get_backtest(id)

        # Validate
        self.assertEqual(response["code"], 200)

        # Cleanup
        self.client.delete_backtest(id)

    def test_get_records(self):
        # Setup
        id = create_instruments("AAPL", "Apple Inc.")
        new_id_bytes = struct.pack("<I", id)

        # Load binary records
        with open("tests/data/test_data.records.json", "r") as f:
            data = json.load(f)

        # Replace instrument
        #!!!! WILL FAIL IF NOT EXACTLY ALIGNED !!!!!
        binary = data["data"]
        binary[4:8] = new_id_bytes
        # binary[60:64] = new_id_bytes

        # Create records
        create_records(binary)

        # Test
        params = RetrieveParams(
            ["AAPL"],
            "2023-11-01",
            "2023-11-30",
            "mbp-1",
        )
        response = self.client.get_records(params)

        # Validate
        records = response.decode_to_array()
        self.assertTrue(len(records) > 0)

        # Cleanup
        delete_instruments(id)

    def test_read_file(self):
        file_path = "tests/data/ohlcv_1m.bin"
        # Test
        data = BufferStore.from_file(file_path)
        df = data.decode_to_df(pretty_ts=True, pretty_px=False)

        # Validate
        self.assertTrue(len(df) > 0)


if __name__ == "__main__":
    unittest.main()
