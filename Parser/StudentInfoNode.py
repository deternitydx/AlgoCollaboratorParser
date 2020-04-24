import logging

class StudentInfoNode:
    def __init__(self, identifiers):

        # identifiers format: "last_name, first_name(computing_id)"

        # Setup logging
        self.logger = logging.getLogger(__name__)

        # Initialize instance vars
        self.identifiers = identifiers
        self.is_valid = True
        self.firstname = None
        self.lastname = None
        self.computing_id = None
        self.grade = 0

        # Set Random ID
        self.randomized_id = str(self.set_randomized_id())

        # Set instance vars
        self.set_identifiers(identifiers)

        # { hw_name str : StudentInfoNode list }
        self.collaborators = {}

        # print(identifiers)
        # print(self.lastname)
        # print(self.firstname)
        # print()

    def match_actual_random_id(self):
        return self.computing_id, self.randomized_id

    def set_identifiers(self, identifiers):
        
        # Separate firstname, lastname, computing_id from student_identifiers
        try:
            identifiers = identifiers.split(",")
            self.lastname = identifiers[0].strip()
            self.firstname = identifiers[1].split("(")[0].strip()
            self.computing_id = identifiers[1].split("(")[1][:-1].strip()
        except:
            self.is_valid = False
            self.logger.warning("Invalid identifier input %s", identifiers)

    def set_randomized_id(self):
        # Simple implementation.
        return hash(self)

        

