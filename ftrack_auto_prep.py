import sys
import os
import ftrack_api

# Information about the session
session = ftrack_api.Session(server_url="https://hguy.ftrackapp.com",
                             api_user="haydenguyn@hotmail.com",
                             api_key="Mzg5MzI0NzUtMTFlMC00YTEzLWEyZmItNzY4N2Q0YTEwZGZlOjowNmVkNTRiOC1lMGQwLTRiYjMtOTVmYi0zMDZlZDczNjBlMmY")

# Gets names of the directories in argv[1] folder and subfolders using recursion
def list_files_recursively(directory_path, project, indent_level=0):
    with os.scandir(directory_path) as entries:
        for entry in entries:
            if entry.is_dir():
                if entry.name == "Asset_Builds": 
                    build_types = os.listdir(entry.path) # Lists the dirs within Asset_Builds
                    for build_type in build_types:
                        asset_builds = os.listdir(f"{entry.path}/{build_type}") # List the folders within the Asset_Builds subfolders
                        for asset in asset_builds:
                            create_asset_build(asset, build_type, project) # Creates the asset builds based on the name and type is based on the folder it is in (i.e. Character)
                elif entry.name == "Sequences":
                    sequences = os.listdir(entry.path)
                    for seq in sequences:
                        create_sequence(seq, project)
                else:
                    list_files_recursively(entry.path, indent_level+1)
                

# Queries a project Name and ID then prints the project name and ID
def get_target_project(project_name):
    # Find the first instance of project named {target_project_name}
    project = session.query(f"Project where name is {project_name}").first()

    # If project doesn't exist run the create_project function, call query again and close the session
    if not project:
        create_project(project_name)
        project = session.query(f"Project where name is {project_name}").first()
    
    return project

# Creates a new ftrack project if user chooses 'y'. If 'n' closes the session and exits the script
def create_project(project_name):
    print(f"Project not found: {project_name}\n")

    user_choice = ""

    while user_choice not in ("y", "n"):
        print("Would you like to create a new project? y/n")
        user_choice = input()

    match user_choice:
        case "y":
            project_code = input("Please enter a project code (eg. PROJ-001): ")

            session.create("Project", {
                "name": project_name,
                "full_name": project_name,
                'project_code': project_code,
            })

            session.commit()
        case "n":
            session.close()
            sys.exit()

# Creates an Asset Build object based on the folder the asset is in
def create_asset_build(name, type, parent):
    # Type ID's for each of the asset build types
    options = {"Character": "66d145f0-13c6-11e3-abf2-f23c91dfaa16",
               "Prop": "66d1aedc-13c6-11e3-abf2-f23c91dfaa16",
               "Vehicle": "8c39f908-8b4c-11eb-9cdb-c2ffbce28b68",
               "Environment": "66d1daba-13c6-11e3-abf2-f23c91dfaa16",
               "Matte_Painting": "66d2038c-13c6-11e3-abf2-f23c91dfaa16"}
    
    asset_type = options.get(type) # Gets the type ID for the passed type

    asset_build = session.create("AssetBuild", {
        "name": name,
        "parent": parent,
        "type_id": asset_type
    })

    # TODO Add error checking for duplicate entry

    session.commit()

    return asset_build

# Creates a Sequence object
def create_sequence(name, parent):
    sequence = session.create("Sequence", {
        "name": name,
        "parent": parent
    })

    session.commit()

    return sequence

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

    project = get_target_project(target_project_name)

    list_files_recursively(directory, project)

if __name__ == "__main__":
    main()