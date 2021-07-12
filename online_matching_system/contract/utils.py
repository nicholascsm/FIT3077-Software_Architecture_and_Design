from datetime import datetime, timedelta
from decouple import config
import requests
from online_matching_system.models.bid_model import search_bids
from online_matching_system.models.contract_model import contract as contract_obj
from online_matching_system.users.utils import get_user_role

api_key = config('FIT3077_API')

root_url = 'https://fit3077.com/api/v2'
bid_url = root_url + "/bid"
contract_url = root_url + "/contract"

def get_contract_details(contract_id):
    """
    params: contract_id: a contract ID string 
    to get the specific contract details from API
    return a JSON format of contract details
    """

    contract_details_url = contract_url + "/{}".format(contract_id)

    contract_details = requests.get(
        url=contract_details_url,
        headers={ 'Authorization': api_key },
    ).json()

    return contract_details

def generate_contract(bid_id):
    """
    params: bid_id: a bid ID string
    to generate a contract based on the bid_id given. The contract details will be obtained from the bid_id. An additionalInfo will be added to indicate first and second party sign date
    return: the response of POST request to the API
    """

    bid_details_url = bid_url + "/{}".format(bid_id)
    # bid_details = requests.get(
    #     url=bid_details_url,
    #     headers={ 'Authorization': api_key },
    #     params={'fields':'messages'}
    # ).json()

    bid_details = search_bids(bid_id)

    requestor_id = bid_details['initiator']['id']
    subject_id = bid_details['subject']['id']

    if bid_details['type'] == 'Open':
        if not bid_details['additionalInfo']['bidderRequest']:
            print("There are no offer in this bid. No contract will be generated.")
            return None

        # loop and find the bidder that wins the bid
        for bidder in bid_details['additionalInfo']['bidderRequest']:
            if bidder['bid_chosen']:
                bidder_id = bidder['bidderId']
                number_of_lesson = bidder['numberOfLessonOffered']
                hours_per_lesson = bidder['hoursPerLessonOffered']
                lesson_time = bidder['preferredTimeOffered']
                lesson_day = bidder['preferredDayOffered']
                lesson_per_week = bidder['sessionPerWeekOffered']
                free_lesson = bidder['freeLesson']
                lesson_rate_choice = bidder['rateChoiceOffered']
                lesson_rate = bidder['rateRequest']

    if bid_details['type'] == 'Close':
        if len(bid_details['messages']) == 0:
            print("There are no offer in this bid. No contract will be generated.")
            return None

        for bids in bid_details['messages']:
            if bids['additionalInfo']['bid_chosen']:
                bidder_id = bids['poster']['id']
                number_of_lesson = bids['additionalInfo']['lessonNeeded']
                hours_per_lesson = bids['additionalInfo']['preferredHours']
                lesson_time = bids['additionalInfo']['preferredTime']
                lesson_day = bids['additionalInfo']['preferredDay']
                lesson_per_week = bids['additionalInfo']['preferredSessionPerWeek']
                free_lesson = bids['additionalInfo']['freeLesson']
                lesson_rate_choice = bids['additionalInfo']['preferredRateChoice']
                lesson_rate = bids['additionalInfo']['preferredRate']
                break

    # default contract will be set to 6 months
    contract_json = {
        "firstPartyId": requestor_id,
        "secondPartyId": bidder_id,
        "subjectId": subject_id,
        "dateCreated": str(datetime.now()),
        "expiryDate": str(datetime.now() + timedelta(seconds=15780000)),
        "paymentInfo": {},
        "lessonInfo": {
            "bidderId":bidder_id,
            "numberOfLesson":number_of_lesson,
            "hoursPerLesson":hours_per_lesson,
            "lessonTime":lesson_time,
            "lessonDay":lesson_day,
            "lessonPerWeek":lesson_per_week,
            "freeLesson":free_lesson,
            "lessonRateChoice":lesson_rate_choice,
            "lessonRate":lesson_rate,
        },
        "additionalInfo": {
            "signInfo":{
                "firstPartySignedDate": None,
                "secondPartySignedDate": None,
            },
            'duration': None,
        }
    }

    post_contract = requests.post(
        url = contract_url,
        headers={ 'Authorization': api_key },
        json = contract_json
    ).json()

    return post_contract

###################################################################
## Moved to users/utils.py to eliminate code smell
###################################################################

# def check_contract_expire_soon():

#     contract_expire_soon_list = []
#     contract_expired_list = []

#     # get user contract
#     # refactoring techniques: replace temp with query
#     user_role = get_user_role()
#     contract_list = user_role.user_contracts

#     for contract in contract_list:
#         if contract['dateSigned'] and not contract['terminationDate']:

#             # get expiry date and current date
#             expiry_date = datetime.strptime(contract['expiryDate'][:19], "%Y-%m-%dT%H:%M:%S")
#             current_time = datetime.now()
            
#             # get the diffenrence between expiry date and current date
#             difference = expiry_date - current_time
#             days = divmod(difference.days, 86400)

#             # Refactoring techniques: composing method
#             contract_expire_soon = (days[1] <= 31) and (days[1] > 0)
#             contract_expired = days[0] < 0

#             if contract_expire_soon:
#                 contract_expire_soon_list.append(contract)
#             if contract_expired:
#                 contract_expired_list.append(contract)
    
#     # return True if there's elem in any list, else False
#     if len(contract_expire_soon_list) >= 1 or len(contract_expired_list) >= 1:
#         return True, contract_expire_soon_list, contract_expired_list
#     else:
#         return False, contract_expire_soon_list, contract_expired_list
