import os




def rename_iba_csv_files(folder_path):
    """
    Renames all CSV files in the given folder that start with "IBA_"
    by removing the "IBA_" prefix from their names.

    Args:
        folder_path (str): The path to the folder containing the files.
    """
    try:
        for filename in os.listdir(folder_path):
            if filename.startswith("IBA_DONE_") and filename.endswith(".xlsx"):
                old_filepath = os.path.join(folder_path, filename)
                new_filename = filename[len("IBA_DONE_"):].strip()  # Remove "IBA_" and any leading/trailing spaces
                new_filepath = os.path.join(folder_path, new_filename)

                if old_filepath != new_filepath:
                    os.rename(old_filepath, new_filepath)
                    print(f"Renamed '{filename}' to '{new_filename}'")
        print("CSV file renaming process completed.")
    except FileNotFoundError:
        print(f"Error: Folder not found at '{folder_path}'")
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    path_base = os.path.dirname(os.path.abspath(__file__))
    folder_path = os.path.join(path_base, 'untreated')
    # folder = input("Enter the path to the folder: ")
    rename_iba_csv_files(folder_path)