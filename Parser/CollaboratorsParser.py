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
        self.logger = logging.getLogger(__name__)
        self.abs_root_directory = os.path.abspath(root_directory)
        self.abs_extracted_directory = os.path.join(self.abs_root_directory, "extracted_data")
        self.student_mappings = {}

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

    def _extract(self, abs_input_file, abs_output_file=None):

        # Assumes zip is uncorrupted and attempts to extract
        try:
            zip_ref = zipfile.ZipFile(abs_input_file)
            zip_ref.extractall(abs_output_file)
            zip_ref.close()
        except:
            self.logger.warning("Unable to extract: %s", abs_input_file)


    def _is_filetype(self, filetype, filename):

        if len(filename)<len(filetype):
            return False

        if filename[-len(filetype):] != filetype:
            return False

        return True

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
                    
    def generate_collaborators(self):
        self.logger.info("Interate through extracted files and parse tex")
        for path, dirs, files in tqdm(list(os.walk(self.abs_extracted_directory))):
            for file in files:
                if self._is_filetype(".tex", file):
                    abs_file_path = os.path.join(path, file)
                    self.parse_tex(abs_file_path)


    def parse_tex(self, abs_input_file):
        with open(abs_input_file, encoding="utf8", errors='ignore') as data:
            c = re.findall(r'\\def\\collabs{(.*?)}', data.read(), re.S)
            # print(abs_input_file)
            # print(c)
            # print()

    def output_to_file(self, filename):
        pass

    def cleanup(self):
        shutil.rmtree(self.abs_extracted_directory)

