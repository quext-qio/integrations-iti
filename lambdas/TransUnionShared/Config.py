import os

config = {
    'trans_union_secret_key': os.environ['TRANS_UNION_SECRET_KEY'],
    'trans_union_report_password': os.environ['TRANS_UNION_REPORT_PASSWORD'],
    'trans_union_postback_url': os.environ['TRANS_UNION_POST_BACK_URL'],
    'leasing_host': os.environ['LEASING_HOST'],
    'leasing_save_report_endpoint': os.environ['LEASING_SAVE_REPORT_ENDPOINT'],
    'member_name': os.environ['TRANS_UNION_MEMBER_NAME'],
    'password': os.environ['TRANS_UNION_REPORT_PASSWORD'],
    'property_id': os.environ['TRANS_UNION_PROPERTY_ID'],
    'source_id': os.environ['TRANS_UNION_SOURCE_ID']
}