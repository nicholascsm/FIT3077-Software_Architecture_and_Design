import requests
# from online_matching_system.routes import *
from flask_login import current_user
from flask import session, flash, redirect, render_template, url_for, request
from functools import wraps
from decouple import config
from online_matching_system.models.user_model import student, tutor
from datetime import datetime

root_url = 'https://fit3077.com/api/v2'
users_url = root_url + "/user"
users_login_url = users_url + "/login"
api_key = config('FIT3077_API')


def check_login():

    try:
        if session['user_id']:
            return True
    except KeyError:
        return False


def create_user_model():
    """
    initialized the user model
    format: boolean
    """

    user_id_url = root_url + "/{}/{}".format("user", session['user_id'])

    user_info = requests.get(
        url=user_id_url,
        headers={ 'Authorization': api_key },
    ).json()

    if user_info['isStudent']:
        session['user_role'] = 'student'
        student.get_user_id()
        student.get_user_details()
        student.get_user_bids()
        student.get_user_competencies()
        student.get_user_qualifications()
        student.get_contract_number()
        student.get_user_contract()
        student.initialized = True
    elif user_info['isTutor']:
        session['user_role'] = 'tutor'
        tutor.get_user_id()
        tutor.get_user_details()
        tutor.get_user_bids()
        tutor.get_user_competencies()
        tutor.get_user_qualifications()
        tutor.get_user_contract()
        tutor.initialized = True
    else:
        raise Exception("user is not student and tutor. What is the user role?")

    print(student, tutor)

    return student, tutor


def login_required(f):
    """
    to ask user login first before perform any action
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        try:
            if session['user_id']:
                pass
        except KeyError:
            return redirect(url_for('users.login', next=request.url))
        return f(*args, **kwargs)
    return decorated_function


def check_user_model(f):
    """
    initialized the user model if it is not yet initialized. 
    when Flask restart stat, class data will de reset and data will be lost. Hence, we'll need to check if the user model is initalized already before we perform any action
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if student.check_initialized() or tutor.check_initialized():
            pass
        else:
            create_user_model()
            return redirect(str(request.url))
        return f(*args, **kwargs)
    return decorated_function


def login_user(username, password):
    """
    login the user by POST request by providing username and password

    Args:
        username ([string]): [username that user enter when login]
        password ([string]): [password that user enter when login]

    Returns:
        [Response]: [response return by the API]
    """

    # get response from API
    response = requests.post(
        url=users_login_url,
        headers={ 'Authorization': api_key },
        params={ 'jwt': 'true' }, 
        data={
            'userName': username,
            'password': password
        }
    )

    # if user exist
    if response.status_code == 200:

        # retrieve jwt returned from API
        json_data = response.json()
        jwt = json_data['jwt']

        # retrieve user's id for profile purposes
        users_list = requests.get(
            url=users_url,
            headers={ 'Authorization': api_key },
            params={ 'jwt': 'true' }, 
        ).json()

        # filter the list and find the user
        for user in users_list:
            if user['userName'] == username:
                # store the user's ID in session
                session['user_id'] = user["id"]

        create_user_model()
    
    return response

def logout_manual():
    # clear session keys
    for key in list(session.keys()):
        session.pop(key)

    return None


def verify_token(token):

    result = requests.post(
        url=verify_token_url,
        headers={ 'Authorization': api_key },
        data={
            'jwt': token,
        }
    )

    print('Status code is: {} {}'.format(result.status_code, result.reason))

def decode_jwt(encoded_jwt):

    encoded_jwt = encoded_jwt.split(".")
    message = base64.b64decode(encoded_jwt[1])
    print('message: ' + str(message))


def user_subject(info=None):
    """
    to get subject or any other info depends on the input

    Args:
        info [string]: to indicate what the caller desire, if the caller want subject name, info='name', if no input, the whole JSON will be append into the list. Defaults to None.

    Returns:
        subject_list [an array of JSON]: an array of subject JSON
    """

    subject_list = []

    # refactoring techniques: replace temp with query
    user_role = get_user_role()

    user_competencies = user_role.user_competencies

    if info != None:
        for subject in user_competencies:
            subject_list.append(subject['subject'][str(info)])
    else:
        for subject in user_competencies:
            subject_list.append(subject['subject'])

    return subject_list

def get_user_role():
    """
    to check user's role
    @return: student object or tutor object, if not raise exception
    """

    if session['user_role'] == 'student':
        return student
    elif session['user_role'] == 'tutor':
        return tutor
    else:
        raise Exception("User is not student or tutor. Who is user?")

def user_profile_details():
    """

    Returns:
        user_profile_info: a dictionary that has user details, competencies, qualifications and bids
    """

    # refactoring techniques: replace temp with query
    user_role = get_user_role()
    
    user_details = user_role.user_details
    user_competencies = user_role.user_competencies
    user_qualifications = user_role.user_qualifications
    user_bids = user_role.user_bids

    user_profile_info = {'user_details': user_details, 'user_competencies':user_competencies, 'user_qualifications':user_qualifications, 'user_bids':user_bids}

    return user_profile_info


def user_index_bids():
    """
    get user's bid, and differentiate it to ongoing bid and closed down bid by checking on the dateClosedDown field

    Returns:
        onging_bid: a list of JSON bid that dateClosedDown is None
        closed_down_bid: a list of JSON bid that has dateClosedDown field 
    """

    # get user role
    # refactoring techniques: replace temp with query
    user_role = get_user_role()
    # update bid data from API
    user_role.get_user_bids()

    ongoing_bid = []
    closed_down_bid = []

    # use for loop to separate ongoing bid and closed down bid
    for bid in user_role.user_bids:

        if bid["dateClosedDown"] != None:
            closed_down_bid.append(bid)
        else:
            ongoing_bid.append(bid)

    return ongoing_bid, closed_down_bid


def check_contract_expire_soon():
    """
    get user's contract from user model and loop through the contract list to check if any contract is expired or expire in a month

    Returns:
        boolean: True if there are any contract expire soon or expired
        contract_expire_soon_list: a list of contract JSON that is going to expire in a month
        contract_expired_list a list of expired contract JSON 
    """

    contract_expire_soon_list = []
    contract_expired_list = []

    # get user contract
    # refactoring techniques: replace temp with query
    user_role = get_user_role()
    contract_list = user_role.user_contracts

    for contract in contract_list:
        if contract['dateSigned'] and not contract['terminationDate']:

            # get expiry date and current date
            expiry_date = datetime.strptime(contract['expiryDate'][:19], "%Y-%m-%dT%H:%M:%S")
            current_time = datetime.now()
            
            # get the diffenrence between expiry date and current date
            difference = expiry_date - current_time
            days = divmod(difference.days, 86400)

            # Refactoring techniques: composing method
            contract_expire_soon = (days[1] <= 31) and (days[1] >= 0)
            contract_expired = days[0] < 0

            if contract_expire_soon:
                contract_expire_soon_list.append(contract)
            if contract_expired:
                contract_expired_list.append(contract)
    
    # return True if there's elem in any list, else False
    if len(contract_expire_soon_list) >= 1 or len(contract_expired_list) >= 1:
        return True, contract_expire_soon_list, contract_expired_list
    else:
        return False, contract_expire_soon_list, contract_expired_list