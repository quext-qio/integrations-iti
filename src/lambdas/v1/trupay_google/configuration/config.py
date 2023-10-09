import os

trupay_config = {
    'company_short_name': os.environ["TRUPAY_COMPANY_SHORT_NAME"],
    'username': os.environ["TRUPAY_USERNAME"],
    'password': os.environ["TRUPAY_PASSWORD"],
    'api_key': os.environ["TRUPAY_API_KEY"],
    'trupay_login_url': 'https://secure.saashr.com/ta/rest/v1/login'
}