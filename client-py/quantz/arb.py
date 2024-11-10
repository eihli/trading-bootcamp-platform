from collections import defaultdict
import time
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

class Arbval:
    def __init__(self, value: float, side: Side):
        self.value = value
        self.side = side
    def __repr__(self):
        return f"{self.value}"
    def market(self):
        pass
    def orders(self):
        pass
    def bids(self):
        pass
    def offers(self):
        pass
    def best_price(self):
        return self.value
    def best_bid(self):
        pass
    def best_offer(self):
        pass
    def execute(self, size: float):
        pass
    @property
    def opposite_side(self):
        return Side.BID if self.side == Side.OFFER else Side.OFFER
    def __neg__(self):
        return Arbval(-self.value, self.opposite_side)

class Arbmark:
    def __init__(self, client: TradingClient, name: str, side: Side):
        self.client = client
        self.name = name
        self.side = side
    
    def __repr__(self):
        return f"{'BID' if self.side == Side.BID else 'ASK'} {self.name} {self.best_price()}"

    def market(self):
        return market_by_name(self.client.state())[self.name]

    def orders(self):
        return self.market().orders
    
    def bids(self):
        return [order for order in self.orders() if order.side == Side.BID]
    
    def offers(self):
        return [order for order in self.orders() if order.side == Side.OFFER]
    
    def best_price(self):
        if self.side == Side.BID:
            return self.best_bid().price
        return -self.best_offer().price
    
    def best_bid(self):
        bids = self.bids()
        if bids:
            return sorted(bids, key=lambda x: -x.price)[0]
        return None

    def best_offer(self):
        offers = self.offers()
        if offers:
            return sorted(offers, key=lambda x: x.price)[0]
        return None
    
    def create_order(self, size: float):
        return CreateOrder(
            market_id=self.market().id,
            price=self.best_price(),
            size=size,
            side=self.side,
        )

    def execute(self, size: float):
        return self.client.create_order(self.market().id, self.best_price(), size, self.side)
    
    @property
    def opposite_side(self):
        return Side.BID if self.side == Side.OFFER else Side.OFFER

    def __neg__(self):
        return Arbmark(
            self.client,
            f'{self.name}',
            self.opposite_side,
            self.composition,
        )

class Arbsket:
    def __init__(self, composition: List[Arbmark]):
        self.composition = composition
    
    def cost(self):
        return sum([arbmark.best_price() for arbmark in self.composition])
    
    def value(self):
        return sum([mark.value() for mark in self.composition])

class MockState:
    def __init__(self, markets: Dict[str, Market]):
        self.markets = markets

class MockClient:
    def __init__(self, state: MockState):
        self.state = state
def demo_arb(client: TradingClient):
    ricki_time = Arbmark(client, 'ricki_time', Side.OFFER)
    david_time = Arbmark(client, 'david_time', Side.OFFER)
    sum = Arbmark(client, 'sum', Side.BID)
    left_side = Arbsket([ricki_time, david_time])
    right_side = Arbsket([sum])
    if left_side.best_price() < right_side.best_price():
        left_side.execute()
        right_side.execute()
    if -right_side.cost() < -left_side.value():
        -right_side.execute()
        -left_side.execute()
    
    shift = Arbval(30, Side.BID)
    diff = Arbmark(client, 'diff', Side.BID)
    left_side = Arbsket([ricki_time, david_time])
    right_side = Arbsket([diff, shift])




bid_markets = [
    'pricing_3_a',
    'pricing_3_b',
    'pricing_3_c',
    'pricing_3_d',
]
offer_markets = [
    'pricing_3_sum',
]

def report_arb(client: TradingClient, bid_markets: List[str], offer_markets: List[str]):
    bid_prices = []
    for bid_market in bid_markets:
        bids = [
            order for order in market_by_name(client.state())['pricing_3_a'].orders 
            if order.side == Side.BID
        ]
        bid_prices.append(sorted(bids, key=lambda x: -x.price)[0].price)
    offer_prices = []
    for offer_market in offer_markets:
        offers = [
            order for order in market_by_name(client.state())[offer_market].orders 
            if order.side == Side.OFFER
        ]
        offer_prices.append(sorted(offers, key=lambda x: x.price)[0].price)
    if sum(bid_prices) > sum(offer_prices):
        print(f"Can buy a, b, c, and d for {sum(bid_prices)} and sell for {sum(offer_prices)}")
        print(f"Go?")
        response = input()
        if response.lower() != 'y':
            return
        execute(client, bid_markets, offer_markets)
    else:
        print(f"Can't buy a, b, c, and d for {sum(bid_prices)} and sell for {sum(offer_prices)}")

def execute(client: TradingClient, orders: List[Order]):
    bid_prices = []
    for bid_market in bid_markets:
        bids = [
            order for order in market_by_name(client.state())['pricing_3_a'].orders 
            if order.side == Side.BID
        ]
        bid_prices.append(sorted(bids, key=lambda x: -x.price)[0].price)
    offer_prices = []
    for offer_market in offer_markets:
        offers = [
            order for order in market_by_name(client.state())[offer_market].orders 
            if order.side == Side.OFFER
        ]
        offer_prices.append(sorted(offers, key=lambda x: x.price)[0].price)
    orders_created = []
    max_possible_trade = 1/4 * orders[-1].size
    max_possible_left_hand_side = [1/4 * order.size for order in orders[:-1]]
    size = min(max_possible_left_hand_side + [max_possible_trade])
    if sum(bid_prices) > sum(offer_prices):
        for order in orders:
            order_created = client.create_order(
                order.market_id,
                order.price,
                size,
                order.side
            )
            orders_created.append(order_created)
        print(f"Created:")
        for order in orders_created:
            print(f"  {order.id}")
        time.sleep(0.2)
        for order in orders:
            client.cancel_order(order.id)
    else:
        print(f"Can't buy a, b, c, and d for {sum(bid_prices)} and sell for {sum(offer_prices)}")

if __name__ == "__main__":
    client = TradingClient(API_URL, JWT, ACT_AS)
    act_as_by_name(client, 'Goofy')
    while True:
        report_arb(client, bid_markets, offer_markets)
        time.sleep(1)
