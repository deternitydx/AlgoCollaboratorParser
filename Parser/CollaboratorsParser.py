import os
import zipfile
import shutil
import re
import logging
import sys

#added imports
from zipfile import ZipFile
import pandas as pd
from functools import reduce
import collections

from Parser.participants_all import get_participants_all_list

from tqdm import tqdm
from Parser.StudentInfoNode import StudentInfoNode


class CollaboratorsParser:

    def __init__(self, root_directory):
        self.logger = logging.getLogger(__name__) # logging
        self.abs_root_directory = os.path.abspath(root_directory) # abs path of class dir 
        self.abs_extracted_directory = os.path.join(self.abs_root_directory, "extracted_data") # abs path of extracted data
        self.student_mappings = {} # mappings of identifiers (computing id, firstname+lastname, etc) map to same StudentInfoNode reference
        self.list_csv_location =[] # the list of the locations of all the csv files to be read
        self.actual_to_randomized_id={}# mapping of each students' actual id to the randomized id


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
        #found_homework_identifiers = re.findall("HW[^\/]*", path)
        found_homework_identifiers = re.findall("HW[0-9]+", path)
        
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
            for each_dir in dirs:
                inner_path = os.path.join(self.abs_extracted_directory, each_dir)
                for r, d, f in os.walk(inner_path):
                    for file in f:
                        if self._is_filetype(".csv", file):
                            self.list_csv_location.append(os.path.join(inner_path, file))
                
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



    
# check if student consent is given
    # def add_possible_student_mapping(self, student_identifiers):

    #     if student_identifiers in self.student_mappings:
    #         return #student already mapped

    #     # Create new student
    #     list_participants_all = get_participants_all_list()
    #     student = StudentInfoNode(student_identifiers)
    #     if student.computing_id in list_participants_all:
    #     # Map main identifier to StudentInfoNode
    #         self.student_mappings[student_identifiers] = student

    #     # Map other identifier
    #     # Checking for invalid edge cases just in case
    #         if student.is_valid:
    #             self.student_mappings[student.firstname + " " + student.lastname] = student
    #             self.student_mappings[student.computing_id] = student

    def add_possible_student_mapping(self, student_identifiers):

        if student_identifiers in self.student_mappings:
            return #student already mapped

        list_participants_all = get_participants_all_list()

        # Map main identifier to StudentInfoNode
        print("Looking for participant", student.computing_id)
        if student.computing_id in list_participants_all:
            print("--Found", student.computing_id)
            # Create new student
            student = StudentInfoNode(student_identifiers)
            # Add the actual and randomized id mapping
            student.set_randomized_id()
            actual, randomized = student.match_actual_random_id()
            self.actual_to_randomized_id.update({actual:randomized})
            self.student_mappings[student_identifiers] = student
            print("-- -- --", actual, randomized)

            # Map other identifier
            # Checking for invalid edge cases just in case
            if student.is_valid:
                self.student_mappings[student.firstname + " " + student.lastname] = student
                self.student_mappings[student.computing_id] = student
        else:
            print("--Not Found", student.computing_id)



    # Create collaborators graph for all students
    def generate_collaborators(self):
        self.logger.info("Creating collaborators graph with StudentInfoNodes...")
        for path, dirs, files in tqdm(list(os.walk(self.abs_extracted_directory))):
            for file in files:
            # mint starts coding here
                abs_file_path = os.path.join(path, file)
                if self._is_filetype(".tex", file):
                    self.map_collaborators(abs_file_path,"tex")
                elif self._is_filetype(".py", file):
                    self.map_collaborators(abs_file_path, "python")
                elif self._is_filetype(".java", file):
                    self.map_collaborators(abs_file_path, "java")
    

    def map_collaborators(self, path, type):

        identifier = self.get_student_identifiers(path)
        
        # Invald student path
        if not identifier:
            return

        # Get homework name
        homework = self.get_homework_identifier(path)
        
        # Get mapped student
        if identifier in self.student_mappings:
            student = self.student_mappings[identifier]

            # Get string put by student
            if type == "tex":
                collab_str = self.parse_tex_collaborators(path)
            else:
                collab_str = self.parse_python_java_collaborators(path)

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

    def parse_python_java_collaborators(self, abs_input_file):
        with open(abs_input_file, encoding="utf8", errors='ignore') as data:
            collabs = re.findall(r'Collaborators: .*?\n', data.read(),re.S)
           
            # returns student submitted string
            # returns empty string if nothing to avoid null checking late (im lazy)
            return collabs[-1] if collabs else ""


    def parse_grade(self, list_of_csv_locations):
        list_df=[]
        list_col_names=[]
        for file in list_of_csv_locations:
            df = pd.read_csv(file, sep=',',engine='python',skiprows = [0,1])
            df_hw = pd.read_csv(file, sep=',',engine='python', nrows=1)
            name = 'HW'+str(re.findall(r"HW(.*?) -", str(df_hw))[-1])

            #extract the computing id and grade columns
            df = df.iloc[:,[0,4]]
            df.columns = ['Display ID',name]
            list_df.append(df)

        # merge all panda frames into one by the computing id
        df_f = reduce(lambda x, y: pd.merge(x, y, how='outer', on = 'Display ID'), list_df)

        # replace real ids with randomized ids
        for actual in self.actual_to_randomized_id:
            df_f.replace(actual, self.actual_to_randomized_id[actual], inplace=True)

        df_f = df_f.set_index('Display ID')
        #enter default grade of 99 for homework students didn't turn in
        df_f.fillna('99', inplace=True)
        #sort all homework columns by homework number
        df_f = df_f.sort_index(axis=1)
        df_f_with_collaborators = df_f

        df_f.to_csv("grades_all.csv")
        


    # look up grade for a specified homework from a specified student
    def grade_lookup(self, randomized_id, hw):
        df = pd.read_csv('grades_all.csv',sep=',')
        df = df.set_index('Display ID')
        str_check = hw
        if hw not in df.columns:
            # raise ValueError("homework not found, possibly because no grades.csv file is contained in folder")
            return 0
        return df.at[str(randomized_id), hw]

    #look up collaborators for a specified homework from a specified student
    def collaborator_lookup(self, randomized_id, hw):
        collaborators_list=[]
        for identifier, student in self.student_mappings.items():
            if str(student.randomized_id) == str(randomized_id):
                try:
                    collaborators_list = [s.randomized_id for s in student.collaborators[hw]]
                # except:
                #     print(sys.exc_info())
                    # print(randomized_id,'does not have collaborators for homework',hw)
                #     print(">")
                finally:
                    return collaborators_list


    def output_to_file(self, filename):

        self.parse_grade(self.list_csv_location)

        self.logger.info("Writing to outputfile...")

        output = open(filename, "a")
        
        # Keep track of outputted to track multiple refrences
        visited = set()
        
        df = pd.read_csv('grades_all.csv')
        cols = list(df.columns)
        # df = df.set_index('Display ID')
        # for identifier in tqdm(self.student_mappings):
        #     student = self.student_mappings[identifier]

        #     if student in visited:
        #         continue
            
        #     visited.add(student)

        #     output.write(student.randomized_id)
        #     output.write("\n")
            
            #open grade.csv, copy, try except all students, modify

            #loop over all homework
            # print("col names",cols[1:])
            # print("here",student.collaborators['HW1'])
            # print(collaborators_list)
        #     print(df['Display ID'])
        #     row_student = df[df['Display ID'] == int(student.randomized_id)].index[0]


        #     for hw in cols[1:]:
        #         try:
        #             collaborators_list = [s.randomized_id for s in student.collaborators[hw]]
        #             print('student random id:',student.randomized_id)
        #             print(df.at[row_student,hw])
        #             # df_f.replace(actual, self.actual_to_randomized_id[actual], inplace=True)
        #             df.replace(df.at[row_student,hw], {df.at[row_student,hw]:collaborators_list}, inplace = True)
        #             # df.at[int(student.randomized_id),hw] = {df.at[int(student.randomized_id),hw]:collaborators_list}
        #         except:
        #             print(sys.exc_info())
        #             print(hw, 'is not found')
        # print(df)    
        # df.to_csv('grades_collaborators_all.csv')


        #     output.write(student.randomized_id)
        #     output.write("\n")
        output.write("first part: list of all students with all their homework grades and collaborators \n")
        students_unchanged_collaborators = []
        students_working_alone = []

        #loop over all students in the grades_all.csv file
        for name in df['Display ID']:
            collaborators_for_each_student=[]
            output.write(str(name))
            output.write("\n")

            #loop through all the homework for each student
            for hw in cols[1:]:
                grade = self.grade_lookup(name,hw)
                collaborators_list = self.collaborator_lookup(name,hw)
                collaborators_for_each_student.append(collaborators_list)
                output.write(hw+"("+str(grade)+")"+": ")

                # if list not empty
                if collaborators_list:
                    output.write(", ".join(collaborators_list))
                output.write("\n")
            #check if all the collaborator list is the same for all homework
            if all(elem == collaborators_for_each_student[0] for elem in collaborators_for_each_student):
                if collaborators_for_each_student[0] == "":
                    students_working_alone.append(name)
                students_unchanged_collaborators.append(name)
            output.write("\n")
        output.write("-----------------------\n")

        output.write("part 2: students who collaborate with the same person/people for all homework: \n")
        for i in students_unchanged_collaborators:
            output.write(str(i))
            output.write("\n")


        output.write("-----------------------\n")
        output.write("part 3: students who always work alone: \n")
        for i in students_working_alone:
            output.write(str(i))
            output.write("\n")


            

            # #each hw is in form of 'HW_', where _ is a number
            # for hw in sorted(student.collaborators):
            #     collaborators_list = [s.randomized_id for s in student.collaborators[hw]]
            #     print(hw)
            #     # hw_num = hw  # re.findall(r"(.*?) -", hw)[-1]

            #     try:
            #         grade = self.grade_lookup(student.randomized_id,hw)
            #         output.write(hw+"("+str(grade)+")"+": ")
            #     except:
            #         print(sys.exc_info())
            #         output.write(hw+"(NOTFOUND)"+": ")
            #     # output.write()

            #     output.write(", ".join(collaborators_list))
            #     output.write("\n")

            # output.write("\n")

        output.close()
    def cleanup(self):
        shutil.rmtree(self.abs_extracted_directory)

