from arb import Arbmark, Arbsket, Arbval, calculate_size
from market import TradingClient, Side, Market, Order, ClientMessage
from config import API_URL, JWT, ACT_AS

def tw_test_sum(dry_run=True):
    client = TradingClient(API_URL, JWT, ACT_AS)
    tw_a_test = Arbmark(client, 'tw_a_test', Side.OFFER)
    tw_b_test = Arbmark(client, 'tw_b_test', Side.OFFER)
    tw_c_test = Arbmark(client, 'tw_c_test', Side.OFFER)
    tw_d_test = Arbmark(client, 'tw_d_test', Side.OFFER)
    tw_sum_test = Arbmark(client, 'tw_sum_test', Side.BID)
    left_side = Arbsket([tw_a_test, tw_b_test, tw_c_test, tw_d_test])
    right_side = Arbsket([tw_sum_test])
    do_arb(client, left_side, right_side, dry_run)

def tw_test_diff(dry_run=True):
    client = TradingClient(API_URL, JWT, ACT_AS)
    tw_a_test = Arbmark(client, 'tw_a_test', Side.OFFER)
    tw_d_test = Arbmark(client, 'tw_d_test', Side.BID)
    tw_diff_test = Arbmark(client, 'tw_diff_test', Side.BID)
    left_side = Arbsket([tw_a_test, tw_d_test])
    right_side = Arbsket([tw_diff_test]) 
    do_arb(client, left_side, right_side, dry_run)

def tw_test_avg(dry_run=True):
    client = TradingClient(API_URL, JWT, ACT_AS)
    tw_avg_test = Arbmark(client, 'tw_avg_test', Side.OFFER)
    tw_sum_test = Arbmark(client, 'tw_sum_test', Side.BID)
    left_side = Arbsket([tw_avg_test, tw_avg_test, tw_avg_test, tw_avg_test])
    right_side = Arbsket([tw_sum_test]) 
    do_arb(client, left_side, right_side, dry_run)

def arb_sum(dry_run=True):
    client = TradingClient(API_URL, JWT, ACT_AS)
    ricki_time = Arbmark(client, 'Jeremy_Eric_Test_1', Side.OFFER)
    david_time = Arbmark(client, 'Jeremy_Eric_Test_2', Side.OFFER)
    sum = Arbmark(client, 'Jeremy_Eric_Test_3', Side.BID)

    left_side = Arbsket([ricki_time, david_time])
    right_side = Arbsket([sum])
    do_arb(client, left_side, right_side, dry_run)

def arb_diff(dry_run=True):
    client = TradingClient(API_URL, JWT, ACT_AS)
    ricki_time = Arbmark(client, 'Jeremy_Eric_Test_1', Side.OFFER)
    david_time = Arbmark(client, 'Jeremy_Eric_Test_2', Side.BID)
    sum = Arbmark(client, 'Jeremy_Eric_Test_4', Side.BID)
    offset = Arbval(100, Side.BID)

    left_side = Arbsket([ricki_time, david_time])
    right_side = Arbsket([sum, offset])
    do_arb(client, left_side, right_side, dry_run)

def do_arb(client, left_side, right_side, dry_run=True):
    orders = []
    if left_side.best_price() < right_side.best_price():
        left, right = calculate_size(left_side, right_side)
        print(left, right)
        orders.extend([a.create_order(left) for a in left_side.composition])
        orders.extend([a.create_order(right) for a in right_side.composition])
    print(orders)
    if not dry_run:
      msgs = []
      for order in orders:
          msgs.append(client.request(ClientMessage(create_order=order)))
      for msg in msgs:
          if msg.order_created.order.id > 0:
              client.request(ClientMessage(cancel_order=msg.order_created.order.d))
      
    orders = []
    if (-right_side).best_price() < (-left_side).best_price():
        left, right = calculate_size(-left_side, -right_side)
        print(left, right)
        orders.extend([a.create_order(left) for a in (-left_side).composition])
        orders.extend([a.create_order(right) for a in (-right_side).composition])
    print(orders)
    if not dry_run:
      msgs = []
      for order in orders:
          msgs.append(client.request(ClientMessage(create_order=order)))
      for msg in msgs:
          if msg.order_created.order.id > 0:
              client.request(ClientMessage(cancel_order=msg.order_created.order.id))

if __name__ == "__main__":
    tw_test_sum()
    arb_diff()
