import sys
import os
import ftrack_api
import json
import ffmpeg
from PIL import Image
import re

# Information about the session
session = ftrack_api.Session(server_url="https://haydenguy.ftrackapp.com",
                             api_user="spam.hguy@gmail.com",
                             api_key="NzlmMzJhNWEtYWRmZS00MmQ3LTlhZTEtZTE4YTM4OWIxYzU5Ojo3YzVmNDllYi03YmMzLTRlMjYtYjY5Zi1mOTYzZDg1NThjYjU")

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
                ftrack_builder(dir_path, project) # Recursively call the function to get the subfolders

# Get a dictionary of dir names:paths from a given path            
def get_directories(directory_path):
    directories = {}
    with os.scandir(directory_path) as entries:
        for entry in entries:
            if entry.is_dir():
                directories[entry.name] = entry.path

    return directories
                    
# Queries a project to see if it exists and runs the create_project if it doesnt
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
def create_task(name, parent, type=None):
    # Type ID's for each of the task types
    task_name_id = {
        "Animation": "44dc3636-4164-11df-9218-0019bb4983d8",
        "Audio_Mix": "a557384c-a5b5-4aec-b192-2049db0975d1",
        "Brand_Assets": "bec6a235-717f-4225-8d9f-bde3a7fd2667",
        "Character": "66d145f0-13c6-11e3-abf2-f23c91dfaa16",
        "Color": "d410af88-73e9-4a2f-be54-dabb3fd09f50",
        "Compositing": "44dd23b6-4164-11df-9218-0019bb4983d8",
        "Concept_Art": "56807358-a0f4-11e9-9843-d27cf242b68b",
        "Conform": "a3ead45c-ae42-11e9-9454-d27cf242b68b",
        "Deliverable": "ae1e2480-f24e-11e2-bd1f-f23c91dfaa16",
        "Editing": "cc46c4c6-13d2-11e3-8915-f23c91dfaa16",
        "Environment": "66d1daba-13c6-11e3-abf2-f23c91dfaa16",
        "Furniture": "0e996e82-6662-11ed-a73a-92ba0fc0dc3d",
        "FX": "44dcea86-4164-11df-9218-0019bb4983d8",
        "Layout": "ffaebf7a-9dca-11e9-8346-d27cf242b68b",
        "Lighting": "44dd08fe-4164-11df-9218-0019bb4983d8",
        "Long_Form": "20b1c08e-dea7-468c-a72d-0817ee2ed6ec",
        "Lookdev": "44dc8cd0-4164-11df-9218-0019bb4983d8",
        "Matte_Painting": "66d2038c-13c6-11e3-abf2-f23c91dfaa16",
        "Modeling": "44dc53c8-4164-11df-9218-0019bb4983d8",
        "Music": "8233270a-14ac-4802-9e47-2e7a774563c0",
        "News": "387efc10-d040-4cb4-bfdd-47e8995f0cef",
        "Previz": "44dc6ffc-4164-11df-9218-0019bb4983d8",
        "Production": "b628a004-ad7d-11e1-896c-f23c91df1211",
        "Prop": "66d1aedc-13c6-11e3-abf2-f23c91dfaa16",
        "Rendering": "262225e8-9dcb-11e9-82b8-d27cf242b68b",
        "Rigging": "44dd5868-4164-11df-9218-0019bb4983d8",
        "Rotoscoping": "c3bcfdb4-ad7d-11e1-a444-f23c91df1211",
        "Short_Form": "d1aa3488-299e-45d1-8469-51fa1b10cebe",
        "Social": "a566a954-ee06-487f-a1db-3103cfb62ec2",
        "Sports": "32617c36-dc40-4bd2-8ae0-375194ae8616",
        "Texture": "a750a84f-b253-11eb-ad41-1e003a0c2434",
        "Tracking": "44dd3ed2-4164-11df-9218-0019bb4983d8",
        "Vehicle": "8c39f908-8b4c-11eb-9cdb-c2ffbce28b68",
        "Video_Shoot": "b7df1bd9-9268-42ea-8be2-6b99abc1730f",
        "Voice_Over": "2ea3363d-8617-4e45-ad23-ae678ec50b43"
    }
    
    task_type = task_name_id.get(type) # Gets the type ID for the passed type

    if task_type == None: # If type ID is not found (None) this item is skipped and not added to ftrack
        return

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
            asset_obj = create_asset_build(asset, build_type, project) # Creates the asset builds based on the name and type is based on the folder it is in (i.e. Character)
            asset_dir = (f"{path}/{build_type}/{asset}")

            tasks = os.listdir(f"{path}/{build_type}/{asset}") # Get list of the dirs within an asset build dir

            for task in tasks:
                _, extension = os.path.splitext(task)
                if extension == ".png":
                    set_thumbnail("AssetBuild", asset_obj["id"], asset_dir)
                else:
                    ftrack_task = create_task(task, asset_obj, task) # Create task objects in ftrack
                    task_dir = (f"{path}/{build_type}/{asset}/{task}")
                    try:
                        set_thumbnail("Task", ftrack_task["id"], task_dir)
                    except TypeError:
                        pass
                    
                    try:
                        _, image_paths = get_file_paths(task_dir) # Gets the full path of the img files in the task_dir. _ is videos
                        for img in image_paths:
                            ftrack_upload_media_file(img, ftrack_task["id"]) # Uploads the media associated with the respective task ID
                    except NotADirectoryError:
                        pass

