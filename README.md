Script will upload the asset builds, sequences, shots and tasks into their respective objects on ftrack. User will be asked if they want to create a new project if one doesn't exist.

Files and folders must be setup in a similar structure to below. For Asset Builds the character will be used as the example but all will follow the same folder structure. See video for more details.

Ensure thumbnails are named as _thumbnail.png. If no thumbnail is present the object parent thumbnail will be used.

- Project_Folder
  - Asset_Builds 
    - Character
      - character_name _**This will be an ftrack Asset Build (Character)**_
        - Concept_Art _**This will be an ftrack Task**_
          - character_concept_thumbnail.png
          - character_concept_v1.png
        - Modeling
        - Texture
        - character_name_thumbnail.png
      - character_name
    - Environment
      - environment_name _**This will be an ftrack Asset Build (Environment)**_
    - Matte_Painting
      - matte_painting_name _**This will be an ftrack Asset Build (Matte Painting)**_
    - Prop
      - prop_name _**This will be an ftrack Asset Build (Prop)**_
    - Vehicle
      - vehicle_name _**This will be an ftrack Asset Build (Vehicle)**_
  - Sequences _**This will be an ftrack Sequence**_
    - Scene01 _**This will be an ftrack Scene**_
      - S01_01 _**This will be an ftrack Shot**_
        - Animation _**This will be an ftrack Task**_
          - S01_01_anim_thumbnail.png
          - S01_01_anim_v1.png
        - Rendering
      - S01_02
      - scene01_thumbnail.png
    - Scene02
  - project_thumbnail.png
    
https://github.com/user-attachments/assets/0f376c67-996d-48e9-85c8-efda7ab2bb56
