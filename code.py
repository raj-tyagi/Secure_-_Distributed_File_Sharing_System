import os
import shutil
import hashlib
from cryptography.fernet import Fernet

# Define constant variables for folders and file names
UPLOADS_FOLDER = "uploads"
ENCRYPTED_FOLDER = "encrypted"
KEY_FILE = "key.key"
VERSIONS_FOLDER = "versions"


class FileSharingServer:
    def __init__(self):
        # Ensure necessary folders and key file exist, if not, create them
        if not os.path.exists(UPLOADS_FOLDER):
            os.makedirs(UPLOADS_FOLDER)
        if not os.path.exists(ENCRYPTED_FOLDER):
            os.makedirs(ENCRYPTED_FOLDER)
        if not os.path.exists(VERSIONS_FOLDER):
            os.makedirs(VERSIONS_FOLDER)
        if not os.path.exists(KEY_FILE):
            # Generate a new encryption key if one doesn't exist
            key = Fernet.generate_key()
            with open(KEY_FILE, "wb") as key_file:
                key_file.write(key)
        else:
            # Load encryption key from file
            with open(KEY_FILE, "rb") as key_file:
                self.key = key_file.read()
                self.cipher = Fernet(self.key)

    def encrypt_file(self, file_name, data):
        # Encrypt file data and save it to the encrypted folder
        encrypted_data = self.cipher.encrypt(data)
        encrypted_file_path = os.path.join(ENCRYPTED_FOLDER, file_name)
        with open(encrypted_file_path, "wb") as file:
            file.write(encrypted_data)
        return encrypted_file_path

    def decrypt_file(self, file_name):
        # Decrypt file data
        encrypted_file_path = os.path.join(ENCRYPTED_FOLDER, file_name)
        with open(encrypted_file_path, "rb") as file:
            encrypted_data = file.read()
        decrypted_data = self.cipher.decrypt(encrypted_data)
        return decrypted_data

    def hash_file(self, data):
        # Generate SHA256 hash of file data
        hash_object = hashlib.sha256()
        hash_object.update(data)
        return hash_object.hexdigest()

    def upload_file(self, file_name, data, show_encryption_process=False):
        # Upload a file to the server
        file_path = os.path.join(UPLOADS_FOLDER, file_name)
        if os.path.exists(file_path):
            return None  # File already exists
        with open(file_path, "wb") as file:
            file.write(data)
        if show_encryption_process:
            # Show encryption process if requested
            print("Starting encryption process...")
            print("Step 1: Reading file content.")
            print("Step 2: Encrypting file content.")
        encrypted_file_path = self.encrypt_file(file_name, data)
        return file_name

    def download_file(self, file_name):
        # Download a file from the server
        file_path = os.path.join(UPLOADS_FOLDER, file_name)
        if os.path.exists(file_path):
            with open(file_path, "rb") as file:
                return file.read()
        else:
            return None

    def list_files(self):
        # List all files available on the server
        return os.listdir(UPLOADS_FOLDER)

    def create_version(self, file_name):
        # Create a version of the file
        file_path = os.path.join(UPLOADS_FOLDER, file_name)
        if os.path.exists(file_path):
            with open(file_path, "rb") as file:
                data = file.read()
            hash_value = self.hash_file(data)
            version_folder = os.path.join(VERSIONS_FOLDER, file_name)
            if not os.path.exists(version_folder):
                os.makedirs(version_folder)
            version_file_path = os.path.join(version_folder, hash_value)
            if not os.path.exists(version_file_path):
                shutil.copy(file_path, version_file_path)
                return True
        return False

    def remove_file(self, file_name):
        # Remove a file from the server
        file_path = os.path.join(UPLOADS_FOLDER, file_name)
        if os.path.exists(file_path):
            os.remove(file_path)
            return True
        else:
            return False


class FileSharingClient:
    def __init__(self, server):
        self.server = server

    def upload_file(self, file_path):
        # Upload a file to the server
        show_encryption_process = input("Do you want to see the encryption process? (yes/no): ").strip().lower() == 'yes'
        if not os.path.exists(file_path):
            print(f"File '{file_path}' not found.")
            return None
        file_name = os.path.basename(file_path)
        with open(file_path, "rb") as file:
            data = file.read()
        uploaded_file_name = self.server.upload_file(file_name, data, show_encryption_process=show_encryption_process)
        if uploaded_file_name:
            return uploaded_file_name
        else:
            print("File upload failed: File already exists on the server.")
            return None

    def download_file(self, file_name, destination_folder):
        # Download a file from the server
        while not os.path.exists(destination_folder):
            print("Destination folder does not exist.")
            destination_folder = input("Enter the destination folder path to save the downloaded file: ")
        if file_name:
            data = self.server.download_file(file_name)
            if data:
                file_path = os.path.join(destination_folder, file_name)
                with open(file_path, "wb") as file:
                    file.write(data)
                return file_path
            else:
                print(f"File '{file_name}' not found on the server.")
                return None
        else:
            print("File name not provided.")
            return None

    def list_files(self):
        # List all files available on the server
        return self.server.list_files()

    def create_version(self, file_name):
        # Create a version of the file
        return self.server.create_version(file_name)

    def remove_file(self, file_name):
        # Remove a file from the server
        return self.server.remove_file(file_name)


def get_user_choice():
    # Get user's choice for actions
    while True:
        choice = input("Enter 'U' to upload a file, 'D' to download a file, 'L' to list files, 'E' to view encrypted file, 'R' to remove a file, or 'Q' to quit: ").strip().upper()
        if choice in ('U', 'D', 'L', 'E', 'R', 'Q'):
            return choice
        else:
            print("Invalid choice. Please enter 'U', 'D', 'L', 'E', 'R', or 'Q'.")


if __name__ == "__main__":
    # Initialize server and client
    server = FileSharingServer()
    client = FileSharingClient(server)

    while True:
        user_choice = get_user_choice()

        if user_choice == 'U':
            # Upload a file
            file_path = input("Enter the file path to upload: ")
            uploaded_file_name = client.upload_file(file_path)
            if uploaded_file_name:
                print(f"File uploaded successfully: {uploaded_file_name}")
            else:
                print("File upload failed: File already exists on the server.")

        elif user_choice == 'D':
            # Download a file
            print("Files on server:", client.list_files())
            file_name = input("Enter the file name to download: ")
            destination_folder = input("Enter the destination folder path to save the downloaded file: ")
            downloaded_file_path = client.download_file(file_name, destination_folder)
            if downloaded_file_path:
                print(f"File downloaded successfully and saved to: {downloaded_file_path}")
            else:
                print(f"File '{file_name}' not found on the server.")

        elif user_choice == 'L':
            # List all files on the server
            print("Files on server:", client.list_files())

        elif user_choice == 'E':
            # View encrypted file data
            print("Files on server:", client.list_files())
            file_name = input("Enter the file name to view encrypted: ")
            encrypted_file_path = os.path.join(ENCRYPTED_FOLDER, file_name)
            if os.path.exists(encrypted_file_path):
                with open(encrypted_file_path, "rb") as file:
                    encrypted_data = file.read()
                print(f"Encrypted data: {encrypted_data}")
            else:
                print(f"File '{file_name}' not found on the server.")

        elif user_choice == 'R':
            # Remove a file from the server
            print("Files on server:", client.list_files())
            file_name = input("Enter the file name to remove from the server: ")
            if client.remove_file(file_name):
                print(f"File '{file_name}' removed successfully from the server.")
            else:
                print(f"File '{file_name}' not found on the server or removal failed.")

        elif user_choice == 'Q':
            # Quit the program
            print("Exiting...")
            break
