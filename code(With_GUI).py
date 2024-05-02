import os
import shutil
import hashlib
from cryptography.fernet import Fernet
from PyQt5 import QtWidgets, QtGui, QtCore
from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QLabel, QFileDialog, QMessageBox

UPLOADS_FOLDER = "uploads"
ENCRYPTED_FOLDER = "encrypted"
KEY_FILE = "key.key"
VERSIONS_FOLDER = "versions"


class FileSharingServer:
    def __init__(self):
        if not os.path.exists(UPLOADS_FOLDER):
            os.makedirs(UPLOADS_FOLDER)
        if not os.path.exists(ENCRYPTED_FOLDER):
            os.makedirs(ENCRYPTED_FOLDER)
        if not os.path.exists(VERSIONS_FOLDER):
            os.makedirs(VERSIONS_FOLDER)
        if not os.path.exists(KEY_FILE):
            key = Fernet.generate_key()
            with open(KEY_FILE, "wb") as key_file:
                key_file.write(key)
        else:
            with open(KEY_FILE, "rb") as key_file:
                self.key = key_file.read()
                self.cipher = Fernet(self.key)

    def encrypt_file(self, file_name, data):
        encrypted_data = self.cipher.encrypt(data)
        encrypted_file_path = os.path.join(ENCRYPTED_FOLDER, file_name)
        with open(encrypted_file_path, "wb") as file:
            file.write(encrypted_data)
        return encrypted_file_path

    def decrypt_file(self, file_name):
        encrypted_file_path = os.path.join(ENCRYPTED_FOLDER, file_name)
        with open(encrypted_file_path, "rb") as file:
            encrypted_data = file.read()
        decrypted_data = self.cipher.decrypt(encrypted_data)
        return decrypted_data

    def hash_file(self, data):
        hash_object = hashlib.sha256()
        hash_object.update(data)
        return hash_object.hexdigest()

    def upload_file(self, file_name, data, show_encryption_process=False):
        file_path = os.path.join(UPLOADS_FOLDER, file_name)
        if os.path.exists(file_path):
            return None  # File already exists
        with open(file_path, "wb") as file:
            file.write(data)
        if show_encryption_process:
            print("Starting encryption process...")
            print("Step 1: Reading file content.")
            print("Step 2: Encrypting file content.")
        encrypted_file_path = self.encrypt_file(file_name, data)
        return file_name

    def download_file(self, file_name):
        file_path = os.path.join(UPLOADS_FOLDER, file_name)
        if os.path.exists(file_path):
            with open(file_path, "rb") as file:
                return file.read()
        else:
            return None

    def list_files(self):
        return os.listdir(UPLOADS_FOLDER)

    def create_version(self, file_name):
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


