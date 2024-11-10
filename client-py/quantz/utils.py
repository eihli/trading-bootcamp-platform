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

bots_by_name = {
    'sum_beep_boop': {
        'token': 'eyJhbGciOiJSUzI1NiIsImtpZCI6ImNhOjA0OmZmOjViOjNmOmUwOmUzOjNjOmU2OmUwOjAzOjZiOjIxOmJiOjQ3OjVlIiwidHlwIjoiSldUIn0.eyJhdWQiOlsidHJhZGluZy1zZXJ2ZXItYXBpIl0sImF6cCI6ImE5ODY5YmIxMjI1ODQ4YjlhZDViYWQyYTA0YjcyYjVmIiwiZXhwIjoxNzMxODgzNTY0LCJpYXQiOjE3MzEyNzg3NjMsImlzcyI6Imh0dHBzOi8vY3Jhenl0aWVndXkua2luZGUuY29tIiwianRpIjoiMDNjMTZkMzAtNDNhZS00NWYxLTk4ZmEtNjNiOTgyMThhMDEzIiwib3JnX2NvZGUiOiJvcmdfMWExZDJjMTAxMGYiLCJwZXJtaXNzaW9ucyI6W10sInNjcCI6WyJvcGVuaWQiLCJwcm9maWxlIiwiZW1haWwiLCJvZmZsaW5lIl0sInN1YiI6ImtwXzI2ODQ4ZDYyZTMwZDQzMjg5YzMzZTRlNjI4ODc1OGY5In0.aiBUbNokF3FFaapSuwiIJd48vvLPzHkfLdxUWhzotT8-uI1BU4LVX6k737xy8DotL2m201VgY0355mgWFbOigHj5UikLRaBLxPE1YkNG7S53npdYbtgllQaiY_gvByPcknZgordLRDYagwM3-FVcImAmEKSu4W18YFOOLEsE27W7ZCXeUoMHjB5q0KH-PHZ8BysabJ5RMVwYWwV3g5o9lnxA64dHIGiF3T2v9frRKb10CCJ0pmGan9_v_etnE7uaAwd9DMNNApNGV1Y_WxUty_P3lwcWKVaMHod-FmOH7-9V_9FeFQZP_fB_uEZyL4NtjvdekjQF6Vnk5YRT-MuA9A',
        'id': '2898c877-1896-4d2f-9a21-2addf0539813'
    },
    'diff_beep_boop': {
        'token': 'eyJhbGciOiJSUzI1NiIsImtpZCI6ImNhOjA0OmZmOjViOjNmOmUwOmUzOjNjOmU2OmUwOjAzOjZiOjIxOmJiOjQ3OjVlIiwidHlwIjoiSldUIn0.eyJhdWQiOlsidHJhZGluZy1zZXJ2ZXItYXBpIl0sImF6cCI6ImE5ODY5YmIxMjI1ODQ4YjlhZDViYWQyYTA0YjcyYjVmIiwiZXhwIjoxNzMxODgzNzAxLCJpYXQiOjE3MzEyNzg5MDAsImlzcyI6Imh0dHBzOi8vY3Jhenl0aWVndXkua2luZGUuY29tIiwianRpIjoiNjZlODM4YTQtMmQ5MC00OTA3LTgwODktZTE3MmE1NWUzN2I4Iiwib3JnX2NvZGUiOiJvcmdfMWExZDJjMTAxMGYiLCJwZXJtaXNzaW9ucyI6W10sInNjcCI6WyJvcGVuaWQiLCJwcm9maWxlIiwiZW1haWwiLCJvZmZsaW5lIl0sInN1YiI6ImtwXzI2ODQ4ZDYyZTMwZDQzMjg5YzMzZTRlNjI4ODc1OGY5In0.eLQoMoHJ__5mz0tlhqkdnR3HpfdsFsL9krRk3iX6SZ2wQJMbWF0CU4aHeKpQzUOxhGcuy9HlDStMuZVbd3hLr0h7zoZWnLTkBI6xOjKTK6j5O8JoJWk_rJCG8FXEhATJs0sXA4DL-wnszQNmg4bRAI0kzrMLe7B1avJC4HhpEw-Mee2fRa8S1RTxqjrNwcn2jwrQCfddU93a0zGxUh80lRLrjyYTciG43nY7iWHoVDpamr19S0VugRjYarcSi2GiWL21of--Xyd22qWXlC6HhcEKmkcP2FeYecaOo5V1RMDzt6jBtpDruV5VqVILEeuRUwqi_qIM0ESGwvIvle2dgg',
        'id': 'daa2b70b-fb0b-44d6-81db-05d80aa6e324',
    },
    'Eric': {
        'token': 'eyJhbGciOiJSUzI1NiIsImtpZCI6ImNhOjA0OmZmOjViOjNmOmUwOmUzOjNjOmU2OmUwOjAzOjZiOjIxOmJiOjQ3OjVlIiwidHlwIjoiSldUIn0.eyJhdWQiOlsidHJhZGluZy1zZXJ2ZXItYXBpIl0sImF6cCI6ImE5ODY5YmIxMjI1ODQ4YjlhZDViYWQyYTA0YjcyYjVmIiwiZXhwIjoxNzMxODgzNzI5LCJpYXQiOjE3MzEyNzg5MjgsImlzcyI6Imh0dHBzOi8vY3Jhenl0aWVndXkua2luZGUuY29tIiwianRpIjoiYjlmM2QyMGItZmQxZi00MjA4LTkzNWQtNDQ2N2RkY2ZlMzIwIiwib3JnX2NvZGUiOiJvcmdfMWExZDJjMTAxMGYiLCJwZXJtaXNzaW9ucyI6W10sInNjcCI6WyJvcGVuaWQiLCJwcm9maWxlIiwiZW1haWwiLCJvZmZsaW5lIl0sInN1YiI6ImtwXzI2ODQ4ZDYyZTMwZDQzMjg5YzMzZTRlNjI4ODc1OGY5In0.NH1QHjaOf7l7indjWazLgARxZuxSPo1vZMrrmheCNS69HdvvRpiJ_zNFx_msqExzOZsv8ubLYZhy0MrmTRsJgYQXapm5EcXvrDb6wEVCni87WOtq6__fBnD9eoFSnhW9Khi-Ba7Gep1CC6eSAqjhYhQ8csLznC9odp3oMtjzdJYgCoiGCz0CQbgRyzs_nnYYwIxjs2S-n1trwL6q6bU-G8tNXbtx41QO130yzUcUojqHDO7mwf37SJ5SYcGb3XMEp9kxsxAqLh455pUq0Y8-XSNfflHeYBfF7RADfJVKcFJtYlXlQqbFrJUOmDOOjZc0GJqoekRlxX_EaYs950dPRA',
        'id': 'kp_26848d62e30d43289c33e4e6288758f9',
    },
}

def act_as_by_name(client: TradingClient, name: str):
    return TradingClient(API_URL, bots_by_name[name]['token'], bots_by_name[name]['id'])

def positions_by_user(client: TradingClient, market_name: str):
    market = market_by_name(client.state())[market_name]
    positions = defaultdict(float)
    for trade in market.trades:
        buyer = users_by_id(client.state())[trade.buyer_id].name
        seller = users_by_id(client.state())[trade.seller_id].name
        positions[buyer] += trade.size
        positions[seller] -= trade.size
    return positions