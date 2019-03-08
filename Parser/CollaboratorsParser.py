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

        # mappings of strings to StudentInfoNode object
        # many identifiers (computing id, firstname+lastname, etc) map to same StudentInfoNode reference
        self.student_mappings = {} 

    # Checks if class dir is in expected initial state with only zip files
    def is_valid(self):
        self.logger.info("Valididating class data directory files and path.")

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
        self.logger.info("Extracting bulk_download zip files.")
        for path, dirs, files in (os.walk(self.abs_root_directory)):
            for file in tqdm(files):
                abs_file_path = os.path.join(path, file)
                self._extract(abs_file_path, self.abs_extracted_directory)

        self.logger.info("Extracting nested student zip files.")
        for path, dirs, files in tqdm(list(os.walk(self.abs_extracted_directory))):
            for file in files:
                if self._is_filetype(".zip", file):
                    abs_file_path = os.path.join(path, file)
                    self._extract(abs_file_path, path)

    # def map_students(self):
    #     self.logger.info("Mapping student identifiers to StudentInfoNode.")
    #     for path, dirs, files in tqdm(list(os.walk(self.abs_extracted_directory))):
    #         for file in files:
    #             if self._is_filetype(".tex", file):
    #                 x = re.search("[A-Z][a-z]+[,][ ][A-Z][a-z]+[(][a-z]+[0-9][a-z]+[)]", file)
    #                 if x:
    #                     print(x)
    #                 else:
    #                     for i in range(30):
    #                         print()
    #                     print(path)
    
    # Create collaborators graph for all students
    def generate_collaborators(self):
        self.logger.info("Parsing tex to get collaborators")
        for path, dirs, files in tqdm(list(os.walk(self.abs_extracted_directory))):
            for file in files:
                if self._is_filetype(".tex", file):
                    abs_file_path = os.path.join(path, file)
                    collaborators = self.parse_tex(abs_file_path)
                    map_student(abs_file_path, collaborators)
                    # [A-Z][a-z]+[,][ ][A-Z][a-z]+[(][a-z]+[0-9][a-z]+[)]

    def parse_tex(self, abs_input_file):
        with open(abs_input_file, encoding="utf8", errors='ignore') as data:
            c = re.findall(r'\\def\\collabs{(.*?)}', data.read(), re.S)
            return c


    def output_to_file(self, filename):
        pass

    def cleanup(self):
        shutil.rmtree(self.abs_extracted_directory)

