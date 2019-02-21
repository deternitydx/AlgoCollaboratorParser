
class StudentInfoNode:
    def __init__(self, student_str):
        # student_str: name of subdirs in collab bulk_download.zip
        # format: last_name, first_name(computing_id)

        student_str = student_str.split(",")

        self.first_name = student_str[0]

        self.last_name = student_str[1].split("(")[0]

        self.computing_id = student_str[1].split("(")[1][:-1]

        # { str hw_name : list Student obj }
        self.collaborators = {}

    def print(self):
        pass

    def get_randomized_id(self):
        return id(self)

