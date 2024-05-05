# Secure - Distributed File Sharing System

Secure - Distributed File Sharing System is a prototype model for a secure file sharing system. This system facilitates file transfer within the local operating system environment. While it doesn't implement actual client-server socket programming, it provides a foundation for further enhancements to enable file transfer between different computers.

## Features

- **Secure Encryption**: Utilizes Fernet encryption from the cryptography library to encrypt files before uploading them to the server, ensuring data security during transfer and storage.
  
- **Versioning**: Supports versioning of files, allowing users to create multiple versions of a file and retain a history of changes.
  
- **Hashing**: Generates SHA256 hashes of file data, enabling integrity verification and ensuring files remain unaltered during transfer and storage.

- **User-friendly Interface**: Provides a simple command-line interface for users to upload, download, list files, view encrypted data, and remove files from the server.

### Prerequisites

- Python 3.x
- Required Python libraries: `cryptography`

### Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/your_username/Secure-Distributed-File-Sharing-System.git
   ```

2. Navigate to the project directory:
   ```bash
   cd Secure-Distributed-File-Sharing-System
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

### Usage

1. Run the program:
   ```bash
   python file_sharing_system.py
   ```

2. Follow the prompts to perform actions:
   - **U**: Upload a file
   - **D**: Download a file
   - **L**: List files on the server
   - **E**: View encrypted file data
   - **R**: Remove a file from the server
   - **Q**: Quit the program

### Example

```bash
Enter 'U' to upload a file, 'D' to download a file, 'L' to list files, 'E' to view encrypted file, 'R' to remove a file, or 'Q' to quit: U
Enter the file path to upload: /path/to/your/file.txt
Do you want to see the encryption process? (yes/no): yes
File uploaded successfully: file.txt
```

## Disclaimer

This project is a prototype model and does not implement actual client-server socket programming for distributed file sharing. Further enhancements would be required to enable file transfer between different computers over a network.

## License

This project is licensed under the [MIT License](LICENSE). 



## Contact

For any inquiries or feedback, please contact the project maintainer:

https://www.linkedin.com/in/raj-tyagi-83765b21b/

