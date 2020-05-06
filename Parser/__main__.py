import argparse
import logging
from Parser.CollaboratorsParser import CollaboratorsParser

# Setup logging
logger = logging.getLogger(__name__)

# Commandline args setup
def set_commandline_args():
    commandline_args = argparse.ArgumentParser()

    commandline_args.add_argument("class_data_directory",
                                  help="Directory containing bulk_down.zip files from Collab",
                                  )

    commandline_args.add_argument("output_file",
                                  help="Filename for output containing collaborator graph data (Ex: AlgorithmsFall2018.txt)",
                                  )

    commandline_args.add_argument("-c",
                                  "--cleanup",
                                  action="store_true",
                                  help="Removes any files extracted during parsing and restores root_dir to original state",
                                  )

    return commandline_args.parse_args()



def main():
    # Gets command line args
    args = set_commandline_args()

    # Initialize parser obj
    algo_class = CollaboratorsParser(args.class_data_directory)

    # Stops if class dir is in unexpected initial state
    if not algo_class.is_valid():
        return
    
    # Extracts nested zip files
    algo_class.extract_bulk_downloads()



    # Reads path names and maps students to StudentInfoNode instances
    algo_class.map_students()

    # Reads latex files and maps creates collaborators graph with mapped StudentInfoNode
    algo_class.generate_collaborators()


    algo_class.output_to_file(args.output_file)

    if args.cleanup:
        algo_class.cleanup()


    logger.info("File Generated: parser.log")


if __name__ == "__main__":
    main()
