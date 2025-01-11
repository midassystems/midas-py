import unittest
import os
import requests
from dotenv import load_dotenv
from midas_client import DatabaseClient
import json
from midas_client.historical import RetrieveParams
from mbn import BufferStore
import mbn

# Load url
load_dotenv()

DATABASE_URL = os.getenv("HISTORICAL_URL")

if DATABASE_URL is None:
    raise ValueError("HISTORICAL_URL environment variable is not set")


# Helper methods
def create_instruments(ticker: str, name: str) -> int:
    url = f"{DATABASE_URL}/historical/instruments/create"
    data = {
        "ticker": ticker,
        "name": name,
        "vendor": "databento",
        "stype": "continuous",
        "dataset": "test",
        "last_available": 1,
        "first_available": 0,
        "active": True,
    }

    response = requests.post(url, json=data).json()

    id = response["data"]
    return id


def delete_instruments(id: int) -> None:
    url = f"{DATABASE_URL}/historical/instruments/delete"

    _ = requests.delete(url, json=id).json()


def json_to_mbp1msg(data):
    """
    Converts a dictionary (parsed JSON) into an Mbp1Msg object.
    """
    try:
        levels = [
            mbn.BidAskPair(
                bid_px=level["bid_px"],
                ask_px=level["ask_px"],
                bid_sz=level["bid_sz"],
                ask_sz=level["ask_sz"],
                bid_ct=level["bid_ct"],
                ask_ct=level["ask_ct"],
            )
            for level in data.get(
                "levels", []
            )  # Default to empty list if no levels
        ]
        return mbn.Mbp1Msg(
            instrument_id=data["instrument_id"],
            ts_event=data["ts_event"],
            price=data["price"],
            size=data["size"],
            action=mbn.Action.from_str(data["action"]),
            side=mbn.Side.from_str(data["side"]),
            depth=data["depth"],
            flags=data["flags"],
            ts_recv=data["ts_recv"],
            ts_in_delta=data["ts_in_delta"],
            sequence=data["sequence"],
            discriminator=data["discriminator"],
            levels=levels,  # Default to an empty list if not provided
        )
    except KeyError as e:
        raise ValueError(f"Missing required field in JSON data: {e}")


def create_records(id: int, client: DatabaseClient) -> None:
    # Load binary records
    with open("tests/data/test_data.records.json", "r") as f:
        data = json.load(f)

    msgs = []
    for i in range(0, len(data)):
        msg = json_to_mbp1msg(data[i])
        msg.instrument_id = int(id)
        msgs.append(msg)

    encoder = mbn.PyRecordEncoder()
    encoder.encode_records(msgs)
    binary = encoder.get_encoded_data()

    # Create records
    client.historical.create_records(binary)


class TestClientMethods(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.client = DatabaseClient()

    # @unittest.skip("")
    def test_list_instruments(self):
        # Setup
        id = create_instruments("AAPL8", "Apple Inc.")

        # Test
        response = self.client.historical.list_instruments()

        # Validate
        self.assertEqual(response["code"], 200)

        # Cleanup
        delete_instruments(id)

    def test_get_records(self):
        # Setup
        id = create_instruments("AAPL", "Apple Inc.")

        # Create Records
        create_records(id, self.client)

        # Test
        params = RetrieveParams(
            ["AAPL"],
            "2023-11-01",
            "2024-11-30",
            "mbp-1",
        )
        response = self.client.historical.get_records(params)

        # Validate
        records = response.decode_to_array()
        self.assertTrue(len(records) > 0)

        # Cleanup
        delete_instruments(id)

    def test_read_mbp_file(self):
        file_path = "tests/data/mbp-1.bin"
        id = create_instruments("AAPL", "Apple Inc.")

        # Create Records
        create_records(id, self.client)

        # Get Recrods to file
        params = RetrieveParams(
            ["AAPL"],
            "2023-11-01",
            "2024-11-30",
            "mbp-1",
        )
        response = self.client.historical.get_records(params)
        response.write_to_file(file_path)

        # Test
        data = BufferStore.from_file(file_path)
        df = data.decode_to_df(pretty_ts=True, pretty_px=False)

        # Validate
        self.assertTrue(len(df) > 0)

        # Cleanup
        delete_instruments(id)

    def test_read_ohlcv_file(self):
        file_path = "tests/data/ohlcv.bin"
        id = create_instruments("AAPL", "Apple Inc.")

        # Create Records
        create_records(id, self.client)

        # Get Recrods to file
        params = RetrieveParams(
            ["AAPL"],
            "2023-11-01",
            "2024-11-30",
            "ohlcv-1d",
        )
        response = self.client.historical.get_records(params)
        response.write_to_file(file_path)

        # Test
        data = BufferStore.from_file(file_path)
        df = data.decode_to_df(pretty_ts=True, pretty_px=False)

        # Validate
        self.assertTrue(len(df) > 0)

        # Cleanup
        delete_instruments(id)

    def test_read_trade_file(self):
        file_path = "tests/data/trade.bin"
        id = create_instruments("AAPL", "Apple Inc.")

        # Create Records
        create_records(id, self.client)

        # Get Recrods to file
        params = RetrieveParams(
            ["AAPL"],
            "2023-11-01",
            "2024-11-30",
            "trade",
        )
        response = self.client.historical.get_records(params)
        response.write_to_file(file_path)

        # Test
        data = BufferStore.from_file(file_path)
        df = data.decode_to_df(pretty_ts=True, pretty_px=False)

        # Validate
        self.assertTrue(len(df) > 0)

        # Cleanup
        delete_instruments(id)

    def test_read_tbbo_file(self):
        file_path = "tests/data/tbbo.bin"
        id = create_instruments("AAPL", "Apple Inc.")

        # Create Records
        create_records(id, self.client)

        # Get Recrods to file
        params = RetrieveParams(
            ["AAPL"],
            "2023-11-01",
            "2024-11-30",
            "tbbo",
        )
        response = self.client.historical.get_records(params)
        response.write_to_file(file_path)

        # Test
        data = BufferStore.from_file(file_path)
        df = data.decode_to_df(pretty_ts=True, pretty_px=False)

        # Validate
        self.assertTrue(len(df) > 0)

        # Cleanup
        delete_instruments(id)

    def test_read_bbo_file(self):
        file_path = "tests/data/bbo.bin"
        id = create_instruments("AAPL", "Apple Inc.")

        # Create Records
        create_records(id, self.client)

        # Get Recrods to file
        params = RetrieveParams(
            ["AAPL"],
            "2023-11-01",
            "2024-11-30",
            "bbo-1m",
        )
        response = self.client.historical.get_records(params)
        response.write_to_file(file_path)

        # Test
        data = BufferStore.from_file(file_path)
        df = data.decode_to_df(pretty_ts=True, pretty_px=False)

        # Validate
        self.assertTrue(len(df) > 0)

        # Cleanup
        delete_instruments(id)


if __name__ == "__main__":
    unittest.main()
