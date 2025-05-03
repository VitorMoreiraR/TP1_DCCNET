import unittest
from itertools import chain, repeat
from unittest.mock import MagicMock
from dccnet.autentication import make_autentication
from dccnet.manipulation_frame import create_data_frame
from dccnet.constants import FLAG_ACK, FLAG_GENERIC_DATA


class TestTransmissionErrors(unittest.TestCase):
    def setUp(self):
        self.client = MagicMock()
        self.valid_data = b"GAS TEST\n"
        self.valid_frame = create_data_frame(self.valid_data, FLAG_ACK)

    def simulate_corrupted_frame(self, frame):
        corrupted = bytearray(frame)
        corrupted[10] ^= 0xFF
        return bytes(corrupted)

    def test_autentication_with_corrupted_ack(self):
        self.client.send = MagicMock()

        corrupted_ack = self.simulate_corrupted_frame(
            create_data_frame(b"ACK", FLAG_ACK)
        )
        valid_auth_msg = create_data_frame(
            "Autenticacao completa\n".encode("ascii"), 0, FLAG_GENERIC_DATA
        )

        self.client.recv = MagicMock(
            side_effect=chain([corrupted_ack, valid_auth_msg], repeat(valid_auth_msg))
        )

        make_autentication(self.valid_data, self.client)

        self.assertTrue(self.client.send.call_count >= 2)


if __name__ == "__main__":
    unittest.main()
