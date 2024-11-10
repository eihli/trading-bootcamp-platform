from unittest.mock import Mock, MagicMock
from dataclasses import dataclass, field
from typing import Dict, List

from arb import Arbmark, Arbsket, Arbval
from market import TradingClient, Side, Market, Order

def create_mock_client():
    """Creates a mock TradingClient that returns specified markets in its state"""
    mock_client = MagicMock()
    
    # Create mock state with markets dict
    mock_state = MagicMock()
    ricki_time = MagicMock()
    ricki_time.name = 'ricki_time'
    david_time = MagicMock()
    david_time.name = 'david_time'
    sum = MagicMock()
    sum.name = 'sum'
    diff = MagicMock()
    diff.name = 'diff'
    mock_markets = {
        'ricki_time': ricki_time,
        'david_time': david_time,
        'sum': sum,
        'diff': diff,
    }
    mock_state.markets = mock_markets
    mock_client.state.return_value = mock_state
    return mock_client

def create_mock_client_with_sum_arb():
    """Creates a mock TradingClient that returns specified markets in its state"""
    mock_client = MagicMock()
    
    # Create mock state with markets dict
    mock_state = MagicMock()
    ricki_time = Arbmark(mock_client, 'ricki_time', Side.OFFER)
    ricki_time.name = 'ricki_time'
    ricki_time.id = 1
    ricki_time_bid_order = Order(market_id=ricki_time.id, side=Side.BID, price=8, size=1)
    ricki_time_ask_order = Order(market_id=ricki_time.id, side=Side.OFFER, price=10, size=1)
    ricki_time.orders = MagicMock(return_value=[ricki_time_bid_order, ricki_time_ask_order])

    david_time = Arbmark(mock_client, 'david_time', Side.OFFER)
    david_time.name = 'david_time'
    david_time.id = 2
    david_time_bid_order = Order(market_id=david_time.id, side=Side.BID, price=18, size=1)
    david_time_ask_order = Order(market_id=david_time.id, side=Side.OFFER, price=20, size=1)
    david_time.orders = MagicMock(return_value=[david_time_bid_order, david_time_ask_order])

    sum = MagicMock()
    sum.name = 'sum'
    sum.id = 3
    sum_bid_order = Order(market_id=sum.id, side=Side.BID, price=32, size=1)
    sum_ask_order = Order(market_id=sum.id, side=Side.OFFER, price=34, size=1)
    sum.orders = MagicMock(return_value=[sum_bid_order, sum_ask_order])

    mock_markets = {
        'ricki_time': ricki_time,
        'david_time': david_time,
        'sum': sum,
    }
    mock_state.markets = mock_markets
    mock_client.state.return_value = mock_state
    return mock_client

def test_arb():
    client = create_mock_client_with_sum_arb()

    ricki_time = Arbmark(client, 'ricki_time', Side.OFFER)
    david_time = Arbmark(client, 'david_time', Side.OFFER)
    sum = Arbmark(client, 'sum', Side.BID)

    left_side = Arbsket([ricki_time, david_time])
    right_side = Arbsket([sum])

    orders = []
    if left_side.best_price() < right_side.best_price():
        orders.append(left_side.create_order())
        orders.append(right_side.create_order())

    print(orders)
    
    orders = []
    if -right_side.best_price() < -left_side.best_price():
        orders.append(-right_side.create_order())
        orders.append(-left_side.create_order())
    
    print(orders)

    shift = Arbval(30, Side.BID)
    diff = Arbmark(client, 'diff', Side.BID)
    left_side = Arbsket([ricki_time, david_time])
    right_side = Arbsket([diff, shift])

if __name__ == "__main__":
    test_arb()