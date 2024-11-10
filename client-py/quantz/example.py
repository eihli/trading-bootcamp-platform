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
# (sum <david_time + ricki_time>, )
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
    def __init__(self, client: TradingClient, market: Market, side: Side):
        self.client = client
        self._market = market
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

# (ricki_time + david_time == sum)

# (-ricki_time - david_time + 30 == diff)

class ArbMarket:
    def __init__(self, market: Market, side: Side):
        self.market = market
        self.side = side

class ArbMagic:
    def __init__(self, value: Union[float, ArbMarket], parents: List["ArbMagic"]):
        self._value = value
        self.parents = parents

    def __add__(self, other: "ArbMagic"):
        return ArbMagic(
            self._value + other._value,
            (self, other)
        )
    
    def __sub__(self, other: "ArbMagic"):
        ask = ArbMagic(self.market, Side.OFFER)
        result = ArbMagic()
        result._result = (self, other)

    def __neg__(self):
        if self.side == Side.BID:
            return ArbMagic(self.market, Side.OFFER)
        else:
            return ArbMagic(self.market, Side.BID)
    
    def __eq__(self, other: "ArbMagic"):
        result = ArbMagic(self.value - other.value, parents=(self, other))
        return result
    
    @property
    def value(self):
        if isinstance(self._value, ArbMarket):
            if self.side == Side.BID:   
                return best_bid(self._value.market.orders).price
            else:
                return best_ask(self._value.market.orders).price
        else:
            return self._value
    
    def find_arbs(self):
        pass

def best_bid(orders: List[Order]):
    return sorted(orders, key=lambda x: -x.price)[0]

def best_ask(orders: List[Order]):
    return sorted(orders, key=lambda x: x.price)[0]


def run_bot():
    # example of the arb between ricki_time offer + david_time offer > sum bid
    state = client.state()
    ricki_time_offers = [
        order for order in state.markets['ricki_time'].orders 
        if order.side == Side.OFFER
    ]
    best_ricki_time_offer = sorted(ricki_time_offers, key=lambda x: x.price)[0]
    david_time_offers = [
        order for order in state.markets['david_time'].orders 
        if order.side == Side.OFFER
    ]
    best_david_time_offer = sorted(david_time_offers, key=lambda x: x.price)[0]
    sum_bids = [
        order for order in state.markets['sum'].orders 
        if order.side == Side.BID
    ]
    best_sum_bid = sorted(sum_bids, key=lambda x: -x.price)[0]

    if best_ricki_time_offer.price + best_david_time_offer.price < best_sum_bid.price:
        execute(client, [best_ricki_time_offer, best_david_time_offer, best_sum_bid])


def execute(client: TradingClient, orders: List[ClientMessage]):
    for order in orders:
        client.request(order)

def create_orders_message(orders: List[Var]) -> List[ClientMessage]:
    size = min(order.size for order in orders)
    return [
        ClientMessage(
            create_order=CreateOrder(
                market_id=order.market_id,
                price=order.price,
                size=size,
                side=order.side,
            ),
        )
        for order in orders
    ]

def test_arb():
    ricki_time = Order(
        id=5,
        market_id=42,
        owner_id="test",
        transaction_id=1,
        price=12,
        size=1,
        side=Side.OFFER,
        sizes=[],
    )
    david_time = Order(
        id=6,
        market_id=43,
        owner_id="test",
        transaction_id=1,
        price=20,
        size=2,
        side=Side.OFFER,
        sizes=[],
    )
    sum = Order(
        id=7,
        market_id=44,
        owner_id="test",
        transaction_id=1,
        price=33,
        size=3,
        side=Side.BID,
        sizes=[],
    )
    if ricki_time.price + david_time.price < sum.price:
        orders_to_execute = create_orders_message([ricki_time, david_time, sum])
    assert orders_to_execute[0].create_order.price == ricki_time.price
    assert orders_to_execute[0].create_order.price == 12


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
    test_arb()
