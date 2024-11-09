from collections import defaultdict
from typing import List
import betterproto
from market import (
    ActAs,
    ActingAs,
    TradingClient, 
    Side, 
    Market, 
    Portfolio,
    State,
    ClientMessage
)
from mapping import market_by_name, bot_by_name, users_by_id
from config import API_URL, JWT, ACT_AS, config

# If a "correlation" is defined as::
# (market_a, market_b, 1.0)
# Which means that as market_a goes up by 1, market_b goes up by 1.
# (market_a, market_b, -0.8) means that as market_a goes up by 1,
# market_by goes up by -0.8.
#
# Is that all you need to be able to find arbitrage opportunities?
#
# (ricki_time, david_time, 0.0)
# (ricki_time, sum,   1.0)
# (david_time, sum,   1.0)
# (ricki_time, diff,  1.0 + 30)
# (david_time, diff, -1.0 + 30)
#
# Aside: What would a more complex function, other than sum,
# look like? What would be an example of a nonlinear combination
# of contracts?
#
# Algorithm:
# Find everything that is correlated with `sum`.
# In this case, ricki_time and david_time.
# 
# Find every combination of assets that results in 
# a flat contract-space.
# 
# ricki_time * its correlation
# + david_time * its correlation
# == sum
#
# If you can buy one for less than you can sell the other,
# you have an arbitrage.
#
# In other words:
# If the offer for one is less than the bid for the other,
# you have an arbitrage.

class Var:
    def __init__(self, client: TradingClient, markets: List[Market], side: Side):
        self.client = client
        self._markets = markets
        self.side = side
    
    def __repr__(self):
        side = "bid" if self.side == Side.BID else "offer"
        return f"{self.market.name} {side}"
    
    @property
    def market(self):
        return self.client.state().markets[self._market.id]
    
    def order(self):
        if self.side == Side.BID:
            bids = [order for order in self.market.orders if order.side == Side.BID]
            best_bid = sorted(bids, key=lambda x: -x.price)[0]
            return best_bid
        else:
            offers = [order for order in self.market.orders if order.side == Side.OFFER]
            best_offer = sorted(offers, key=lambda x: x.price)[0]
            return best_offer
        
    def __lt__(self, other: "Var"):
        if self.side == Side.BID and other.side == Side.BID:
            raise ValueError("Bids cannot be compared")
        elif self.side == Side.OFFER and other.side == Side.OFFER:
            raise ValueError("Offers cannot be compared")
        elif self.side == Side.OFFER and other.side == Side.BID:
            return self.order().price < other.order().price
        else:
            return self.order().price > other.order().price

    def __eq__(self, other: "Var"):
        return self.order().price == other.order().price
    
    def execute(self, size: float):
        order_created = self.client.create_order(
            self._market.id,
            self.order().price,
            size,
            self.side
        )

class Basket:
    def __init__(self, client: TradingClient, vars: List[Var]):
        self.client = client
        self._vars = vars

    def __repr__(self):
        return f"Basket({', '.join(repr(var) for var in self._vars)})"
    
    def __add__(self, other: "Basket"):
        return Basket(self.client, self._vars + other._vars)
    
    def __lt__(self, other: "Basket"):
        return sum(var.order().price for var in self._vars) < sum(var.order().price for var in other._vars)

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
