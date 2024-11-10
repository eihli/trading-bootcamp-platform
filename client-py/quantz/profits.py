from arb import Arbmark, Arbsket, Arbval, calculate_size
from market import TradingClient, Side, Market, Order, ClientMessage, Portfolio, Trade
from config import API_URL, JWT, ACT_AS
from typing import List
from utils import act_as_by_name
import argparse

def group_by_market(portfolio: Portfolio):
    return {m.id: m for m in portfolio.market_exposures}

def market_by_name(client: TradingClient, name: str):
    return next(m for m in client.state().markets.values() if m.name == name)

def user_by_name(client: TradingClient, username: str):
    return next(u for u in client.state().users if u.name == username)

def trades_by_user(client: TradingClient, market: Market, username: str):
    user = user_by_name(client, username)
    market = market_by_name(client, market)
    trades = [t for t in market.trades if t.buyer_id == user.id or t.seller_id == user.id]
    return trades

def foo():
    my_trades = [trade for trade in market.trades if trade.seller_id == user_by_name(client, 'Eric Ihli').id]
    sells = sum(trade.size * trade.price for trade in my_trades)
    last_trade = market.trades[-1]
    print(sells - last_trade.price)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Watch market trades and profits for a user')
    parser.add_argument('market', help='Name of market to watch')
    parser.add_argument('username', help='Name of user to watch')
    args = parser.parse_args()

    client = TradingClient(API_URL, JWT, ACT_AS)
    market = market_by_name(client, market)
    trades = trades_by_user(client, market, username)
    print(f"Watching trades for user {args.username} in market {args.market}")
    print(f"Found {len(trades)} trades")
    for trade in trades:
        print(trade)
