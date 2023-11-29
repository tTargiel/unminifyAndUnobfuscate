# unminifyAndUnobfuscate

This Python application leverages the power of generative AI language models to unminify and unobfuscate source code of any given application - in an automated fashion (you can provide either single file or whole directory of files to unminify and unobfuscate). 
By interfacing with the GitHub Copilot API, this tool allows developers to take minified or obfuscated code snippets and obtain human-readable, expanded versions.
To achieve the goal of automated unobfuscation of many files at once - this application sends initial authorization request, is spoofing itself as Visual Studio Code and generates valid session that is reauthorized every 1500 seconds.


Of course, you need correct authorization token from your GitHub Copilot license to use this program.

## Features

- **Unminify Code**: Convert minified code snippets into more readable and expanded versions.
- **Unobfuscate Code**: Transform obfuscated code snippets into clear and understandable code.


## Prerequisites

Before using this script, ensure that you have the following installed:

- Python 3.x
- Required Python packages (install using `pip install -r requirements.txt`)


## Usage

1. Clone this repository:

    ```bash
    git clone https://github.com/tTargiel/unminifyAndUnobfuscate.git
    cd unminifyAndUnobfuscate
    ```

2. Install dependencies:

    ```bash
    pip install -r requirements.txt
    ```

3. Run the script:

    ```bash
    python3 unminifyAndUnobfuscate.py -t <auth_token> <path_to_file | path_to_directory>
                                      -f <auth_token_file> <path_to_file | path_to_directory>
    ```

4. The unminified and unobfuscated code will be printed to the console and also saved to the original directory with `new_` prefix.


## Configuration

In the `auth_token.txt` file, you can write your authorization token to GitHub Copilot API (for ease of use).
In the `config.txt` file, you can specify `vscode_session_id = ` and `vscode_machine_id = `, but if you don't - those ids will be generated random at first run.

You may want to change `"model": "gpt-3.5",` to `"model": "gpt-4",` inside data json-dictionary in `sendUnminifyAndUnobfuscateRequest()` function (for better results), but that model is much slower than gpt-3.5 - keep that in mind.


## Disclaimer

This script is intended for educational and development purposes only. Use it responsibly and adhere to the terms and conditions of the GitHub Copilot API.

**Usage of this Python program is at your own risk. By using this software, you acknowledge and agree that:**

1. The developers are not liable for any damages or losses resulting from the use of the software.

2. The program is provided "as is," without any warranty or guarantee.

3. User actions with the software are solely the user's responsibility.

**Use this software responsibly and in compliance with laws.**

By using this program, you agree to these terms. If you disagree, do not use the software.