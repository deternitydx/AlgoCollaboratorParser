import argparse

from Parser.CollaboratorsParser import CollaboratorsParser

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

    args = set_commandline_args()

    algo_class = CollaboratorsParser(args.class_data_directory)

    if not algo_class.is_valid():
        return

    algo_class.extract_bulk_downloads()

    algo_class.map_students()
    
    algo_class.generate_collaborators()

    # algo_class.output_to_file(args.output_file)

    if args.cleanup:
        algo_class.cleanup()



if __name__ == "__main__":
    main()
