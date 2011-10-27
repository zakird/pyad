class comException(Exception):
    def __init__(self, error_info, additional_info={}):
        self.error_info = error_info
        self.additional_info = additional_info   


class genericADSIException(comException):
    def __init__(self, error_info, additional_info={}):
        comException.__init__(error_info, additional_info)

    def __str__(self):
        return "%s (%s): %s" % (self.error_info['error_constant'], self.error_info['error_code'], self.error_info['error_message'])


class win32Exception(comException):
    def __init__(self, error_info, additional_info={}):
        comException.__init__(self, error_info, additional_info)

    def __str__(self):
        return "%s: %s" % (self.error_info['error_code'], self.error_info['message'])


class invalidOwnerException(Exception):
    def __str__(self):
        return "The submitted object is not eligible to own another object."


class noObjectFoundException(Exception): 
    def __str__(self):
        return "The requested object does not exist."

class InvalidObjectException(noObjectFoundException, win32Exception):
    def __init__(self, error_info, additional_info):
        win32Exception.__init__(self, error_info, additional_info)


class InvalidAttribute(AttributeError):
    def __init__(self, obj, attribute):
        self.obj, self.attribute = obj, attribute

    def __str__(self):
        return 'The attribute "%s" is not permitted by the schema definition of the object "%s" (the requested attribute does not exist).' % (self.attribute, self.obj)


class noExecutedQuery(Exception):
    def __str__(self):
        return 'No query has been executed. Therefore there are no results to return. Execute a query before requesting results.'


class invalidResults(Exception):
  def __init__(self, numberResults):
    self.__numberResults = numberResults
    
  def __str__(self):
    return 'The specified query resturned %i results. getSingleResults only functions with a single result.' % self.__numberResults