import os
import zipfile
import shutil
import re
import logging
import sys

from tqdm import tqdm
from Parser.StudentInfoNode import StudentInfoNode


class CollaboratorsParser:

    def __init__(self, root_directory):
        self.logger = logging.getLogger(__name__) # logging
        self.abs_root_directory = os.path.abspath(root_directory) # abs path of class dir 
        self.abs_extracted_directory = os.path.join(self.abs_root_directory, "extracted_data") # abs path of extracted data
        self.student_mappings = {} # mappings of identifiers (computing id, firstname+lastname, etc) map to same StudentInfoNode reference


    # Generates student identifiers string given given
    # Return Forrmat: "last_name, first_name(computing_id)"
    # changes
    def get_student_identifiers(self, path):
        # Regex to get lastname, firstname, and computing id from path
        found_student_identifiers = re.findall("[A-Za-z\s]+[,][\s][A-Za-z\s]+[(][a-z]+[0-9][a-z]+[)]", path)

        # Found
        if found_student_identifiers:
            # Return last instance incase user named input path dir to match regex
            return found_student_identifiers[-1]

    def get_homework_identifier(self, path):
        # print(path)
        # Regex to get lastname, firstname, and computing id from path
        found_homework_identifiers = re.findall("HW[^\/]*", path)
        
        # Found
        if found_homework_identifiers:
            # Return last instance incase user named input path dir to match regex
            # print(found_homework_identifiers[-1])
            return found_homework_identifiers[-1]


    # Checks if class dir is in expected initial state with only zip files
    def is_valid(self):
        self.logger.info("Valididating class data directory files and path...")

        valid_filetype = ".zip"
        for path, dirs, files in os.walk(self.abs_root_directory):
            if dirs:
                self.logger.error("Directory contains invalid dirs")
                return False

            for file in tqdm(files):
                if not self._is_filetype(valid_filetype, file):
                    self.logger.error("Directory contains invalid files")
                    self.logger.error('%s is not %s', file, valid_filetype)
                    return False

        return True

    # Assumes zip is uncorrupted and attempts to extract
    def _extract(self, abs_input_file, abs_output_file=None):
        try:
            zip_ref = zipfile.ZipFile(abs_input_file)
            zip_ref.extractall(abs_output_file)
            zip_ref.close()
        except:
            # Log failures to parser.log
            self.logger.warning("Unable to extract: %s", abs_input_file)

    # Checks if file has the input extension
    def _is_filetype(self, filetype, filename):

        if len(filename)<len(filetype):
            return False
        if filename[-len(filetype):] != filetype:
            return False

        return True


    # Extracts nested zip files
    def extract_bulk_downloads(self):
        self.logger.info("Extracting bulk_download zip files...")
        for path, dirs, files in (os.walk(self.abs_root_directory)):
            for file in tqdm(files):
                abs_file_path = os.path.join(path, file)
                self._extract(abs_file_path, self.abs_extracted_directory)

        self.logger.info("Extracting nested student zip files...")
        for path, dirs, files in tqdm(list(os.walk(self.abs_extracted_directory))):
            for file in files:
                if self._is_filetype(".zip", file):
                    abs_file_path = os.path.join(path, file)
                    self._extract(abs_file_path, path)

    # Reads latex files and maps students to StudentInfoNode instances
    def map_students(self):
        self.logger.info("Mapping student identifiers to StudentInfoNode...")
        for path, dirs, files in tqdm(list(os.walk(self.abs_extracted_directory))):
            for file in files:
                if self._is_filetype(".tex", file):
                    
                    # Get lastname, firstname, and computing id from path
                    student_identifiers = self.get_student_identifiers(path)

                    # Add mappings if student found
                    if student_identifiers:
                        self.add_possible_student_mapping(student_identifiers)
                    else:
                        self.logger.warning("Unable to parse path using defined regex: %s", os.path.join(path, file))

    

    def add_possible_student_mapping(self, student_identifiers):

        if student_identifiers in self.student_mappings:
            return #student already mapped

        # Create new student
        student = StudentInfoNode(student_identifiers)

        # Map main identifier to StudentInfoNode
        self.student_mappings[student_identifiers] = student

        # Map other identifier
        # Checking for invalid edge cases just in case
        if student.is_valid:
            self.student_mappings[student.firstname + " " + student.lastname] = student
            self.student_mappings[student.computing_id] = student

    
    # Create collaborators graph for all students
    def generate_collaborators(self):
        self.logger.info("Creating collaborators graph with StudentInfoNodes...")
        for path, dirs, files in tqdm(list(os.walk(self.abs_extracted_directory))):
            for file in files:
                if self._is_filetype(".tex", file):
                    abs_file_path = os.path.join(path, file)
                    self.map_collaborators(abs_file_path)
    

    def map_collaborators(self, path):

        identifier = self.get_student_identifiers(path)
        
        # Invald student path
        if not identifier:
            return

        # Get homework name
        homework = self.get_homework_identifier(path)
        
        # Get mapped student
        student = self.student_mappings[identifier]

        # Get string put by student
        collab_str = self.parse_tex_collaborators(path)

        # Generate every substring and attempt to match collaborators
        # This is gross. But also the best away to catch all edge cases.
        substrings = [collab_str[i:j+1] for i in range(len(collab_str)) for j in range(i,len(collab_str))]


        # Map
        for s in substrings:
            if s not in self.student_mappings:
                continue
            
            collaborator = self.student_mappings[s]

            # Create empty set to hold collaborators in student obj
            # Avoids duplicate edges in graph
            if homework not in student.collaborators:
                student.collaborators[homework] = set()
            
            student.collaborators[homework].add(collaborator)

         

    # Reads latex file and finds collaborators
    def parse_tex_collaborators(self, abs_input_file):
        with open(abs_input_file, encoding="utf8", errors='ignore') as data:
            collabs = re.findall(r'\\def\\collabs{(.*?)}', data.read(), re.S)
            
            # returns student submitted string
            # returns empty string if nothing to avoid null checking late (im lazy)
            return collabs[-1] if collabs else ""


    def output_to_file(self, filename):
        self.logger.info("Writing to outputfile...")

        output = open(filename, "a")
        
        # Keep track of outputted to track multiple refrences
        visited = set()

        for identifier in tqdm(self.student_mappings):
            student = self.student_mappings[identifier]

            if student in visited:
                continue
            
            visited.add(student)

            output.write(student.randomized_id)
            output.write("\n")

            for hw in student.collaborators:
                collaborators_list = [s.randomized_id for s in student.collaborators[hw]]
                output.write(hw+": ")
                output.write(", ".join(collaborators_list))
                output.write("\n")

            output.write("\n")

        output.close()
    def cleanup(self):
        shutil.rmtree(self.abs_extracted_directory)

