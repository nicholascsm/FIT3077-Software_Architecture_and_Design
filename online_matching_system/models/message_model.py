from abc import ABCMeta
from flask import session
import requests
from datetime import datetime
from decouple import config

api_key = config('FIT3077_API')
root_url = 'https://fit3077.com/api/v2/'

class MessageModel():

    def __init__(self):
        self.message_list = []

    def get_message_list(self):
        """
        get all of the message from API
        """
        
        result = requests.get(
            url = root_url + '/{}'.format("message"),
            headers = { 'Authorization': api_key },
        )

        message_list = result.json()

        self.message_list = message_list

    def get_message_details(self, message_id):
        """
        get the specific message by looping the message_list

        Args:
            message_id (string): a type string of message id

        Raises:
            Exception: if there's no message found

        Returns:
            [message class object]: the specific message that is required
        """

        for message in self.message_list:
            if message['id'] == message_id:
                return message
        
        raise Exception('No message with this message id')

message = MessageModel()
