import betterproto
from market import TradingClient, ClientMessage, State

def users_by_id(state: State):
    return {
        user.id: user
        for user in state.users
    }

def bot_by_name(state: State):
    ownership_ids = [ownership.of_bot_id for ownership in state.ownerships]
    owned_bots = [
        user for user in state.users
        if user.id in ownership_ids and user.is_bot
    ]
    return {
        bot.name[4:]: bot
        for bot in owned_bots
    }

def market_by_name(state: State):
    return {
        market.name: market
        for market in state.markets.values()
    }
