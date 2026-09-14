from pyftpdlib.authorizers import DummyAuthorizer
from pyftpdlib.handlers import FTPHandler
from pyftpdlib.servers import FTPServer
import os
import utils.constants

# Define the directory where you want to store files
FTP_WORKING_DIRECTORY = os.path.join(utils.constants.LLM_WORKING_FOLDER, "ftp_server")
os.makedirs(FTP_WORKING_DIRECTORY, exist_ok=True)

# Instantiate a dummy authorizer for managing 'virtual' users
authorizer = DummyAuthorizer()

# Add user permissions based on local environment variables.
ftp_user = utils.constants.FTP_SERVER_USER
ftp_pass = utils.constants.FTP_SERVER_PASS

if not ftp_user or not ftp_pass:
    raise RuntimeError(
        "FTP_SERVER_USER and FTP_SERVER_PASS must be set in .env before starting the FTP server."
    )

authorizer.add_user(ftp_user, ftp_pass, FTP_WORKING_DIRECTORY, perm="elradfmw")

# Instantiate FTP handler class
handler = FTPHandler
handler.authorizer = authorizer

# Define a custom banner (optional)
handler.banner = "Welcome to my FTP server."

# Specify the address and port for the server to listen on
address = ("", 2100)  # Listen on all interfaces

# Create FTP server instance and start serving
server = FTPServer(address, handler)
