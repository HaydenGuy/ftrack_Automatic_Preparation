import sys
import os
import ftrack_api

# Information about the session
session = ftrack_api.Session(server_url="https://hguy.ftrackapp.com",
                             api_user="haydenguyn@hotmail.com",
                             api_key="Mzg5MzI0NzUtMTFlMC00YTEzLWEyZmItNzY4N2Q0YTEwZGZlOjowNmVkNTRiOC1lMGQwLTRiYjMtOTVmYi0zMDZlZDczNjBlMmY")

# Calls the ftrack builder functions to create ftrack objects based on the dirs passed
def ftrack_builder(directory_path, project):
    directories = get_directories(directory_path)

    for dir_name in directories:
        dir_path = directories[dir_name]

        match dir_name:
            case "Asset_Builds":
                ftrack_asset_build(dir_path, project)
            case "Sequences":
                ftrack_sequence_build(dir_path, project)
            case _:
                directories = get_directories(directory_path) # Recursively call the function to get the subfolders

# Get a dictionary of dir names:paths from a given path            
def get_directories(directory_path):
    directories = {}
    with os.scandir(directory_path) as entries:
        for entry in entries:
            if entry.is_dir():
                directories[entry.name] = entry.path

    return directories
                    
# Queries a project Name and ID then prints the project name and ID
def get_target_project(project_name):
    # Find the first instance of project named {target_project_name}
    project = session.query(f"Project where name is {project_name}").first()

    # If project doesn't exist run the create_project function and query the project again
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

    try:
        asset_build = session.create("AssetBuild", {
            "name": name,
            "parent": parent,
            "type_id": asset_type
        })

        session.commit()

    # if DuplicateEntryError a message will be printed and script will end
    except ftrack_api.exception.ServerError as e:
        if "DuplicateEntry" in str(e):
            sys.exit()

    return asset_build

# Creates a Sequence object
def create_sequence(name, parent):
    try:
        sequence = session.create("Sequence", {
            "name": name,
            "parent": parent
        })

        session.commit()

    # if DuplicateEntryError a message will be printed and script will end
    except ftrack_api.exception.ServerError as e:
        if "DuplicateEntry" in str(e):
            sys.exit()

    return sequence

# Creates a Shot object
def create_shot(name, parent):
    try:
        shot = session.create("Shot", {
            "name": name,
            "parent": parent
        })

        session.commit()

    # if DuplicateEntryError a message will be printed and script will end
    except ftrack_api.exception.ServerError as e:
        if "DuplicateEntry" in str(e):
            sys.exit()

    return shot

# Create a Task object
def create_task(name, type, parent):
    # Type ID's for each of the task types
    options = {"Animation": "44dc3636-4164-11df-9218-0019bb4983d8",
               "Rendering": "262225e8-9dcb-11e9-82b8-d27cf242b68b"
    }
    
    task_type = options.get(type) # Gets the type ID for the passed type

    try:
        task = session.create("Task", {
            "name": name,
            "parent": parent,
            "type_id": task_type
        })

        session.commit()

    # if DuplicateEntryError a message will be printed and script will end
    except ftrack_api.exception.ServerError as e:
        if "DuplicateEntry" in str(e):
            sys.exit()

    return task

# Search through the Asset_Build subfolders and then create ftrack objects from that
def ftrack_asset_build(path, project):
    build_types = os.listdir(path)
    for build_type in build_types:
        asset_builds = os.listdir(f"{path}/{build_type}") # List the folders within the Asset_Builds subfolders

        for asset in asset_builds:
            create_asset_build(asset, build_type, project) # Creates the asset builds based on the name and type is based on the folder it is in (i.e. Character)

# Search through the Sequence subfolders to create ftrack object for Sequences, Shots, and Tasks
def ftrack_sequence_build(path, project):
    sequences = os.listdir(path)
    for seq in sequences:
        create_sequence(seq, project) # Create the sequence objects in ftrack
        sequence_obj = session.query(f"Sequence where name is '{seq}'").one() # Query the sequence name and return its object on ftrack
        shots = os.listdir(f"{path}/{seq}") # Get list of shot dirs within a sequence dir

        for shot in shots:
            create_shot(shot, sequence_obj) # Create the shot objects in ftrack
            shot_obj = session.query(f"Shot where name is {shot}").one() # Query the shot name and return its object on ftrack
            tasks = os.listdir(f"{path}/{seq}/{shot}") # Get a list of the task dirs within the shot dir

            for task in tasks:
                create_task(task, task, shot_obj) # Create the task objects in ftrack

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

    ftrack_builder(directory, project)

if __name__ == "__main__":
    main()