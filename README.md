
## CS 4102 Homework Collaborators Parser

### Status
Work in progess. Needs more testing.

 &nbsp;&nbsp;
 
### Usage
`python3 -m Parser [-h] CLASS_DATA_DIRECTORY OUTPUT_FILE [-c]`

##### Positional Arguments

  _CLASS_DATA_DIRECTORY_
  Directory containing bulk_down.zip files from Collab
  
  _OUTPUT_FILE_
  Filename for output containing collaborator graph data (Ex: AlgorithmsFall2018.txt)

##### Optional Arguments

  _-h, --help_
  Show this help message and exit
  
  _-c, --cleanup_
  Removes any files extracted during parsing and restores parent to original state


&nbsp;&nbsp;
### Setup

##### Downloading Student Data

1. Access class collab page on an instructor account
2. Click Assignments tab
3. Select grade on an written assignment with student collaboration data (not Coding Assignments, LaTeX Practice, or Exams)
4. Select 'Download All' and choose 'Student submission attachment(s)'
5. This should begin the download for the bulk_download.zip for that specific homework.
6. Repeat this step for every written homework from which student collaboration data can be collected (not Coding Assignments, LaTeX Practice, or Exams)

##### Expected Directory Layout

+ Parser/
    + \_\_init\_\_.py
    + CollaboratorsParser.py
    + StudentInfo.py
    + run.py
+ ClassData2018F/
    * bulk_download.zip
    * bulk_download (1).zip
    * bulk_download (2).zip
    * ...
    * bulk_download (n).zip
+ ClassData2017S/
    * bulk_download.zip
    * bulk_download (1).zip
    * bulk_download (2).zip
    * ...
    * bulk_download (n).zip

##### Example Usage
`python3 -m run ` 
Generate collaborators data for ClassData2017S directory, save to Collaborators2017S.txt, and clean up extracted files 


&nbsp;&nbsp;

### Randomizing Student Data
Student data is stored in instances of the StudentInfoNode object. After the collaborator info is parsed from the latex files and mapped to the StudentInfoNode objects, the StudentInfoNode.get_randomized_id function is used to randomize the data that is outputted.

##### Current implementation
UUID Module
https://docs.python.org/3/library/uuid.html

&nbsp;&nbsp;

### Other Notes
- Multiple calls using the same class data directory without the clean up flag is not allowed without manual deletion of extracted data
- No grade information should be downloaded.
- Data from each semester should be separated into folders containing bulk data zip files.


 &nbsp;&nbsp;