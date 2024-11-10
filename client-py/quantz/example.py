from collections import defaultdict
from typing import List, Union
import betterproto
from market import (
    ActAs,
    ActingAs,
    TradingClient, 
    Side, 
    Market, 
    Portfolio,
    State,
    ClientMessage,
    CreateOrder,
    Order,
)
from mapping import market_by_name, bot_by_name, users_by_id
from config import API_URL, JWT, ACT_AS, config

def act_as(client: TradingClient, user_id: str):
    msg = ClientMessage(act_as=ActAs(user_id=user_id))
    response = client.request(msg)
    _, message = betterproto.which_one_of(response, "message")
    return response, message

def act_as_by_name(client: TradingClient, name: str):
    return act_as(client, bot_by_name(client.state())[name].id)

def positions_by_user(client: TradingClient, market_name: str):
    market = market_by_name(client.state())[market_name]
    positions = defaultdict(float)
    for trade in market.trades:
        buyer = users_by_id(client.state())[trade.buyer_id].name
        seller = users_by_id(client.state())[trade.seller_id].name
        positions[buyer] += trade.size
        positions[seller] -= trade.size
    return positions

if __name__ == "__main__":
    client = TradingClient(API_URL, JWT, ACT_AS)
    state = client.state()
    message = act_as(client, config['accounts']['lok'])
    print(message)