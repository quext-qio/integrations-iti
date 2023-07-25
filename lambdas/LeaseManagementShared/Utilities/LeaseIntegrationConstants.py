class LeaseIntegrationConstants:
    HTTP_GOOD_RESPONSE_CODE = 200
    HTTP_BAD_RESPONSE_CODE = 400
    LEASE_MANAGEMENT_PURPOSE = 'leaseManagement'
    COMMUNITY_UUID = 'communityUUID'
    CUSTOMER_UUID = 'customerUUID'
    PURPOSE = 'purpose'
    LEASE_ID = 'leaseId'
    PLATFORM_OUTGOING_CHANNEL = 'Platform_Outgoing_Channel'
    LEASE_REMOVE = 'Lease_Remove_Channel'
    PLATFORM_DATA = 'platformData'
    HEADERS = {
        "Content-Type": "application/json",
        "Accept": "application/json"}
    CREATE_LEASE_METHOD = 'createLeaseRequestData'
    UPDATE_LEASE_METHOD = 'updateLeaseRequestData'
    DELETE_LEASE_METHOD = 'deleteLeaseRequestData'
    GET_LEASE_METHOD = 'getLeaseRequestData'
    RESPONSE_CODE = 'responseCode'
    RESPONSE_MESSAGE = 'responseMessage'
    FORMAT_CREATE_LEASE_METHOD = 'formatCreateLeaseResponseData'
    FORMAT_UPDATE_LEASE = 'formatUpdateLeaseResponseData'
    FORMAT_DELETE_LEASE = 'formatDeleteLeaseResponseData'
    FORMAT_GET_LEASE = 'formatGetLeaseResponseData'
