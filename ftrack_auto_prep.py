import sys
import os
import ftrack_api

# Information about the session
session = ftrack_api.Session(server_url="https://hguy.ftrackapp.com",
                             api_user="haydenguyn@hotmail.com",
                             api_key="Mzg5MzI0NzUtMTFlMC00YTEzLWEyZmItNzY4N2Q0YTEwZGZlOjowNmVkNTRiOC1lMGQwLTRiYjMtOTVmYi0zMDZlZDczNjBlMmY")

# Prints the names of the files in all folders and subfolders using recursion
def list_files_recursively(directory_path, indent_level=0):
    with os.scandir(directory_path) as entries:
        for entry in entries:
            if entry.is_dir():
                print(f"Directory: {entry.name}")
                list_files_recursively(entry.path, indent_level+1)
            elif entry.is_file():
                print(entry.name)

def get_target_project(project_name):
    # Find the first instance of project named {target_project_name}
    project = session.query(f"Project where name is {project_name}").first()

    # Print name and ID if project exists else print error 
    if project:
        print(f"Project Name: {project['name']} | ID: {project['id']}")
    else:
        print(f"No project with the name '{project_name}' could be found")

    session.close()

def main():
    # Print message and exit unless a single argument is given
    if len(sys.argv) != 2:
        print("Usage: python script.py <directory>")
        sys.exit(1)

    directory = sys.argv[1]

    # Checks if the directory exists. Prints message and exits script if not
    if not os.path.isdir(directory):
        print(f"{directory} does not exist")
        sys.exit(1)

    print("Enter the name of the project: ")
    target_project_name = input("")

    get_target_project(target_project_name)

    # list_files_recursively(directory)

if __name__ == "__main__":
    main()