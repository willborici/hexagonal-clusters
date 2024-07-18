# Class for elicited information (needs, challenges, desires, ideas, etc.)
class ElicitedInformation:
    def __init__(self, information, source=''):
        self.__information = information  # the information text
        self.__source = source  # the information source

    @property
    def information(self):
        return self.__information

    @information.setter
    def information(self, information):
        self.__information = information

    @property
    def source(self):
        return self.__source

    @source.setter
    def source(self, source):
        self.__source = source