# Search through the Sequence subfolders to create ftrack object for Sequences, Shots, and Tasks
def ftrack_sequence_build(path, project):
    sequences = os.listdir(path)
    for seq in sequences:
        create_sequence(seq, project) # Create the sequence objects in ftrack
        sequence_obj = session.query(f"Sequence where name is '{seq}'").first() # Query the sequence name and return its object on ftrack
        shots = os.listdir(f"{path}/{seq}") # Get list of shot dirs within a sequence dir

        for shot in shots:
            _, extension = os.path.splitext(shot)
            if extension == ".png":
                pass
            else:
                ftrack_shot = create_shot(shot, sequence_obj) # Create the shot objects in ftrack

                shot_obj = session.query(f"Shot where name is {shot}").first() # Query the shot name and return its object on ftrack
                shot_dir = (f"{path}/{seq}/{shot}")
                
                try:
                    set_thumbnail("Shot", ftrack_shot["id"], shot_dir)                
                except TypeError:
                    pass

                tasks = os.listdir(f"{path}/{seq}/{shot}") # Get a list of the task dirs within the shot dir

                for task in tasks:
                    ftrack_task = create_task(task, shot_obj, task) # Create the task objects in ftrack and return the task
                    task_dir = (f"{path}/{seq}/{shot}/{task}") 

                    try:
                        set_thumbnail("Task", ftrack_task["id"], task_dir)
                    except TypeError:
                        pass
                    video_paths, _ = get_file_paths(task_dir) # Gets the full path of the video files in the task_dir. _ is image paths

                    for vid in video_paths:
                        ftrack_upload_media_file(vid, ftrack_task["id"]) # Uploads the media associated with the respective task ID

# Gets the full file path for the mp4 or pngs in a directory and returns them as as list 
def get_file_paths(directory):
    videos = [os.path.join(directory, vid) for vid in os.listdir(directory) if vid.endswith(".mp4") and vid]
    images = [os.path.join(directory, img) for img in os.listdir(directory) if img.endswith(".png") and img]

    return videos, images

# Create an ftrack asset and asset version object
def ftrack_create_asset_and_asset_version(name, task):
    task = session.query(f"Task where id is '{task}'").one()
    asset_parent = task["parent"]
    asset_type = session.query("AssetType where name is 'Upload'").one()

    # Create an asset with name of the paths file name e.g. my_mov.mp4
    asset = session.create("Asset", {
        "name": name,
        "type": asset_type,
        "parent": asset_parent
    })

    asset_version = session.create("AssetVersion", {
        "asset": asset,
        "task": task
    })

    session.commit()

    return asset_version

