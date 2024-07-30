import sys
import os
import ftrack_api

def main():
    # Print message and exit unless a single argument is given
    if len(sys.argv) != 2:
        print("Usage: python script.py <directory>")
        sys.exit(1)

    directory = sys.argv[1]

    # Checks if the given variable is a directory and print message based on return
    if os.path.isdir(directory):
        print(f"{directory} exists")
    else:
        print(f"{directory} does not exist")

    # Information about the session
    session = ftrack_api.Session(server_url="https://hguy.ftrackapp.com",
                             api_user="haydenguyn@hotmail.com",
                             api_key="Mzg5MzI0NzUtMTFlMC00YTEzLWEyZmItNzY4N2Q0YTEwZGZlOjowNmVkNTRiOC1lMGQwLTRiYjMtOTVmYi0zMDZlZDczNjBlMmY")

    target_project_name = "Coding"

    # Find the first instance of project named {target_project_name}
    project = session.query(f"Project where name is {target_project_name}").first()

    # Print name and ID if project exists else print error 
    if project:
        print(f"Project Name: {project['name']} | ID: {project['id']}")
    else:
        print(f"No project with the name '{target_project_name}' could be found")

    session.close()

if __name__ == "__main__":
    main()