# Project Name

Club Management System

## Table of Contents

- [Requirements](#requirements)
- [Installation](#installation)
- [Usage](#usage)
- [API Endpoints](#api-endpoints)
- [Local Setup](#local-setup)
- [Contributing](#contributing)

## Requirements

- Python version >= 3.7
- MySQL shell on Windows. Please update the file path in the `deploy_file.ps1` script located in the Initialization folder. Replace the value of `$mysql_loc` with the file path of your MySQL shell. For example: 
  `$mysql_loc = "C:\Program Files\MySQL\MySQL Shell 8.0\bin\mysqlsh.exe"`
- Open a command shell and run the following command inside a virtual environment to install the required dependencies:

```bash
pip install -r requirements.txt
```
-    Add the serverName parameter in the root directory of the project. Also, add your metadata.json file to the root directory. The metadata.json file should contain the following key components:
        projectName: "club"
        indicator: "dw"
        schemaName: "amritsar_dw"

## Installation

- Clone the repository:

bash

git clone https://github.com/username/project.git

- Change into the project directory:

bash

cd project

- Install the required dependencies using the following command:

bash

pip install -r requirements.txt

- Continue with the installation:

bash

pip install -r requirements.txt


## Usage

To start the operation, run the following command:

```bash
python main.py
```
After starting the server, you can send POST and GET requests to the following address: http://127.0.0.1:5000

Visit http://127.0.0.1:5000 in your web browser to access the application and provide the required information.

## API Endpoints

The following API endpoints are available:

    GET /api/resource: Retrieves a resource.
    POST /api/resource: Creates a new resource.
    PUT /api/resource/{id}: Updates an existing resource.
    DELETE /api/resource/{id}: Deletes a resource.

## Local Setup

To set up a local development environment, follow these steps:

    Clone the repository:

bash

git clone https://github.com/username/project.git

    Change into the project directory:

bash

cd project

    Install the required dependencies using the following command:

bash

pip install -r requirements.txt

    Refer to the localhost folder for the necessary files to create a replica of the required information.

    The files will be added to the MySQL_DBSetup directory under the server folder created in step 4.

## Contributing

Contributions are welcome! If you would like to contribute to this project, please follow these steps:

    Fork the repository.
    Create a new branch for your feature or bug fix.
    Make the necessary changes and commit your code.
    Push your changes to your forked repository.
    Submit a pull request to the main repository.