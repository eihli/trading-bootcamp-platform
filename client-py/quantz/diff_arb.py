from arb import Arbmark, Arbsket, Arbval, calculate_size
from do_arb import do_arb, tw_test_diff
from market import TradingClient, Side, Market, Order, ClientMessage
from config import API_URL, JWT, ACT_AS
import time

if __name__ == "__main__":
    while True:
        tw_test_diff()
        time.sleep(1)
