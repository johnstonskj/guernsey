from guernsey import ClientFilter

class LastClientFilter(ClientFilter):
    """ TBD
    """
    def __init__(self, response):
        self.response = response

    def handle(self, client_request, next_filter):
        return self.response

