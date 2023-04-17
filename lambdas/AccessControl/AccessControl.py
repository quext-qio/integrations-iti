# zato: ide-deploy=True

import re

from zato.server.service import Service

def pruneDisallowedRows(zato, acl, payload):
    if acl.rows["mode"] == "whitelist":
        zato.logger.info("unimplemented")
    elif acl.rows["mode"] == "blacklist":
        raise Exception("ACL blacklist feature is unimplemented.")
    elif acl.rows["mode"] == "all":
        zato.logger.info('Requester\'s X-API-KEY has a row-level ACL of "all", nothing to do.')
    else:
        raise Exception("Unknown row-level ACL mode.")

    return payload

def pruneDisallowedColumns(zato, acl, payload):
    # What's the mode?
    if acl.columns["mode"] == "whitelist":
        if payload is list:
            for i in payload:
                pruneKeys(zato, acl.columns["template"], i)
        else:
            pruneKeys(zato, acl.columns["template"], payload)
    elif acl.columns["mode"] == "blacklist":
        raise Exception("ACL blacklist feature is unimplemented.")
    elif acl.columns["mode"] == "all":
        zato.logger.info('Requester\'s X-API-KEY has a column-level ACL of "all", nothing to do.')
    else:
        raise Exception("Unknown column-level ACL mode.")

    return payload

def pruneKeys(zato, template, branch):
    zato.logger.info(type(branch))
    keys = list(branch.keys())
    for key in keys:
        # zato.logger.info('this ' + key + ' ' + str(type(branch[key])))
        if key not in template.keys() and "*" not in template.keys():
            zato.logger.info('bonk ' + str(key))
            del branch[key]
        elif type(branch[key]) is dict:
            templateKey = key if key in template.keys() else "*"
            zato.logger.info('digging deeper ' + str(key))
            pruneKeys(zato, template[templateKey], branch[key])  
        # If it's an array list, we'll just prune each element using the branch of the template as it were.
        elif type(branch[key]) is list:
            templateKey = key if key in template.keys() else "*"
            for a in branch[key]:
                pruneKeys(zato, template[templateKey], a)

    return branch

    # JSON acl:
        # {
        #     "rows": {
        #         "mode": "whitelist"   // possible values: blacklist (to be implemented later, or never), all (no other properties needed, we just give them everything)
        #         "column": "whatever",
        #         "values": []          // need a better name here, to indicate they are whitelisted
        #     },
        #     "columns": {
        #         "mode": "whitelist",  // possible values: blacklist (to be implemented later, or never), all (no other properties needed, we just give them everything)
        #         "template": {         // this is an object with the same shape as the response payload, properties only, values set to 1
        #             "v": 1,           // * (for everything) and simple regexes are allowed for keynames
        #             "x": 1,
        #             "y": {
        #                 "start": 1
        #             }
        #         }
        #     }
        # }


#----------------------------------

def accessControl(z):
    global ACLs
    wsgi = z.wsgi_environ
    endpoint = wsgi['PATH_INFO']
    verb = wsgi['REQUEST_METHOD']

    try:
        api_key = wsgi['HTTP_X_API_KEY']
    except KeyError:
        return None, "No API key header."

    try:
        ACLs
    except NameError:
        AccessControlService.loadACLs(z)

    if api_key is None:
        return None, "No API key value."

    for d in ACLs:
        if "apiKey" in d and d["apiKey"] == api_key:
            if "endpoints" not in d:
                return None, "No permission for any endpoint is defined."
            for e in d["endpoints"]:
                if "uri" in e and "verbs" in e and e["uri"] == endpoint and verb in e["verbs"]:
                    return e["acl"], "good"
                elif "uri" in e and e["uri"] == endpoint:
                    return None, "No permission for this HTTP method."
            return None, "No permission for this endpoint."

    # if an api key is provided, but isn't anywhere in the list, what then?
        # we need to keep track of that ip address and the attempt, if that ip address 
        # uses more than 50 non-existent api keys within some period, blackhole it

    return None, "Unknown API key."

