import logging

#new imports
import random
import string

class StudentInfoNode:

    availableIds = list(range(1,190))

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
        #self.randomized_id = str(self.set_randomized_id())

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
        #return hash(self)
        
        #Random implementation- possible but very low chance of duplicates for our purposes
        #(there are 62^9, or 1.354 * 10^16 possible combinations, if I've done the math right)
       #return ''.join(random.choices(string.ascii_letters+string.digits,k = 9))

        #final implementation-chooses randomly from list of ids
        if(len(StudentInfoNode.availableIds)>0):
            #choose randomly from list of available Ids and then remove that Id from the list
            temp = random.choice(StudentInfoNode.availableIds)
            StudentInfoNode.availableIds.remove(temp)
            self.randomized_id = str(temp)
        else:
            # randomly choose id if the available id list runs dry (shouldn't happen for our list)
            self.randomized_id = ''.join(random.choices(string.digits+string.ascii_letters,k = 5))

    def set_randomized_id_for_nonparticipants(self):
        self.randomized_id = "999"

        

