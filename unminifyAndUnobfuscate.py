import sys
import requests
import os
import uuid
import re
import time
import random
import string


# Define both variables as global so that they can be used in other functions
expires_at = 0
auth_token = ""


def authTokenOrFile(argument):
    global auth_token  # Use the global variable

    # Based on the argument, either use the auth token or read it from the file
    if argument == "-t":
        auth_token = sys.argv[2]
        sendAuthorizationRequest(auth_token)
    elif argument == "-f":
        isFileWithAuthToken(sys.argv[2])


def isFileWithAuthToken(auth_token_file):
    global auth_token  # Use the global variable

    auth_token_file = os.path.realpath(auth_token_file)  # Get the real path to the file

    if os.path.exists(auth_token_file):
        with open(auth_token_file, "r") as auth_token_file:
            auth_token = auth_token_file.read().replace('\n', '')  # Read the file and remove the new line character

        sendAuthorizationRequest(auth_token)
    else:
        print("File " + auth_token_file + " does not exist.")
        sys.exit(1)


def sendAuthorizationRequest(auth_token):
    global expires_at  # Use the global variable

    # print("Current time: ", time.time())
    # print("expires_at time: ", expires_at)

    if expires_at < time.time():  # If the token has expired, send the authorization request
        print("Sending authorization GET request...")
        url = "https://api.github.com/copilot_internal/v2/token"
        headers = {
            "Host": "api.github.com",
            "Authorization": "token " + auth_token,
            "Editor-Version": "vscode/1.84.2",
            "Editor-Plugin-Version": "copilot-chat/0.10.2",
            "User-Agent": "GitHubCopilotChat/0.10.2",
            "Accept": "*/*",
            "Accept-Encoding": "gzip, deflate, br"
        }
        response = requests.get(url, headers=headers)
        # print("Response: " + str(response.text))

        if response.status_code == 200:  # If the authorization was successful, save the token and expiresAt time
            expires_at = response.json()["expires_at"]
            token = response.json()["token"]
            isPathValid(token, sys.argv[3])
        else:
            print("Authorization failed. Response: " + str(response.text))
            sys.exit(1)
    else:
        pass  # If the token has not expired, continue with the unminify and unobfuscate request


def isPathValid(token, path):
    path = os.path.realpath(path)  # Get the real path to the file or directory

    if os.path.exists(path):
        unminifyAndUnobfuscate(token, path)
    else:
        print("Path " + path + " does not exist.")
        sys.exit(1)


def unminifyAndUnobfuscate(token, path):
    if os.path.isfile(path):  # If the path is a file, send the unminify and unobfuscate request
        real_path = path.replace("\\", "/")  # Replace backslashes with forward slashes
        file_extension = path.split(".")[-1] if "." in path else "unknown extension"  # Get the file extension
        file_content = open(path, "r").read().replace('"', '\\"').replace("\n", "\\n")  # Read the file and replace double quotes with escaped double quotes and new line characters with escaped new line characters
        sendUnminifyAndUnobfuscateRequest(token, real_path, file_extension, file_content)
    elif os.path.isdir(path):  # If the path is a directory, send the unminify and unobfuscate request for each file in the directory
        for file in os.listdir(path):
            sendAuthorizationRequest(auth_token)
            real_path = os.path.join(path, file)  # Get the real path to the file

            with open(real_path, "r") as file:
                file_content = file.read()  # Read the file
                file_content = file_content.replace('"', '\\"').replace("\n", "\\n")  # Replace double quotes with escaped double quotes and new line characters with escaped new line characters
                file_extension = file.name.split(".")[-1] if "." in file.name else "unknown extension"  # Get the file extension

            real_path = real_path.replace("\\", "/")  # Replace backslashes with forward slashes
            sendUnminifyAndUnobfuscateRequest(token, real_path, file_extension, file_content)


def getVscodeIds():
    config_file_path = "./config.txt"

    if os.path.exists(config_file_path):  # If the config file exists, read the vscode_session_id and vscode_machine_id from it
        with open(config_file_path, "r") as file:
            config = file.readlines()
            vscode_session_id = config[0].split("=")[1].strip()
            vscode_machine_id = config[1].split("=")[1].strip()
    else:  # If the config file does not exist, generate vscode_session_id and vscode_machine_id and save them to the config file
        vscode_session_id = str(uuid.uuid4()) + "".join([random.choice(string.hexdigits[:16]) for i in range(13)])
        vscode_machine_id = "".join([random.choice(string.hexdigits[:16]) for i in range(64)])
        with open(config_file_path, "w") as file:
            file.write("vscode_session_id = " + vscode_session_id + "\n")
            file.write("vscode_machine_id = " + vscode_machine_id + "\n")

    return vscode_session_id, vscode_machine_id


