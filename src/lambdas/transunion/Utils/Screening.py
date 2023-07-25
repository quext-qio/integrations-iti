import re

def structure_object_resident_screening_transunion(request, member_name, password, property_id, source_id, trans_union_postback_url):
    new_request = {"gateway": request}
    new_request['gateway']['version'] = 2
    new_request['gateway']['agent'] = {
        "memberName": member_name,
        "password": password,
        "propertyId": property_id,
        "sourceId": source_id,
        "responseURL": trans_union_postback_url
    }
    return new_request


def clean_xml_transunion_screening_response(response):
    return re.sub(r'(?s)(<BackgroundReport>)(.*?)(</BackgroundReport>)', '', response.text)