import os
from dotenv import load_dotenv
load_dotenv('/docker/local.env')

config = {
    'IntegrationPartnerID': os.getenv('RESMAN_INTEGRATION_PARTNER_ID'),
    'APIKey': os.getenv('RESMAN_API_KEY'),
    'AccountID': os.getenv('RESMAN_ACCOUNT_ID'),
    'PropertyID': os.getenv('RESMAN_PROPERTY_ID')
}