def externalCredentials(z, partner):
    global ACLs
    wsgi = z.wsgi_environ
    api_key = wsgi['HTTP_X_API_KEY']

    try:
        ACLs
    except NameError:
        AccessControlService.loadACLs(z)

    if api_key is None:
        return None, "No API key value."

    for d in ACLs:
        if "apiKey" in d and d["apiKey"] == api_key:
            if "credentials" not in d:
                return None, "No credentials defined for any partner."
            for e in d["credentials"]:
                if "partner" in e and e["partner"] == partner:
                    headers = {}; body = {}
                    if "headers" in e:
                        headers = e["headers"]
                    if "body" in e:
                        body = e["body"]
                    return { "headers": headers, "body": body }, "good"
            return None, "No credentials defined for specified partner."

    return None, "Unknown API key."

def pruneDataSpruse(z, acl, payload):

    temp = []
    a = 0

    for d in payload:
        for e in d.keys():
            if e in ["residentId", "firstName", "lastName", "apt", "emailAddress", "phone", "leaseStartDate", "leaseEndDate", "moveInDate", "moveOutDate"]:
                if a > len(temp) - 1:
                    temp.append({})
                temp[a][e] = d[e]
        a += 1
    return temp

def pruneData(z, node, payload):
    z.logger.info(acl)

    root = acl["root"]

    node = 6

    # First, we'll get all the horizontal/row items squared away
    if "horizontal" in root:
        for r in node["horizontal"]["rules"]:
            # process the rules against payload, one by one
            z.logger.info(78)
        payload = pruneHorizontalData(z, root["mode"], node["horizontal"], payload)

    if "vertical" in root:
        for r in node["vertical"]["rules"]:
            # call pruneData recursively
            z.logger.info(78)
    

    # if type(payload) is list and "horizontal" in root:
    #     horizontal = root["horizontal"]
    #     for a in payload: # If payload is non-array, treat as a single-index array
    #         if "mode" not in horizontal:
    #             raise Exception("Horizontal rules are required to have a 'mode' property.")
    #         elif horizontal["mode"] == "whitelist":
    #             for b in horizontal["rules"]:
    #                 print(6)
    #         elif horizontal["mode"] == "blacklist":
    #             for b in horizontal["rules"]:
    #                 if b matches :
    #                     # del a somehow

    # elif type(payload) is dict and "horizontal" in root:



    # Next, we do the vertical/column

    return payload


# def pruneHorizontalData(z, mode, horizontal, payload):

#     match = False
#     temp = payload.copy()

#     if isinstance(payload, list):
#         tempList = payload.copy()
#         for a in payload:
#             for r in horizontal["rules"]:
#                 if isinstance(r, dict) and r.keys() >= { "type", "name", "value" } and r["type"] == "key" and payload[r["name"]] == r["value"]:
#                     X
#             if (mode == "blacklist" and match) or (mode == "whitelist" and not match):
#                 X
#     elif isinstance(payload, dict):
#         # Looking for a single rule that will match so that this single dict can survive (whitelist) or be nulled (blacklist)
#         for r in horizontal["rules"]:
#             if isinstance(r, dict) and r.keys() >= { "type", "name", "value" } and r["type"] == "key" and payload[r["name"]] == r["value"]:
#                 match = True
#             # Or, sometimes we're not looking for a single rule. TODO.
#             elif isinstance(r, dict) and r.keys() >= { "and" } and isinstance(r["and"], list):
#                 raise Exception("ACL horizontal boolean-and rules are unimplemented.")
#         if (mode == "blacklist" and match) or (mode == "whitelist" and not match):
#             temp = None

#     else:
#         if (payload not in horizontal["rules"] and mode == "whitelist") or (payload in horizontal["rules"] and mode == "blacklistlist"):
#             temp = None


#     return temp

# def pruneDisallowedRows(z, acl, mode, payload):
#     if mode == "whitelist":
#         # Is this a list or dict? If list, iterate through, if not, treat it as a single-index list
#         x
#     elif mode == "blacklist":
#         raise Exception("ACL blacklist feature is unimplemented.")
#     elif mode == "all":
#         z.logger.info('Requester\'s X-API-KEY has a horizontal ACL of "all", nothing to do.')
#     else:
#         raise Exception("Unknown row-level ACL mode.") 

#     return payload

# def pruneDisallowedColumns(z, acl, payload):
#     # if mode == "whitelist":
#     #     payload[]
#     # elif mode == "blacklist":
#     #     raise Exception("ACL blacklist feature is unimplemented.")
#     # elif mode == "all":
#     #     z.logger.info('Requester\'s X-API-KEY has a horizontal ACL of "all", nothing to do.')
#     # else:
#     #     raise Exception("Unknown row-level ACL mode.") 

#     return payload