from abc import ABCMeta
from flask import session
import requests
from datetime import datetime
from decouple import config

api_key = config('FIT3077_API')
root_url = 'https://fit3077.com/api/v2/'

class ContractModel():

    def __init__(self):
        self.contract_list = []

    def get_contract_list(self):

        self.update_contract_list()

        return self.contract_list

    def update_contract_list(self):
        """
        update the contract_list 
        """
        
        result = requests.get(
            url = root_url + '/{}'.format("contract"),
            headers = { 'Authorization': api_key },
        )

        contract_list = result.json()

        self.contract_list = contract_list

    def get_contract_details(self, contract_id):
        """
        get the specific contract by looping the contract_list

        Args:
            contract_id (string): a type string of contract id

        Raises:
            Exception: if there's no contract found

        Returns:
            [contract class object]: the specific contract that is required
        """

        self.update_contract_list()

        for contract in self.contract_list:
            if contract['id'] == contract_id:
                return contract
        
        raise Exception('No contract with this contract id')

contract = ContractModel()
