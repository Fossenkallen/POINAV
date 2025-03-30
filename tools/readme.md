# Qt Application Deployment Script

## Overview

This Python script automates the deployment process for Qt applications, simplifying the workflow from build to installer creation. It handles copying application files, deploying Qt dependencies, building an installer using the Qt Installer Framework, and generating online update repositories. The script automatically detects application version from source code.

## Requirements

- Python 3.7 or higher
- Qt 6.x with Qt Installer Framework installed
- Windows operating system

## Installation

1. Save the script as `deploy.py` in a location of your choice
2. Ensure you have proper permissions to access the build and installer directories

## Basic Usage

Run all deployment steps with default settings:

```bash
python deploy.py
```

This will:
1. Clean the installer data directory
2. Copy and rename the executable
3. Copy resource folders
4. Run windeployqt to gather Qt dependencies
5. Build the installer
6. Generate an online repository for updates

The script automatically reads the application version from version.h (#define APP_VERSION "x.y.z").
6. Generate an online repository for updates

The script automatically reads the application version from version.h (#define APP_VERSION "x.y.z").

## Command-Line Options

### Action Flags

| Flag | Description |
|------|-------------|
| `--clean` | Clean data directory before copying |
| `--copy-exe` | Copy and rename executable |
| `--copy-resources` | Copy resource folders |
| `--deployqt` | Run windeployqt to gather Qt dependencies |
| `--build-installer` | Build installer using Qt Installer Framework |
| `--generate-repo` | Generate a fresh online repository for updates |
| `--update-repo` | Update existing repository with new components |
| `--all` | Perform all actions except updating repository (default if no actions specified) |

### Path Overrides

| Option | Description |
|--------|-------------|
| `--source-dir PATH` | Source directory containing the project |
| `--build-exe PATH` | Path to the built executable |
| `--installer-data PATH` | Installer data directory path |
| `--output PATH` | Output installer path |
| `--repo-dir PATH` | Repository directory for online updates |
| `--version-header PATH` | Path to header file containing version definition |
| `--repo-dir PATH` | Repository directory for online updates |
| `--version-header PATH` | Path to header file containing version definition |

### Additional Options

| Option | Description |
|--------|-------------|
| `--qml-dir PATH` | QML directory for windeployqt (defaults to source directory) |
| `--version VERSION` | Version number for installer (overrides version from header file) |

## Examples

### Run Specific Steps

Only copy resources and run windeployqt:

```bash
python deploy.py --copy-resources --deployqt
```

### Override Paths

Use custom paths for source and output:

```bash
python deploy.py --source-dir "D:\Projects\MyApp" --output "D:\Releases\MyApp-1.1.0.exe"
```

### Set Version Manually

Override version from version.h:

```bash
python deploy.py --version 1.2.3
```

### Generate Update Repository

Create/update the repository for online updates:

```bash
python deploy.py --generate-repo
```

### Update Existing Repository

Add new components to an existing repository:

```bash
python deploy.py --update-repo
```

### Custom Version Header

Specify a different location for version.h:

```bash
python deploy.py --version-header "C:\Projects\Common\version.h"
```

## Common Workflows

### Full Release Build

```bash
python deploy.py --clean
```

### Update Existing Deployment

```bash
python deploy.py --copy-exe --deployqt --build-installer
```

### Quick Test Build

```bash
python deploy.py --copy-exe --copy-resources --deployqt
```

### Create Initial Release with Repository

```bash
python deploy.py --clean --build-installer --generate-repo
```

### Release Update to Existing Users

```bash
python deploy.py --clean --build-installer --update-repo
```

## Troubleshooting

### Script fails with permission errors
- Ensure you have write access to all relevant directories
- Try running the script as administrator

### windeployqt doesn't find all dependencies
- Use the `--qml-dir` option to specify where your QML files are located
- Manually check for missing dependencies in the INSTALLER_DATA_DIR

### Installer fails to build
- Check the deploy_log.txt file for specific errors
- Verify that your config.xml and package.xml files are correctly formatted

### Version not detected correctly
- Verify your version.h file contains the correct format: `#define APP_VERSION "x.y.z"`
- Use the `--version-header` option to point to the correct file
- Override with `--version` if needed

### Repository generation fails
- Ensure your package.xml files include proper version information
- Check that the repository directory is writable
- For online repositories, verify the URL in config.xml is correct

### Version not detected correctly
- Verify your version.h file contains the correct format: `#define APP_VERSION "x.y.z"`
- Use the `--version-header` option to point to the correct file
- Override with `--version` if needed

### Repository generation fails
- Ensure your package.xml files include proper version information
- Check that the repository directory is writable
- For online repositories, verify the URL in config.xml is correct

## Configuration

The script uses default paths for a standard project setup. You can customize these paths either by:

1. Editing the constants at the top of the script:
   ```python
   SOURCE_DIR = r"C:\path\to\your\project"
   BUILD_EXE_PATH = r"C:\path\to\your\build\exe"
   VERSION_HEADER = r"C:\path\to\your\project\version.h"
   REPOSITORY_DIR = r"C:\path\to\repository"
   # etc.
   ```

2. Using the command-line overrides mentioned above

### Version Header File Format

The script expects to find version information in a C/C++ header file (version.h) with the following format:

```cpp
#define APP_VERSION "1.2.3"  // Version string in semver format
```

If the version.h file doesn't exist or doesn't contain the APP_VERSION define, the script will use a default version.

## Logging

The script logs all actions to both the console and a file named `deploy_log.txt` in the current directory. Check this file for detailed information about the deployment process and any errors encountered.

## Online Repository for Updates

The script can generate a repository structure that enables your application to receive automatic updates. To use this feature:

1. Make sure your config.xml includes a proper RemoteRepositories section:
   ```xml
   <RemoteRepositories>
       <Repository>
           <Url>https://your-server.com/repository</Url>
           <DisplayName>Your App Repository</DisplayName>
           <Enabled>1</Enabled>
       </Repository>
   </RemoteRepositories>
   ```

2. Host the generated repository directory on a web server
3. When releasing updates:
   - Update version in version.h
   - Run `python deploy.py --update-repo` to update the repository
   - Upload the updated repository to your server

Your application will then be able to check for and download updates automatically.

## Online Repository for Updates

The script can generate a repository structure that enables your application to receive automatic updates. To use this feature:

1. Make sure your config.xml includes a proper RemoteRepositories section:
   ```xml
   <RemoteRepositories>
       <Repository>
           <Url>https://your-server.com/repository</Url>
           <DisplayName>Your App Repository</DisplayName>
           <Enabled>1</Enabled>
       </Repository>
   </RemoteRepositories>
   ```

2. Host the generated repository directory on a web server
3. When releasing updates:
   - Update version in version.h
   - Run `python deploy.py --update-repo` to update the repository
   - Upload the updated repository to your server

Your application will then be able to check for and download updates automatically.