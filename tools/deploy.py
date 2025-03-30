#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Qt Installer Build Automation Script
-----------------------------------
This script automates the process of building and deploying a Qt application.
It copies files from build directory, runs windeployqt, and creates an installer.
Also supports generating update repositories.

Compatible with Python 3.7+
"""

import os
import sys
import shutil
import argparse
import subprocess
import logging
import time
import re
from pathlib import Path

# Constants
APP_SHORT_NAME = "POINAV"
APP_NAME = "POI Navigator.exe"  # Renamed executable
DEFAULT_VERSION = "1.0.0"  # Fallback version if can't be determined

# Default paths (can be overridden with command-line arguments)
SOURCE_DIR = r"C:\Users\Scipio\source\repos\QtMapUI_MVP"
BUILD_EXE_PATH = os.path.join(SOURCE_DIR, r"x64\Release\QtMapUI_MVP.exe")
RESOURCE_FOLDERS = ["img", "rsrc"]
INSTALLER_DATA_DIR = r"C:\Users\Scipio\source\repos\POINAV\installers\packages\com.limaltd.POINAV\data"
INSTALLER_CONFIG_DIR = r"C:\Users\Scipio\source\repos\POINAV\installers\config"
INSTALLER_ROOT_DIR = r"C:\Users\Scipio\source\repos\POINAV\installers"
BINARY_CREATOR = r"C:\Qt652\Tools\QtInstallerFramework\4.8\bin\binarycreator"
REPOGEN = r"C:\Qt652\Tools\QtInstallerFramework\4.8\bin\repogen"
WINDEPLOYQT = r"C:\Qt652\6.8.1\msvc2022_64\bin\windeployqt.exe"
REPOSITORY_DIR = os.path.join(INSTALLER_ROOT_DIR, "repository")
VERSION_HEADER = os.path.join(SOURCE_DIR, "version.h")

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('deploy_log.txt', mode='w')
    ]
)
logger = logging.getLogger("deploy")


def get_app_info():
    """Extract application information from version.h file"""
    app_info = {
        'version': DEFAULT_VERSION,
        'app_name': "POI Navigator",  # Default
        'company_name': "Lima Ltd",  # Default
        'release_date': time.strftime("%Y-%m-%d"),  # Current date
        'app_short_name': APP_SHORT_NAME  # Use the defined constant
    }

    try:
        if not os.path.exists(VERSION_HEADER):
            logger.warning(f"Version header file not found: {VERSION_HEADER}")
            return app_info

        with open(VERSION_HEADER, 'r') as f:
            content = f.read()

        # Look for version, app name, and organization
        version_match = re.search(r'#define\s+APP_VERSION\s+"([^"]+)"', content)
        name_match = re.search(r'#define\s+APP_NAME\s+"([^"]+)"', content)
        org_match = re.search(r'#define\s+APP_ORGANIZATION\s+"([^"]+)"', content)

        if version_match:
            app_info['version'] = version_match.group(1)
            logger.info(f"Found version: {app_info['version']}")
        else:
            logger.warning("APP_VERSION not found in version.h, using default")

        if name_match:
            app_info['app_name'] = name_match.group(1)
            logger.info(f"Found app name: {app_info['app_name']}")
        else:
            logger.warning("APP_NAME not found in version.h, using default")

        if org_match:
            app_info['company_name'] = org_match.group(1)
            logger.info(f"Found company name: {app_info['company_name']}")
        else:
            logger.warning("APP_ORGANIZATION not found in version.h, using default")

        return app_info
    except Exception as e:
        logger.error(f"Error reading version header: {e}")
        return app_info


def update_config_xml(config_file, app_info):
    """Update config.xml with application information"""
    logger.info(f"Updating config file: {config_file}")
    try:
        if not os.path.exists(config_file):
            logger.error(f"Config file not found: {config_file}")
            return False

        with open(config_file, 'r', encoding='utf-8') as f:
            content = f.read()

        # Update Name
        content = re.sub(r'<Name>.*?</Name>', f'<Name>{app_info["app_name"]}</Name>', content)

        # Update Version
        content = re.sub(r'<Version>.*?</Version>', f'<Version>{app_info["version"]}</Version>', content)

        # Update Title
        content = re.sub(r'<Title>.*? Installer</Title>', f'<Title>{app_info["app_name"]} Installer</Title>', content)

        # Update Publisher
        content = re.sub(r'<Publisher>.*?</Publisher>', f'<Publisher>{app_info["company_name"]}</Publisher>', content)

        # Update StartMenuDir
        content = re.sub(r'<StartMenuDir>.*?</StartMenuDir>', f'<StartMenuDir>{app_info["app_name"]}</StartMenuDir>',
                         content)

        with open(config_file, 'w', encoding='utf-8') as f:
            f.write(content)

        logger.info(f"Successfully updated config file")
        return True
    except Exception as e:
        logger.error(f"Error updating config file: {e}")
        return False


def update_package_xml(package_file, app_info):
    """Update package.xml with application information"""
    logger.info(f"Updating package file: {package_file}")
    try:
        if not os.path.exists(package_file):
            logger.error(f"Package file not found: {package_file}")
            return False

        with open(package_file, 'r', encoding='utf-8') as f:
            content = f.read()

        # Update DisplayName
        content = re.sub(r'<DisplayName>.*? Core</DisplayName>',
                         f'<DisplayName>{app_info["app_short_name"]} Core</DisplayName>', content)

        # Update Description
        content = re.sub(r'<Description>The core application files for .*?</Description>',
                         f'<Description>The core application files for {app_info["app_short_name"]}</Description>',
                         content)

        # Update Version
        content = re.sub(r'<Version>.*?</Version>', f'<Version>{app_info["version"]}</Version>', content)

        # Update ReleaseDate
        content = re.sub(r'<ReleaseDate>.*?</ReleaseDate>',
                         f'<ReleaseDate>{app_info["release_date"]}</ReleaseDate>', content)

        # Update Name (com.company.APP)
        company_part = app_info["company_name"].lower().replace(" ", "")
        content = re.sub(r'<Name>com\..*?\..*?</Name>',
                         f'<Name>com.{company_part}.{app_info["app_short_name"]}</Name>', content)

        with open(package_file, 'w', encoding='utf-8') as f:
            f.write(content)

        logger.info(f"Successfully updated package file")
        return True
    except Exception as e:
        logger.error(f"Error updating package file: {e}")
        return False


def update_js_file(js_file, app_info):
    """Update installscript.qs file with application information"""
    logger.info(f"Updating JavaScript file: {js_file}")
    try:
        if not os.path.exists(js_file):
            logger.error(f"JavaScript file not found: {js_file}")
            return False

        with open(js_file, 'r', encoding='utf-8') as f:
            content = f.read()

        # Look for variable definitions and update them
        # Common patterns in QS installer scripts

        # Replace app name
        content = re.sub(r'(var\s+appName\s*=\s*["\']).*?(["\'])',
                         r'\1' + app_info["app_name"] + r'\2', content)
        content = re.sub(r'(// Application Name:).*',
                         r'\1 ' + app_info["app_name"], content)

        # Replace version
        content = re.sub(r'(var\s+appVersion\s*=\s*["\']).*?(["\'])',
                         r'\1' + app_info["version"] + r'\2', content)
        content = re.sub(r'(// Version:).*',
                         r'\1 ' + app_info["version"], content)

        # Replace company name
        content = re.sub(r'(var\s+companyName\s*=\s*["\']).*?(["\'])',
                         r'\1' + app_info["company_name"] + r'\2', content)
        content = re.sub(r'(// Company:).*',
                         r'\1 ' + app_info["company_name"], content)

        # Replace app short name
        content = re.sub(r'(var\s+appShortName\s*=\s*["\']).*?(["\'])',
                         r'\1' + app_info["app_short_name"] + r'\2', content)

        with open(js_file, 'w', encoding='utf-8') as f:
            f.write(content)

        logger.info(f"Successfully updated JavaScript file")
        return True
    except Exception as e:
        logger.error(f"Error updating JavaScript file: {e}")
        return False

def clean_directory(directory):
    """Clean the target directory but keep it existing"""
    logger.info(f"Cleaning directory: {directory}")
    if os.path.exists(directory):
        for item in os.listdir(directory):
            item_path = os.path.join(directory, item)
            try:
                if os.path.isfile(item_path):
                    os.unlink(item_path)
                elif os.path.isdir(item_path):
                    shutil.rmtree(item_path)
            except Exception as e:
                logger.error(f"Error cleaning {item_path}: {e}")
    else:
        os.makedirs(directory, exist_ok=True)
        logger.info(f"Created directory: {directory}")


def copy_resources(source_dir, target_dir, resource_folders):
    """Copy resource folders from source to target"""
    logger.info(f"Copying resource folders: {resource_folders}")
    for folder in resource_folders:
        source_folder = os.path.join(source_dir, folder)
        target_folder = os.path.join(target_dir, folder)

        if os.path.exists(source_folder):
            logger.info(f"Copying {source_folder} to {target_folder}")
            try:
                if os.path.exists(target_folder):
                    shutil.rmtree(target_folder)
                shutil.copytree(source_folder, target_folder)
            except Exception as e:
                logger.error(f"Error copying folder {folder}: {e}")
        else:
            logger.warning(f"Source folder not found: {source_folder}")


def copy_executable(source_exe, target_dir, new_name):
    """Copy and rename the executable"""
    target_exe = os.path.join(target_dir, new_name)
    logger.info(f"Copying {source_exe} to {target_exe}")
    try:
        shutil.copy2(source_exe, target_exe)
        return target_exe
    except Exception as e:
        logger.error(f"Error copying executable: {e}")
        return None


def run_windeployqt(exe_path, qml_dir=None):
    """Run windeployqt to gather Qt dependencies"""
    logger.info("Running windeployqt...")
    cmd = [WINDEPLOYQT, "--release"]

    if qml_dir:
        cmd.extend(["--qmldir", qml_dir])

    cmd.append(exe_path)

    logger.info(f"Command: {' '.join(cmd)}")
    try:
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            universal_newlines=True
        )
        stdout, stderr = process.communicate()

        if process.returncode != 0:
            logger.error(f"windeployqt failed with code {process.returncode}")
            logger.error(f"stderr: {stderr}")
            return False

        logger.info("windeployqt completed successfully")
        return True
    except Exception as e:
        logger.error(f"Error running windeployqt: {e}")
        return False


def build_installer():
    """Build the installer using binarycreator"""
    logger.info("Building installer...")
    cmd = [
        BINARY_CREATOR,
        "--offline-only",
        "-c", os.path.join(INSTALLER_CONFIG_DIR, "config.xml"),
        "-p", os.path.join(INSTALLER_ROOT_DIR, "packages"),
        OUTPUT_INSTALLER
    ]

    logger.info(f"Command: {' '.join(cmd)}")
    try:
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            universal_newlines=True
        )
        stdout, stderr = process.communicate()

        if process.returncode != 0:
            logger.error(f"binarycreator failed with code {process.returncode}")
            logger.error(f"stderr: {stderr}")
            return False

        logger.info(f"Installer built successfully: {OUTPUT_INSTALLER}")
        return True
    except Exception as e:
        logger.error(f"Error building installer: {e}")
        return False


def generate_repository(update_components=False):
    """Generate an online repository using repogen"""
    logger.info("Generating online repository...")

    # Create repository directory if it doesn't exist
    os.makedirs(REPOSITORY_DIR, exist_ok=True)

    cmd = [REPOGEN]

    if update_components:
        logger.info("Using --update-new-components flag")
        cmd.append("--update-new-components")

    cmd.extend([
        "-p", os.path.join(INSTALLER_ROOT_DIR, "packages"),
        REPOSITORY_DIR
    ])

    logger.info(f"Command: {' '.join(cmd)}")
    try:
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            universal_newlines=True
        )
        stdout, stderr = process.communicate()

        if process.returncode != 0:
            logger.error(f"repogen failed with code {process.returncode}")
            logger.error(f"stderr: {stderr}")
            return False

        logger.info(f"Repository generated successfully: {REPOSITORY_DIR}")
        return True
    except Exception as e:
        logger.error(f"Error generating repository: {e}")
        return False


def parse_arguments():
    """Parse command-line arguments"""
    parser = argparse.ArgumentParser(description="Build and deploy Qt application")

    # Action flags
    parser.add_argument("--clean", action="store_true", help="Clean data directory before copying")
    parser.add_argument("--copy-exe", action="store_true", help="Copy executable")
    parser.add_argument("--copy-resources", action="store_true", help="Copy resource folders")
    parser.add_argument("--deployqt", action="store_true", help="Run windeployqt")
    parser.add_argument("--build-installer", action="store_true", help="Build installer")
    parser.add_argument("--generate-repo", action="store_true", help="Generate online repository")
    parser.add_argument("--update-repo", action="store_true", help="Update existing repository with new components")
    parser.add_argument("--update-configs", action="store_true",
                        help="Update configuration files with information from version.h")
    parser.add_argument("--all", action="store_true", help="Perform all actions (except update-repo)")

    # Path overrides
    parser.add_argument("--source-dir", help=f"Source directory (default: {SOURCE_DIR})")
    parser.add_argument("--build-exe", help=f"Build executable path (default: {BUILD_EXE_PATH})")
    parser.add_argument("--installer-data", help=f"Installer data directory (default: {INSTALLER_DATA_DIR})")
    parser.add_argument("--output", help=f"Output installer path (default based on version)")
    parser.add_argument("--repo-dir", help=f"Repository directory (default: {REPOSITORY_DIR})")

    # Additional options
    parser.add_argument("--qml-dir", help="QML directory for windeployqt")
    parser.add_argument("--version",
                        help=f"Version number for installer (default: from version.h or {DEFAULT_VERSION})")
    parser.add_argument("--version-header", help=f"Path to version header file (default: {VERSION_HEADER})")

    args = parser.parse_args()

    # If no actions specified, default to --all
    if not (args.clean or args.copy_exe or args.copy_resources or
            args.deployqt or args.build_installer or args.generate_repo or
            args.update_repo or args.update_configs or args.all):
        args.all = True
        logger.info("No actions specified, defaulting to --all")

    return args


def main():
    """Main function"""
    start_time = time.time()
    logger.info("Starting deployment process...")

    args = parse_arguments()

    # Extract all application info at once
    app_info = get_app_info()

    # Update paths if provided via command line
    global SOURCE_DIR, BUILD_EXE_PATH, INSTALLER_DATA_DIR, OUTPUT_INSTALLER, VERSION, VERSION_HEADER, REPOSITORY_DIR

    if args.source_dir:
        SOURCE_DIR = args.source_dir
    if args.build_exe:
        BUILD_EXE_PATH = args.build_exe
    if args.installer_data:
        INSTALLER_DATA_DIR = args.installer_data
    if args.repo_dir:
        REPOSITORY_DIR = args.repo_dir
    if args.version_header:
        VERSION_HEADER = args.version_header
        # Re-read app info from the specified header
        app_info = get_app_info()

    # Allow version override from command line
    if args.version:
        app_info['version'] = args.version

    # Set VERSION global from app_info
    VERSION = app_info['version']

    # Update output installer name based on version
    if not args.output:
        OUTPUT_INSTALLER = os.path.join(INSTALLER_ROOT_DIR,
                                        f"{app_info['app_name'].replace(' ', '')}-{VERSION}-setup.exe")
    else:
        OUTPUT_INSTALLER = args.output

    logger.info(f"Using application version: {VERSION}")

    # Create directories if they don't exist
    os.makedirs(INSTALLER_DATA_DIR, exist_ok=True)

    # Clean directory if requested
    if args.clean or args.all:
        clean_directory(INSTALLER_DATA_DIR)

    # Copy executable
    target_exe = None
    if args.copy_exe or args.all:
        target_exe = copy_executable(BUILD_EXE_PATH, INSTALLER_DATA_DIR, APP_NAME)
        if not target_exe:
            logger.error("Failed to copy executable, aborting process")
            return 1

    # Copy resources
    if args.copy_resources or args.all:
        copy_resources(SOURCE_DIR, INSTALLER_DATA_DIR, RESOURCE_FOLDERS)

    # Add config file update step
    if args.update_configs or args.all:
        # Update config.xml
        config_file = os.path.join(INSTALLER_CONFIG_DIR, "config.xml")
        if not update_config_xml(config_file, app_info):
            logger.warning("Failed to update config.xml")

        # Update package.xml
        package_file = os.path.join(INSTALLER_ROOT_DIR, "packages",
                                    f"com.{app_info['company_name'].lower().replace(' ', '')}.{app_info['app_short_name']}",
                                    "package.xml")
        if not os.path.exists(package_file):
            # Try with the default path
            package_file = os.path.join(INSTALLER_ROOT_DIR, "packages", "com.limaltd.POINAV", "meta", "package.xml")

        if not update_package_xml(package_file, app_info):
            logger.warning("Failed to update package.xml")

        # Look for installscript.qs
        js_file = os.path.join(os.path.dirname(package_file), "meta", "installscript.qs")
        if os.path.exists(js_file):
            if not update_js_file(js_file, app_info):
                logger.warning("Failed to update installscript.qs")
        else:
            logger.info("installscript.qs not found, skipping JavaScript update")

    # Run windeployqt
    if args.deployqt or args.all:
        if not target_exe and os.path.exists(os.path.join(INSTALLER_DATA_DIR, APP_NAME)):
            target_exe = os.path.join(INSTALLER_DATA_DIR, APP_NAME)

        if target_exe:
            qml_dir = args.qml_dir if args.qml_dir else SOURCE_DIR
            if not run_windeployqt(target_exe, qml_dir):
                logger.error("Failed to run windeployqt, continuing with process")
        else:
            logger.error("No executable found for windeployqt")

    # Build installer
    if args.build_installer or args.all:
        if not build_installer():
            logger.error("Failed to build installer")
            return 1

    # Generate or update repository
    if args.generate_repo or args.all:
        if not generate_repository():
            logger.error("Failed to generate repository")
            return 1

    if args.update_repo:
        if not generate_repository(update_components=True):
            logger.error("Failed to update repository")
            return 1

    elapsed_time = time.time() - start_time
    logger.info(f"Deployment process completed in {elapsed_time:.2f} seconds")
    return 0


if __name__ == "__main__":
    sys.exit(main())