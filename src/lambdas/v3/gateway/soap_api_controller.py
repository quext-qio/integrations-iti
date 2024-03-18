from zeep import Client


class SOAPCaller:
    @staticmethod
    def handle_request(request):
        # Make the soap api call
        xml_payload = request.body

        client = Client(request.url)
        response = client.service.some_method(xml_payload)

        return response