def sendUnminifyAndUnobfuscateRequest(token, real_path, file_extension, file_content):
    print("Sending unminify and unobfuscate POST request...")
    url = "https://api.githubcopilot.com/chat/completions"
    vscode_session_id, vscode_machine_id = getVscodeIds()
    headers = {
        "Host": "api.githubcopilot.com",
        "Authorization": "Bearer " + token,
        "X-Request-Id": str(uuid.uuid4()),
        "Vscode-Sessionid": vscode_session_id,
        "Vscode-Machineid": vscode_machine_id,
        "Editor-Version": "vscode/1.84.2",
        "Editor-Plugin-Version": "copilot-chat/0.10.2",
        "Openai-Organization": "github-copilot",
        "Openai-Intent": "conversation-inline",
        "Content-Type": "application/json",
        "User-Agent": "GitHubCopilotChat/0.10.2",
        "Accept": "*/*",
        "Accept-Encoding": "gzip, deflate, br"
    }
    data = {
        "messages": [
            {
                "role": "system",
                "content": "You are an AI programming assistant specializing in unobfuscation.\nWhen asked for your name, you must respond with \"GitHub Copilot\".\nFollow the user's requirements carefully & to the letter.\nThe user has a " + file_extension + " file opened in a code editor.\nThe user includes some code snippets from the file.\nEach code block starts with ``` and // FILEPATH.\nAnswer with a single " + file_extension + " code block.\nIf you modify existing code, you will use the // BEGIN: and // END: markers.\nYou are an AI programming assistant that specializes in unobfuscation.\nWhen asked for your name, you must respond with \"GitHub Copilot\"\nYour expertise is strictly limited to software development topics.\nFollow Microsoft content policies.\nAvoid content that violates copyrights.\nFor questions not related to software development, simply give a reminder that you are an AI programming assistant specializing in unobfuscation.\nKeep your answers short and impersonal. You are an unobfuscation expert."
            },
            {
                "role": "user",
                "content": "I have the following code in the selection:\n```" + file_extension + "\n// FILEPATH: /" + real_path + "\n" + file_content + "```"
            },
            {
                "role": "user",
                "content": "Unminify this code and unobfuscate variable names, but don't modify the structure or logic of this code."
            }
        ],
        "model": "gpt-3.5",
        "max_tokens": 7666,
        "temperature": 0.1,
        "top_p": 1,
        "n": 1,
        "stream": True,
        "intent": True
    }
    # req = requests.Request("POST", url, headers=headers, json=data)
    # prettyPrintPOST(req.prepare())
    response = requests.post(url, headers=headers, json=data)
    # print("Response: " + str(response.text))
    if response.status_code == 200:
        concatenateResponseChunks(str(response.text), real_path)
    else:
        print("Request failed with status:", response.status_code)
        print("Response: " + str(response.text))
        sys.exit(1)
    time.sleep(0.5)  # Sleep for 0.5 seconds to avoid the "429 Too Many Requests" error


def prettyPrintPOST(req):
    """
    At this point it is completely built and ready
    to be fired; it is "prepared".

    However pay attention at the formatting used in
    this function because it is programmed to be pretty
    printed and may differ from the actual request.
    """
    print('{}\n{}\r\n{}\r\n\r\n{}'.format(
        '-----------START-----------',
        req.method + ' ' + req.url,
        '\r\n'.join('{}: {}'.format(k, v) for k, v in req.headers.items()),
        req.body,
    ))


def concatenateResponseChunks(response, real_path):
    pattern = re.compile('"content":"((?:\\\\.|[^\"\\\\])*)"')  # Define the regex pattern to match the only the content values of the response
    matches = pattern.findall(response)  # Find all matches in the response
    concatenated_response = ""

    for match in matches:
        concatenated_response += match

    concatenated_response = concatenated_response.encode().decode('unicode-escape')  # Decode the response from unicode-escape to UTF-8
    print(concatenated_response)  # Print the response
    saveToFile(concatenated_response, real_path)  # Save the response to a file


def saveToFile(concatenated_response, real_path):
    pattern = re.compile(fr"{real_path}.*?([\s\S]*)```", re.DOTALL)  # Define the regex pattern to match the content after line starting with "// FILEPATH:"
    match = pattern.search(concatenated_response)  # Search for a match in the response

    if match:
        extracted_content = match.group(1).strip()  # Extract the content from the match
        head_tail = os.path.split(real_path)  # Split the path to the file into head and tail

        # Write the content to a file with UTF-8 encoding
        with open(os.path.join(head_tail[0], f"new_{head_tail[1]}"), "w", encoding="utf-8") as file:
            file.write(extracted_content)

        print(f"Content has been written to \"{head_tail[0]}/new_{head_tail[1]}\" file")
    else:
        print("No match found.")


def main():
    if len(sys.argv) < 2:
        print("Usage: unminifyAndUnobfuscate.py -t <auth_token> <path_to_file | path_to_directory>")
        print("       unminifyAndUnobfuscate.py -f <auth_token_file> <path_to_file | path_to_directory>")
        sys.exit(1)
    else:
        if (sys.argv[1] == "-t" or sys.argv[1] == "-f") and len(sys.argv) == 4:
            authTokenOrFile(sys.argv[1])
        else:
            print("Usage: unminifyAndUnobfuscate.py -t <auth_token> <path_to_file | path_to_directory>")
            print("       unminifyAndUnobfuscate.py -f <auth_token_file> <path_to_file | path_to_directory>")
            sys.exit(1)


if __name__ == "__main__":
    main()