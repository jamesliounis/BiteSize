class OverwriteError(Exception):
    """
    The variable we're trying to write to already holds information. Indicates something isn't processing right.
    """
    
    def __str__(self):
        return 'The variable you\'re trying to write to already holds information'
    
class DocumentLength(Exception):
    """
    The document we parsed to string is too short to make a quiz from. 
    """
    
    def __str__(self):
        return 'The provided document is too short to make meaningful questions from. Please provide a document with more than 212 characters' 

class UnknownTestType(Exception):
    """
    The option for generating the test bank doesn't match mcq, short answer, or custom
    """
    
    def __str__(self):
        return '[Developer] The options for building the question bank are mcq, short answer, and custom'  