# Sets the thumbnail by taking the directory/thumbnail file and attaching it to the queried object
def set_thumbnail(object_type, object_id, dir):
    pattern = r".*_thumbnail\.png$" # Regex pattern to get only files that end in _thumbnail.png
    _, images = get_file_paths(dir) # Gets the file paths in the given dir

    thumbnail = [path for path in images if re.search(pattern, path)] # Finds the _thumbnail.png using regex
    
    object = session.query(f"{object_type} where id is '{object_id}'").one()
    
    try: # Create the thumbnail if one exists: there should be only one thumbnail per folder
        object.create_thumbnail(thumbnail[0])
        session.commit()
    except IndexError: # If there is no thumbnail list will be empty [] so we return
        return
    
# Return video metadata for use in media upload
def get_video_metadata(file_path):
    probe = ffmpeg.probe(file_path) # Gets video info with ffmpeg

    # Gets the video stream (video data)
    video_stream = next((stream for stream in probe["streams"] if stream["codec_type"] == "video"), None)

    if not video_stream:
        return "No video stream found"
    
    # Extract width and height
    width = int(video_stream["width"])
    height = int(video_stream["height"])

    # Calculate frame rate
    frame_rate_str = video_stream["r_frame_rate"]
    numerator, denominator = map(int, frame_rate_str.split("/"))
    frame_rate = numerator / denominator

    # Get duration and calculate frame out
    duration = float(probe["format"]["duration"])
    frame_out = int(frame_rate * duration)
    frame_in = 0

    return width, height, frame_rate, frame_in, frame_out

# Create an ftrack video component for an asset version
def ftrack_create_video_component(asset_version, path, frame_rate, frame_in, frame_out, vid_width, vid_height):
    location = session.query("Location where name is 'ftrack.server'").one() # Sets the location to the ftrack.server
    
    component = asset_version.create_component( # Calls the asset version create_component function
        path = path,
        data = {
            "name": "ftrackreview-mp4"
        },
        location = location # Can use a custom defined location if wanted 
    )

    # Define the metadata for the video to use in the web player
    component["metadata"]["ftr_meta"] = json.dumps({
        "frameIn": frame_in,
        "frameOut": frame_out,
        "frameRate": frame_rate,
        "width": vid_width,
        "height": vid_height
    })

    session.commit()

# Return image metadata for use in media upload
def get_image_metadata(file_path):
    with Image.open(file_path) as img:
        width, height = img.size

    return width, height

# Create an ftrack image component for an asset version
def ftrack_create_image_component(asset_version, path, width, height):
    location = session.query("Location where name is 'ftrack.server'").one()

    component = asset_version.create_component( # Calls the asset version create_component function
        path = path, 
        data = {
            "name": "ftrackreview-image"
        },
        location = location
    )

    # Define the metadata for the image to use in the web player
    component["metadata"]["ftr_meta"] = json.dumps({
        "format": "image",
        "width": width,
        "height": height
    })
    
    session.commit()

# Uploads the media file to ftrack based on the path and task ID
def ftrack_upload_media_file(path, task):
    base_file = os.path.basename(path) # File name
    extension = os.path.splitext(base_file)[1] # File extension

    asset_version = ftrack_create_asset_and_asset_version(base_file, task)

    if extension == ".mp4":
        vid_width, vid_height, frame_rate, frame_in, frame_out = get_video_metadata(path)
        ftrack_create_video_component(asset_version, path, frame_rate, frame_in, frame_out, vid_width, vid_height)
    elif extension == ".png":
        width, height = get_image_metadata(path)
        ftrack_create_image_component(asset_version, path, width, height)

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
    set_thumbnail("Project", project["id"], directory)

    ftrack_builder(directory, project)

if __name__ == "__main__":
    main()