"""
The LLamaText Generator connects to and sends predictions.
We want an inference call to be made once per document, reducing cost and later test generation.
Given we offer multiple services, we create containers for the generates question banks and allow for easy storage and retrival of answers.
"""

# General
from random import randint, sample
import numpy as np

# Custom
from infer import LlamaTextGenerator
from customerrors import OverwriteError, DocumentLength, UnknownTestType

class TestBank():
    def __init__(self):
        # Document info
        self.text = None
        # Resonable number of questions given the document length
        self.numQuestions = None

        # Create connection to the text service model
        self.generator = LlamaTextGenerator()
        
        # Original STATIC question banks (mixed will be sampled from mcqs and short_answers)
        self.mcqs = None
        self.short_answers = None
        self.custom = None

        # Unseen versions of Original question banks
        self.unseen_mcq = None
        self.unseen_short_answers = None
        self.unseen_custom = None

        # Constants
        self.divFactor = 212

    def _validateDocument(self, N):
        """
        Check that the document has enough text to test from. If it does, create the right number of questions based on that.
        """
        if N < self.divFactor:
            raise DocumentLength()
        
        else:
            self.numQuestions = round(N / self.divFactor())

    def initalizeText(self, text):
        """
        Assigns the document information. Trips on the user's first call to generate a test.
        """
        # Make sure this document is long enough to make a test from and assign proper number of questions
        self._validateDocument(len(text))
        # Assign to the object only after it passes the validation 
        self.text = text

    def buildBank(self, option: str, prompt = None):
        """
        Called from the MCQGenerator to build the specific test bank for the test type (expect mixed).

        Args:
            option (str): Switches the case for which question bank to build (thus how to prompt the model)
            prompt (str): IF the developer wants to have a prompt, they can use this argument

        """
        if option.lower() == 'mcq':
            # Create the original question bank and instantiate the unseen version
            self.mcqs = self.generator.generate_questions(self.text, self.numQuestions)
            self.unseen_mcq = self.mcqs

        elif option.lower() == 'short answer':
             # Create the original question bank and instantiate the unseen version
            self.short_answers = self.generator.generate_short_answers(self.text, self.numQuestions)
            self.unseen_short_answers = self.short_answers

        elif option.lower() == 'custom':
             # Create the original question bank and instantiate the unseen version
            self.custom = self.generator.generate_custom_prompt_questions(self.text, prompt)
            self.unseen_custom = self.custom

        else:
            # Something happened during dev
            raise UnknownTestType()
        
    def generate_mcq_test(self, numQuestions, repeats):
        """
        Generates the MCQ test by pulling from the created bank. Default behavior is no repeats, 10 questions.

        Args:
            numQuestions (int): The number of questions the user wants this test to have.
            repeats (bool): Indictaes if the user is okay with seeing repeats.

        Returns:
            list[str]: List of multiple choice questions.
        """
        # Make sure the parameter is some type of singular number
        try:
            numQuestions = int(numQuestions)

        except:
            raise TypeError('Please enter a whole number of how many questions you\'d like for this test')
        
        # If the user has gone through all their unseen questions, reset and inform
        if not repeats and len(self.unseen_mcq) == 0:
            print('You\'ve completed seen all the questions, congrats! Resetting the set.')
            self.unseen_mcq = self.mcqs

        # If the user wants no repeats but they want more questions than we generated for the whole QB, tell them no and fix it
        if not repeats and len(self.mcqs) < numQuestions:
            print(f'You requested {numQuestions} unique questions, but only {len(self.mcqs)} exist')
            # For now, just make the test shorter, but we could ask the user what they prefer -- repeats or this
            print('We\'ll generate a shorter test to keep the questions unique.')
            numQuestions = self.numQuestions

        # If the user asked for more questions than they have left in the unseen set, let them know and make a test only that big
        if repeats and len(self.unseen_mcq) < numQuestions:
            print(f'You only have {len(self.unseen_mcq)} unseen questions left. We\'ll make a test out of those first.')
            numQuestions = len(self.unseen_mcq)

        # Check if the user wants repeats or not
        if repeats:
            # Generate directly from the originalQB, uses sample so we don't get repeat questions in the SAME test
            testQs = sample(self.mcqs, numQuestions)

            return testQs

        else:
            # Generate random indices one at a time so we ensure no repeats in this set or bewteen the others
            qIDs = sample(list(np.arange(0, len(self.unseen_mcq))), numQuestions)
            # Exploit numpy indexing to do this in one go then reset to python list
            testQs = list(np.array(self.unseen_mcq)[qIDs])

            # Get rid of the overlap with set difference, then back to list
            self.unseen_mcq = list(set(self.unseen_mcq) - set(testQs))

            return testQs        

    def generate_short_answer_test(self, numQuestions, repeats):
        """
        Generates the short answer test by pulling from the created bank. Default behavior is no repeats, 10 question.

        Args:
            numQuestions (int): The number of questions the user wants this test to have.
            repeats (bool): Indictaes if the user is okay with seeing repeats.

        Returns:
            list[str]: List of short answer questions.
        """
        raise NotImplementedError('Generating the short answer test in [TestBank] is not finished yet.')


    def generate_mixed_test(self, numQuestions, repeats):
        """
        Generates a mix of MCQs and short answers. Default behavior is no repeats, 10 questions.

        Args:
            numQuestions (int): The number of questions the user wants this test to have.
            repeats (bool): Indictaes if the user is okay with seeing repeats.

        Returns:
            list[str]: List of mixed questions.
        """
        # mcqs = self.generate_questions(text, max_length)
        # short_answers = self.generate_short_answers(text, max_length)

        # # Interleave MCQs and short answers or just concatenate, based on your preference
        # mixed_questions = mcqs + short_answers
        # return mixed_questions
        raise NotImplementedError('Generating the mixed format test in [TestBank] is not finished yet.')

    def generate_custom_test(self, repeats):
        """
        Generates a test based on a custom prompt. Default behavior is no repeats.

        Args:
            repeats (bool): Indictaes if the user is okay with seeing repeats.

        Returns:
            list[str]: List of mixed questions.
        """
        raise NotImplementedError('Generating the custom prompt test in [TestBank] is not finished yet.')
