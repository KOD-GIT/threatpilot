import os
import shutil
import utils.constants

# Get path to the script folder and resolve working folder
script_folder = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(script_folder, ".."))
working_folder = os.path.abspath(
    os.path.join(project_root, utils.constants.LLM_WORKING_FOLDER)
)

llm_config = {
    "model": utils.constants.OPENAI_MODEL_NAME,
    "api_key": utils.constants.OPENAI_API_KEY,
    "cache_seed": None,
}


def clean_working_directory(agent_subfolder: str):
    # Normalize subfolder name
    clean_subfolder = agent_subfolder.lstrip("/\\")
    working_subfolder = os.path.join(working_folder, clean_subfolder)

    # Avoid accidental deletion of root or parent folder
    if not clean_subfolder or os.path.abspath(working_subfolder) == project_root:
        return

    # If folder does not exist, create it
    if not os.path.exists(working_subfolder):
        os.makedirs(working_subfolder, exist_ok=True)
        return

    # Loop through all items in the folder and clear them
    for filename in os.listdir(working_subfolder):
        file_path = os.path.join(working_subfolder, filename)
        try:
            if os.path.isfile(file_path) or os.path.islink(file_path):
                os.unlink(file_path)
            elif os.path.isdir(file_path):
                shutil.rmtree(file_path)
        except Exception as e:
            print(f"Failed to delete {file_path}. Reason: {e}")
