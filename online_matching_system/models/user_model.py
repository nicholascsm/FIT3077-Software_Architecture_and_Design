from abc import ABCMeta, abstractmethod
from flask import session
import requests
from datetime import datetime
from decouple import config

api_key = config('FIT3077_API')
root_url = 'https://fit3077.com/api/v2/'

class UserModel():
    __metaclass__ = ABCMeta 

    def __init__(self):
        self.user_id = None
        self.initialized = False
        self.user_details = None
        self.user_competencies = None
        self.user_qualifications = None
        self.user_bids = None
        self.user_contracts = []
        self.is_student = None
        self.is_tutor = None

    def __str__(self):
        return "{}, {}".format(self.user_id ,self.initialized)
        
    def get_user_id(self):
        """
        get user id from session
        """

        self.user_id = session.get('user_id',0)

    def get_user_details(self):
        """
        get user's details from API
        format: JSON
        """

        user_id_url = root_url + "/{}/{}".format("user", session['user_id'])

        user_details = requests.get(
            url=user_id_url,
            headers={ 'Authorization': api_key },
        ).json()

        self.user_details = user_details


    def get_user_competencies(self):
        """
        get user's competency from API
        format: a list of JSON 
        """

        user_id_url = root_url + "/{}/{}".format("user", session['user_id'])

        user_competencies = requests.get(
            url=user_id_url,
            headers={ 'Authorization': api_key },
            params={
                'fields':'competencies.subject'
            }
        ).json()
        
        self.user_competencies = user_competencies['competencies']


    def get_user_qualifications(self):
        """
        get user's qualification from API
        format: a list of JSON 
        """

        user_id_url = root_url + "/{}/{}".format("user", session['user_id'])

        user_qualifications = requests.get(
            url=user_id_url,
            headers={ 'Authorization': api_key },
            params={
                'fields':'qualifications'
            }
        ).json()

        self.user_qualifications = user_qualifications['qualifications']

    def get_user_role(self):
        """
        check isStudent and isTutor
        format: boolean
        """

        user_id_url = root_url + "/{}/{}".format("user", session['user_id'])

        user_info = requests.get(
            url=user_id_url,
            headers={ 'Authorization': api_key },
        ).json()

        self.isStudent = user_info['isStudent']
        self.isTutor = user_info['isTutor']

    def get_user_contract(self):
        """
        get user's contract from API
        """
        user_contract_list = []
        contract_url = root_url + "/contract"

        user_contracts = requests.get(
            url=contract_url,
            headers={ 'Authorization': api_key },
        ).json()

        for contract in user_contracts:
            if contract['firstParty']['id'] == session['user_id'] or contract['secondParty']['id'] == session['user_id']:
                user_contract_list.append(contract)
        
        self.user_contracts = user_contract_list

    @abstractmethod
    def get_user_bids(self):
        pass

    def check_initialized(self):

        return self.initialized


class StudentModel(UserModel):

    def __init__(self):
        UserModel.__init__(self)
        self.contract_number = 0

    def get_contract_number(self):
        """
        get the number of contract that a student have
        format: integer
        """

        user_contract = 0

        contracts = requests.get(
            url=root_url + "/{}".format("contract"),
            headers={ 'Authorization': api_key },
        ).json()

        for contract in contracts:
            expiry_date = datetime.strptime(contract['expiryDate'], "%Y-%m-%dT%H:%M:%S.%fZ")
            if (contract['firstParty'] == session['user_id']) & (datetime.now() < expiry_date):
                user_contract += 1
            elif (contract['secondParty'] == session['user_id']) & (datetime.now() < expiry_date):
                user_contract += 1

        self.contract_number = user_contract

    def get_user_bids(self):
        """
        get user's bid from API
        format: a list of JSON
        """

        user_id_url = root_url + "/{}/{}".format("user", session['user_id'])

        user_bids = requests.get(
            url=user_id_url,
            headers={ 'Authorization': api_key },
            params={
                'fields':'initiatedBids'
            }
        ).json()

        self.user_bids = user_bids['initiatedBids']


class TutorModel(UserModel):

    def __init__(self):
        UserModel.__init__(self)
        self.bid_monitor_list = []

    def get_user_bids(self):
        """
        to get the bids that a tutor have bid, fetch all of the bid and loop thru the bidderRequest
        field to check if the tutor has bid on the bid. Append and assign the list to tutor.user_bids
        """

        bid_url = root_url + "/{}".format("bid")

        bids = requests.get(
            url=bid_url,
            headers={ 'Authorization': api_key },
        ).json()

        user_bid = []

        for bid in bids:
            if bid['additionalInfo']:
                bidder_request_list = bid['additionalInfo']['bidderRequest']
                for bidder_request in bidder_request_list:
                    if bidder_request['bidderId'] == session['user_id']:
                        user_bid.append(bid)

        self.user_bids = user_bid


student = StudentModel()
tutor = TutorModel()