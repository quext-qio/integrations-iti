from cerberus.errors import BasicErrorHandler

class CustomErrorHandler(BasicErrorHandler):
    def __init__(self, schema):
        self.custom_defined_schema = schema

    def _format_message(self, field, error):
        if error.code == 65:
            return self.custom_defined_schema[field].get('meta', {}).get('regex', field)
        else:
            return super(CustomErrorHandler, self)._format_message(field, error) 