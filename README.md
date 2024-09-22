# Project Setup Tool

## Overview

The **Project Setup Tool** is a Python-based application designed to streamline the process of initializing new projects. It automates the creation of project directories, virtual environments, Git repositories, and essential configuration files. The tool supports different types of projects, including basic Python projects, data analytics projects and FastAPI projects.

## Features

- **Project Directory Creation**: Automatically creates a project directory with the specified name.
- **Virtual Environment**: Sets up a Python virtual environment with `pip` installed.
- **Git Initialization**: Initializes a Git repository and downloads a `.gitignore` file.
- **Configuration Files**: Generates configuration files such as `ruff.toml`, `requirements.txt`, and VS Code settings.
- **Project Templates**: Provides templates for different project types, including basic Python, data analytics, and FastAPI projects.
- **Docker Support**: Creates Dockerfile and docker-compose.yml files for containerization.
- **VS Code Integration**: Configures VS Code settings and opens the project in VS Code.

## Dependencies

The Project Setup Tool relies on the following Python packages:

- **PyQt5**: For the graphical user interface. The tool uses PyQt5 to create a modern, user-friendly interface with a dark theme inspired by Material Design.
- **venv**: For creating virtual environments.
- **requests**: For downloading the `.gitignore` file.

## How It Works

1. **User Interface**: The tool provides a simple GUI where users can input the project name and select the project type.
2. **Project Creation**: Upon clicking the "Create Project" button, the tool performs the following steps:
   - Creates the project directory.
   - Sets up a virtual environment.
   - Downloads a `.gitignore` file.
   - Initializes a Git repository.
   - Generates configuration files (`ruff.toml`, `requirements.txt`, etc.).
   - Creates project-specific files and directories based on the selected type.
   - Configures VS Code settings.
   - Installs dependencies.
   - Opens the project in VS Code.
3. **Progress Tracking**: The tool provides real-time feedback through a progress bar and an output console that highlights different log levels (INFO, SUCCESS, ERROR).

## Getting Started

### Prerequisites

- Python 3.12 or higher
- Git installed on your system
- VS Code installed on your system

### Installation

1. Clone the repository:

   ```sh
   git clone https://github.com/yourusername/project-setup-tool.git
   cd project-setup-tool
   ```
2. Install the required dependencies:

   ```sh
   pip install -r requirements.txt
   ```

### Running the Project

To run the Project Setup Tool, you can use the provided `.bat` file for Windows.

#### Windows

1. **Create a `.bat` file**:
   Create a file named `run.bat` with the following content:

   ```bat
   @echo off
   start "" "C:\path\to\your\python.exe" "C:\path\to\your\project\main.py"
   ```

   Replace `"C:\path\to\your\python.exe"` with the path to your Python interpreter and `"C:\path\to\your\project\main.py"` with the path to your main Python script.
2. **Create a Desktop Shortcut**:

   - Right-click on the desktop and select "New" -> "Shortcut".
   - In the "Location of item" field, enter the full path to the `.bat` file, e.g., `C:\path\to\your\run_project.bat`.
   - Click "Next", enter a name for the shortcut, and click "Finish".

### Usage

1. **Launch the Tool**: Double-click the desktop shortcut to launch the Project Setup Tool.
2. **Input Project Details**: Enter the project name and select the project type from the dropdown menu.
3. **Create Project**: Click the "Create Project" button to start the project setup process.
4. **Monitor Progress**: The progress bar and output console will provide real-time feedback on the setup process.

### User Interface (UI)

The Project Setup Tool features a modern, user-friendly interface built with PyQt5. The UI includes the following elements:

- **Project Name Input**: A text field where users can enter the name of the project.
- **Project Type Selection**: A dropdown menu that allows users to select the type of project (Basic Python, Data Analytics, FastAPI).
- **Create and Cancel Buttons**: Buttons to start the project creation process or cancel the operation.
- **Output Console**: A text area that displays real-time logs and feedback, with syntax highlighting for different log levels (INFO, SUCCESS, ERROR).
- **Progress Bar**: A visual indicator that shows the progress of the project setup process.

## Contributing

Contributions are welcome! Please feel free to submit a pull request or open an issue if you find any bugs or have suggestions for improvements.

## License

This project is licensed under the MIT License. See the [LICENSE](https://opensource.org/license/mit) file for details.
