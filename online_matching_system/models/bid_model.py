import abc
from flask import session
import requests
from datetime import datetime
from decouple import config

api_key = config('FIT3077_API')
root_url = 'https://fit3077.com/api/v2/'


class BidModel(object):

    __metaclass__ = abc.ABCMeta

    def __init__(self):
        self.bid_list = []

    @abc.abstractmethod
    def get_bid_list():
        pass

    
    def get_bid_details(self, bid_id):

        for bid in self.bid_list:
            if bid["id"] == bid_id:
                return bid
        
        return None


class OpenBid(BidModel):

    def get_bid_list(self):

        open_bid_list = []

        result = requests.get(
            url=root_url + '/{}'.format("bid"),
            headers={ 'Authorization': api_key },
            params={'fields': 'messages'}, 
        )

        bid_list = result.json()
        
        for bid in bid_list:
            if bid['type'].lower() == 'open':
                open_bid_list.append(bid)

        self.bid_list = open_bid_list


class CloseBid(BidModel):

    def get_bid_list(self):

        close_bid_list = []

        result = requests.get(
            url=root_url + '/{}'.format("bid"),
            headers={ 'Authorization': api_key },
            params={'fields': 'messages'}, 
        )

        bid_list = result.json()
        
        for bid in bid_list:
            if bid['type'].lower() == 'close':
                close_bid_list.append(bid)

        self.bid_list = close_bid_list

open_bids = OpenBid()
open_bids.get_bid_list()
close_bids = CloseBid()
close_bids.get_bid_list()

def search_bids(bid_id):

    # update bid list before search
    open_bids.get_bid_list()
    close_bids.get_bid_list()

    bid_list = open_bids.bid_list + close_bids.bid_list

    for bid in bid_list:
        if bid['id'] == bid_id:
            return bid

    raise Exception("No bid with this bid id.")
