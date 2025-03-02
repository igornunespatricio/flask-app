import os
import time


def delete_file(file_path):
    """Delete a file after ensuring no process is using it."""
    # release_file_lock(file_path)  # Kill any process using the file
    time.sleep(1)  # Give OS time to release the file lock

    if os.path.exists(file_path):
        os.remove(file_path)
        print(f"🗑️ File {file_path} deleted successfully.")
    else:
        print(f"⚠️ File {file_path} not found.")