class FileSharingClient:
    def __init__(self, server):
        self.server = server

    def upload_file(self, file_path):
        show_encryption_process = QMessageBox.question(None, "Encryption Process", "Do you want to see the encryption process?", QMessageBox.Yes | QMessageBox.No)
        if show_encryption_process == QMessageBox.Yes:
            show_encryption_process = True
        else:
            show_encryption_process = False
        
        if not os.path.exists(file_path):
            QMessageBox.critical(None, "File Not Found", f"File '{file_path}' not found.")
            return None
        file_name = os.path.basename(file_path)
        with open(file_path, "rb") as file:
            data = file.read()
        uploaded_file_name = self.server.upload_file(file_name, data, show_encryption_process=show_encryption_process)
        if uploaded_file_name:
            return uploaded_file_name
        else:
            QMessageBox.critical(None, "File Upload Failed", "File already exists on the server.")
            return None

    def download_file(self, file_name, destination_folder):
        while not os.path.exists(destination_folder):
            QMessageBox.critical(None, "Folder Not Found", "Destination folder does not exist.")
            destination_folder = QFileDialog.getExistingDirectory(None, "Select Destination Folder")
        if file_name:
            data = self.server.download_file(file_name)
            if data:
                file_path = os.path.join(destination_folder, file_name)
                with open(file_path, "wb") as file:
                    file.write(data)
                return file_path
            else:
                QMessageBox.critical(None, "File Not Found", f"File '{file_name}' not found on the server.")
                return None
        else:
            QMessageBox.critical(None, "File Name Not Provided", "File name not provided.")
            return None

    def list_files(self):
        return self.server.list_files()

    def create_version(self, file_name):
        return self.server.create_version(file_name)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("File Sharing Application")

        self.choice_label = QLabel("Choose an option:", self)
        self.choice_label.setGeometry(50, 50, 500, 50)
        self.choice_label.setAlignment(QtCore.Qt.AlignCenter)
        self.choice_label.setStyleSheet("font-size: 20px; font-weight: bold;")

        self.output_label = QLabel("", self)
        self.output_label.setGeometry(50, 200, 500, 100)  # Adjust size as needed
        self.output_label.setAlignment(QtCore.Qt.AlignCenter)
        self.output_label.setStyleSheet("font-size: 16px;")
        self.output_label.setWordWrap(True)  # Enable word wrap
        self.output_label.setScaledContents(True)  # Enable scaling

        self.choice_button = QPushButton("Submit", self)
        self.choice_button.setGeometry(225, 150, 150, 30)
        self.choice_button.setStyleSheet("font-size: 14px;")
        self.choice_button.clicked.connect(self.handle_choice)

        self.previous_executions_label = QLabel("Previous Executions:", self)
        self.previous_executions_label.setGeometry(50, 350, 500, 30)
        self.previous_executions_label.setStyleSheet("font-size: 16px; font-weight: bold;")

        self.previous_executions_text = QLabel("", self)
        self.previous_executions_text.setGeometry(50, 400, 500, 150)  # Adjust size as needed
        self.previous_executions_text.setStyleSheet("font-size: 14px;")
        self.previous_executions_text.setWordWrap(True)  # Enable word wrap
        self.previous_executions_text.setScaledContents(True)  # Enable scaling

        self.previous_executions = []

    def handle_choice(self):
        user_choice, ok = QtWidgets.QInputDialog.getText(self, 'User Choice', "Enter 'U' to upload a file, 'D' to download a file, 'L' to list files, 'E' to view encrypted file, or 'Q' to quit:")
        if ok:
            self.choice_var = user_choice.strip().upper()
            client = FileSharingClient(server)
            if self.choice_var == 'U':
                file_path, _ = QFileDialog.getOpenFileName(self, "Select File to Upload")
                if file_path:
                    uploaded_file_name = client.upload_file(file_path)
                    if uploaded_file_name:
                        self.output_label.setText(f"File uploaded successfully: {uploaded_file_name}")
                        self.previous_executions.append(f"Uploaded file: {uploaded_file_name}")
            elif self.choice_var == 'D':
                files = client.list_files()
                if files:
                    file_name, ok = QtWidgets.QInputDialog.getItem(self, "File Name", "Files on server:", files, 0, False)
                    if ok:
                        destination_folder = QFileDialog.getExistingDirectory(self, "Select Destination Folder")
                        if destination_folder:
                            downloaded_file_path = client.download_file(file_name, destination_folder)
                            if downloaded_file_path:
                                self.output_label.setText(f"File downloaded successfully and saved to: {downloaded_file_path}")
                                self.previous_executions.append(f"Downloaded file: {file_name}")
                        else:
                            self.output_label.setText("Destination folder not selected.")
                else:
                    self.output_label.setText("No files found on the server.")
            elif self.choice_var == 'L':
                files = client.list_files()
                if files:
                    self.output_label.setText("Files on server:\n" + "\n".join(files))
                    self.previous_executions.append("Listed files")
                else:
                    self.output_label.setText("No files found on the server.")
            elif self.choice_var == 'E':
                files = client.list_files()
                if files:
                    file_name, ok = QtWidgets.QInputDialog.getItem(self, "File Name", "Files on server:", files, 0, False)
                    if ok:
                        encrypted_file_path = os.path.join(ENCRYPTED_FOLDER, file_name)
                        if os.path.exists(encrypted_file_path):
                            with open(encrypted_file_path, "rb") as file:
                                encrypted_data = file.read()
                            self.output_label.setText(f"Encrypted data: {encrypted_data}")
                            self.previous_executions.append(f"Viewed encrypted data of file: {file_name}")
                        else:
                            self.output_label.setText(f"File '{file_name}' not found on the server.")
                else:
                    self.output_label.setText("No files found on the server.")
            elif self.choice_var == 'Q':
                quit_msg = "Are you sure you want to quit?"
                reply = QMessageBox.question(self, 'Message', quit_msg, QMessageBox.Yes, QMessageBox.No)
                if reply == QMessageBox.Yes:
                    self.output_label.setText("Exiting...")
                    self.previous_executions.append("Exited the application.")
                    self.close()
        self.update_previous_executions()

    def update_previous_executions(self):
        self.previous_executions_text.setText("\n".join(self.previous_executions))
        for execution in self.previous_executions:
            print(execution)


if __name__ == "__main__":
    app = QApplication([])
    server = FileSharingServer()
    window = MainWindow()
    window.setGeometry(200, 200, 800, 800)
    window.show()
    app.exec_()
