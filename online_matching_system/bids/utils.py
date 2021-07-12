from decouple import config
import requests
from datetime import datetime
from online_matching_system.contract.utils import generate_contract
from online_matching_system.users.utils import users_url, get_user_role
from online_matching_system.models.user_model import student, tutor
from online_matching_system.models.bid_model import open_bids, close_bids

api_key = config('FIT3077_API')

root_url = 'https://fit3077.com/api/v2'
bid_url = root_url + "/bid"
contract_url = root_url + "/contract"


def search_bids(bid_id):

    # update bid list before search
    open_bids.get_bid_list()
    close_bids.get_bid_list()

    bid_list = open_bids.bid_list + close_bids.bid_list

    for bid in bid_list:
        if bid['id'] == bid_id:
            return bid

    raise Exception("No bid with this bid id.")


def all_bids():

    # update bid list before return all bids
    open_bids.get_bid_list()
    close_bids.get_bid_list()

    return open_bids.bid_list + close_bids.bid_list


def get_bid_type(bid_info):

    bid_json = bid_info.json()
    print(bid_json)

    if bid_json['type'].lower() == 'open':
        return open_bids
    elif bid_json['type'].lower() == 'close':
        return close_bids
    
    raise Exception("Bid is neither open or close bid.")


def close_bid(bid_id):
    """
    Function to close a bid
    """
    close_bid_url = bid_url + '/{}/close-down'.format(bid_id)

    print("The bid being closed down"+str(bid_id))
    print("The bid url:"+str(close_bid_url))

    response = requests.post(
        url=close_bid_url,
        headers={ 'Authorization': api_key },
        data = {
            "dateClosedDown": datetime.now()
        }
    )

    open_bids.get_bid_list()
    close_bids.get_bid_list()

    generate_contract(bid_id)

    return response.status_code


def get_bid_details(bid_id):
    """
    Function to get a bid's details using the bid_id
    """

    target_bid = search_bids(bid_id)

    bid_type = target_bid['type'].lower()
    bid_date_created = target_bid['dateCreated']
    bid_date_closed_down = target_bid['dateClosedDown']
    bid_subject = target_bid['subject']['name']
    initiator_bid = target_bid['additionalInfo']['initiatorBid']
    bidder_request = target_bid['additionalInfo']['bidderRequest']
    messages = target_bid['messages']

    return {'bid_type':bid_type, 'bid_date_created':bid_date_created, 'bid_date_closed_down':bid_date_closed_down,
            'bid_subject':bid_subject, 'initiator_bid':initiator_bid, 'bidder_request':bidder_request, 'messages':messages}


def check_valid_offer(bid_info, bidder_id):
    """
    to check if the user submit the offer more than once
    and also to check if the user has the competencies to offer/buy out a bid
    """
    user_has_competencies = False
    first_bid = True
    bidder_level = ''
    initiator_level = ''

    # to check if the user has bidded the bid before
    bidder_requests = bid_info['additionalInfo']['bidderRequest']

    for bid_request in bidder_requests:
        if bid_request['bidderId'] == bidder_id:
            first_bid = False

    # to check if the user has the competencies to bid
    # refactoring techniques: replace temp with query
    user_role = get_user_role()

    user_competencies = user_role.user_competencies

    for competency in user_competencies:
        if competency["subject"]["id"] == bid_info["subject"]["id"]:
            bidder_level = competency['level']
            user_has_competencies = True

    # check if bidder's competencies is two level higher than requestor competencies
    # get initiator's competencies
    initiator_id = bid_info['initiator']['id']

    # fetch initiator's details to get initiator's competencies
    initiator_user_url = root_url + "/user/{}".format(initiator_id)

    response = requests.get(
        url=initiator_user_url,
        headers={ 'Authorization': api_key },
        params={
            'fields':'competencies.subject'
        }
    ).json()

    # initiator's competencies
    initiator_competencies = response['competencies']
    for competency in initiator_competencies:
        if competency['subject']['id'] == bid_info['subject']['id']:
            initiator_level = competency['level']

    # check the level
    if bidder_level and initiator_level:
        enough_level = (bidder_level - initiator_level) >= 2
    else:
        enough_level = False

    return (user_has_competencies and first_bid and enough_level)


def filter_ongoing_bids(bid_list):
    """
    check the field of dateClosedDown to determine if the bid is closed down
    :return - a list of JSON
    """

    result = []

    for bid in bid_list:
        if not bid['dateClosedDown']:
            result.append(bid)

    return result


def check_bid_status(bid_id):
    """
    check if there's any bidder offer their bid, if yes, choose the last bidder, if no, close the bid
    """

    bid_details_url = bid_url + "/{}".format(bid_id)

    response = search_bids(bid_id)

    addtional_info = response['additionalInfo']

    if addtional_info['bidderRequest']:
        addtional_info['bidderRequest'][-1]['bid_chosen'] = True

        return_value = {'additionalInfo': addtional_info}

        response = requests.patch(
            url=bid_details_url,
            headers={ 'Authorization': api_key },
            json = return_value,
        ).json()

        # TODO: log this information
        # if response.status_code != 200:
        #     print(status)


def check_contract():

    user_contract = 0

    contracts = requests.get(
        url=contract_url,
        headers={ 'Authorization': api_key },
    ).json()

    # Refactoring techniques: composing method
    for contract in contracts:
        first_party_contract = contract['firstParty'] == session['user_id']
        second_party_contract = contract['secondParty'] == session['user_id']
        contract_not_expired = datetime.now() < contract['expiryDate']

        if (first_party_contract) & (contract_not_expired):
            user_contract += 1
        elif (second_party_contract) & (contract_not_expired):
            user_contract += 1

    return user_contract < 5
