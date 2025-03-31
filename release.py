# SPDX-License-Identifier: GPL-3.0-or-later
"""
Automates the release process for a Blender extension.

Provides functionalities to:

- Extract version information from `blender_manifest.toml`.
- Manage existing versions and create new releases.
- Create development copies of the extension.
- Build the extension into a zip file using Blender's command line interface.
- Optionally install the extension into Blender.

FIRST make sure to customize the following variables according to your setup:

- `PATH_TO_BLENDER`: Path to the Blender executable.
- `EXTENSION_FOLDER`: Name of the folder containing the extension files.

The script can be run from the command line with the following options:

- `--dev`, `-D`: Create a development build with '_dev' suffix.
- `--install`, `-I`: Installs the created extension into Blender.

"""

import argparse
import os
import glob
import re
import shutil
import subprocess
import tomllib
from colors import printcol


def get_base_path() -> str | os.PathLike:
    """Returns the base directory path of the release.py script."""
    return os.path.dirname(os.path.abspath(__file__))


def release_toml_parser():
    """
    Gets the path to the Blender executable path and name of extension folderf
    from `release.tom` file. Create with default values if doesn't exist.
    """

    if not os.path.exists("release.toml"):
        with open("release.toml", "w") as f:
            f.write(
                (
                    "# name of the folder containing your extension\n"
                    'extension = "my_extension"\n'
                    "# path to your blender executable\n"
                    'blender = "blender"\n'
                )
            )

    with open("release.toml", "rb") as f:
        cfg = tomllib.load(f)
        return cfg["extension"], cfg["blender"]


EXTENSION_FOLDER, PATH_TO_BLENDER = release_toml_parser()


def check_blender_and_extension_paths(base_path: str | os.PathLike) -> bool:
    """
    Checks existence of Blender executable and the extension directory.
    """

    result = True
    try:
        subprocess.run([PATH_TO_BLENDER, "-b"], check=True)
    except FileNotFoundError:
        printcol(
            "Red", (f"Error: Blender Executable not found in:\n{PATH_TO_BLENDER}`")
        )
        result = False

    if not os.path.isdir(os.path.join(base_path, EXTENSION_FOLDER)):
        printcol(
            "Red", (f"Error: Extension not found in:\n`{base_path}/{EXTENSION_FOLDER}`")
        )
        result = False

    return result


def devify_extension_name(dev_path: str | os.PathLike) -> None:
    """
    Set the addon name with '_dev' suffix in toml file
    """

    toml_path = os.path.join(dev_path, "blender_manifest.toml")
    with open(toml_path, "r", encoding="utf-8") as file:
        content = file.read()
    content = re.sub(
        r'^(name\s*=\s*)"([^"]+)"', r'\1"\2_dev"', content, flags=re.MULTILINE
    )
    content = re.sub(
        r'^(id\s*=\s*)"([^"]+)"', r'\1"\2_dev"', content, flags=re.MULTILINE
    )
    with open(toml_path, "w", encoding="utf-8") as file:
        file.write(content)


def dev_build_setup(base_path: str | os.PathLike) -> str | os.PathLike:
    """
    Delete any existing dev folder and zip to avoid possible outdated data.
    Creates a '*_dev' copy of the extension folder
    Modifies its internal files to rename the extension with '*_dev' suffix.
    """

    # Define paths
    dev_folder = os.path.join(base_path, EXTENSION_FOLDER + "_dev")
    releases_dir = os.path.join(base_path, "Releases")

    # Remove the dev folder if it exists
    if os.path.exists(dev_folder):
        printcol("Orange", f"Removing old dev folder: {dev_folder}")
        shutil.rmtree(dev_folder)

    # Creates _dev copy of extension folder
    shutil.copytree(os.path.join(base_path, EXTENSION_FOLDER), dev_folder)

    # Find and delete any existing _dev zip file
    dev_zip_files = glob.glob("*_dev.zip", root_dir=releases_dir) or []

    for file in dev_zip_files:
        file_path = os.path.join(releases_dir, file)
        printcol("Orange", f"Removing old dev zip: {file_path}")
        os.remove(file_path)

    devify_extension_name(dev_folder)

    return dev_folder


def read_version_toml(base_path: str | os.PathLike) -> tuple[int, int, int]:
    """Extracts version number from blender_manifest.toml into a tuple."""
    toml_path = os.path.join(base_path, EXTENSION_FOLDER, "blender_manifest.toml")
    if not os.path.exists(toml_path):
        raise FileNotFoundError(f"File not found: {toml_path}")

    with open(toml_path, "r", encoding="utf-8") as file:
        content = file.read()
    match = re.search(r'^version\s*=\s*"(\d+)\.(\d+)\.(\d+)"', content, re.MULTILINE)
    if match:
        return tuple(map(int, match.groups()))
    raise ValueError("Version not found in blender_manifest.toml")


def get_existing_versions(base_path: str | os.PathLike) -> list[tuple[int, int, int]]:
    """
    Returns a sorted tuples list of all extensions versions found in the
    Releases folder, omitting dev releases.
    """
    releases_dir = os.path.join(base_path, "Releases")
    if not os.path.exists(releases_dir):
        return []

    version_pattern = re.compile(
        rf"extension_{EXTENSION_FOLDER}_v(\d+)-(\d+)-(\d+)\.zip"
    )
    existing_versions = []

    for filename in os.listdir(releases_dir):
        match = version_pattern.match(filename)
        if match:
            version = tuple(map(int, match.groups()))
            existing_versions.append(version)

    return sorted(existing_versions)


def check_zip_exists(
    base_path: str | os.PathLike, version: tuple[int, int, int]
) -> bool:
    """
    Checks whether the zip file for the current version exists in the
    Releases folder.
    """
    releases_dir = os.path.join(base_path, "Releases")
    full_version = f"{version[0]}-{version[1]}-{version[2]}"
    zip_filename = f"extension_{EXTENSION_FOLDER}_v{full_version}.zip"
    return os.path.exists(os.path.join(releases_dir, zip_filename))


def update_version_in_toml(
    base_path: str | os.PathLike, version: tuple[int, int, int]
) -> None:
    """Updates the version in blender_manifest.toml"""

    version_str = f'version = "{version[0]}.{version[1]}.{version[2]}"'
    toml_path = os.path.join(base_path, EXTENSION_FOLDER, "blender_manifest.toml")
    with open(toml_path, "r", encoding="utf-8") as file:
        content = file.read()
    content = re.sub(
        r'^version\s*=\s*"\d+\.\d+\.\d+"', version_str, content, flags=re.MULTILINE
    )
    with open(toml_path, "w", encoding="utf-8") as file:
        file.write(content)


def build_extention_zip(
    base_path: str | os.PathLike, version: str, source_folder: str | os.PathLike
) -> bool:
    """
    Builds a Blender extension zip file using Blender's command line interface.

    Checks if the Releases directory exists, creating it if it does not.
    Assembles the zip filename using the extension folder name and version.
    Use Blender's CLI to build the extension into the Releases folder.
    """

    if not os.path.exists(f"{base_path}/Releases"):
        os.mkdir(f"{base_path}/Releases")

    file_name = f"extension_{EXTENSION_FOLDER}_{version}.zip"
    file_path = os.path.join(base_path, "Releases", file_name)
    command = (
        f"{PATH_TO_BLENDER} --factory-startup --command extension build "
        f"--source-dir {source_folder} "
        f"--output-filepath {file_path}"
    )
    printcol("Cyan", f"Building Extension: {file_name}")
    printcol("LightYellow", command)

    result = subprocess.run(
        command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, check=False
    )

    # Check if there's any output or error
    if result.stdout.strip():
        printcol("LightYellow", result.stdout.strip())
    if os.path.exists(file_path):
        printcol("Green", f"Successfully built: {file_name}")
        return True
    else:
        printcol("Red", f"Failed to build: {file_name}", alert=True)
        return False


def get_version(base_path: str | os.PathLike) -> str:
    """
    Returns an str version number for the extension to be built.
    If the version already have builds, ask the user whether to overwrite the
    existing build file, or type a new version, or cancel the build operation
    entirely.
    """

    # version_init = read_version_init(base_path)
    version_toml = read_version_toml(base_path)

    # Check if zip exists for the current version
    if check_zip_exists(base_path, version_toml):
        existing_versions = get_existing_versions(base_path)

        # Filter versions starting from the current version
        starting_index = existing_versions.index(version_toml)
        versions_from_current = existing_versions[starting_index:]

        # Display versions from the current one onward
        existing_versions_str = [
            f"{v[0]}.{v[1]}.{v[2]}" + f"{' (current)' if v == version_toml else ''}"
            for v in versions_from_current
        ]

        printcol(
            "Orange",
            (
                f"A release with version "
                f"{version_toml[0]}.{version_toml[1]}.{version_toml[2]} "
                "already exists."
            ),
        )
        printcol(
            "LightYellow",
            (f"Existing versions from current: {', '.join(existing_versions_str)}"),
        )

        while True:
            response = (
                input(
                    "Do you want to "
                    "(O)verwrite existing build, "
                    "(I)ncrement version, or "
                    "(C)ancel? (O/I/C): "
                )
                .strip()
                .lower()
            )

            if response == "c":  # Cancel building
                return "Cancel"
            if response == "o":  # Proceed with overwriting
                break
            if response == "i":
                new_version = input("Enter new version (X.Y.Z): ").strip()
                try:
                    version_tuple = tuple(map(int, new_version.split(".")))
                    if len(version_tuple) != 3:
                        raise ValueError
                    update_version_in_toml(base_path, version_tuple)
                    return f"v{version_tuple[0]}-{version_tuple[1]}-{version_tuple[2]}"
                except ValueError:
                    printcol("Orange", "Invalid version format. Try again.")
            else:
                printcol("Orange", "Invalid input. Please enter O, I, or C.")

    return f"v{version_toml[0]}-{version_toml[1]}-{version_toml[2]}"


def install_extension(base_path: str | os.PathLike, version: str) -> None:
    """
    Installs a Blender extension from the specified version zip file.

    Args:
        base_path (str): The base directory path of the Releases folder.
        version (str): version number or 'dev' variant

    1: tries to uninstall the extension using Blender's CLI.
    2: If the specified version's zip file exists in the Releases directory,
       it proceeds to install it as an extension using Blender's CLI.
    """

    releases_dir = os.path.join(base_path, "Releases")
    module = EXTENSION_FOLDER
    zip_filename = f"extension_{EXTENSION_FOLDER}_{version}.zip"

    if version == "dev":
        command = f"{PATH_TO_BLENDER} --command extension remove {module}_dev"
    else:
        command = f"{PATH_TO_BLENDER} --command extension remove {module}"

    printcol("Cyan", f"Removing old extension: {zip_filename}")

    # Run the command without raising an exception on non-zero exit status
    result = subprocess.run(
        command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, check=False
    )

    # Check if there's any output or error
    if result.stdout.strip():
        printcol("LightYellow", result.stdout.strip())

    # Check if stderr contains a message about the addon not being installed
    if result.stderr.strip():
        if "No module named" in result.stderr:
            printcol("Cyan", "Addon not installed, nothing to remove.")
        else:
            printcol("Orange", result.stderr.strip())
    else:
        printcol("Cyan", "Old extension successfully removed!")

    zip_path = os.path.join(releases_dir, zip_filename)
    if not os.path.exists(zip_path):
        printcol("Red", f"Error: Zip file not found: {zip_path}", alert=True)
        return
    command = (
        f"{PATH_TO_BLENDER} --command extension install-file "
        f"--repo user_default --enable {zip_path}"
    )
    printcol("Cyan", f"Installing extension: {zip_filename}")
    printcol("LightYellow", command)
    result = subprocess.run(
        command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, check=True
    )
    if result.stdout.strip():
        printcol("LightYellow", result.stdout.strip())
    if result.stderr.strip():
        printcol("Orange", result.stderr.strip())
    else:
        printcol("Green", "Installation completed.")


def main() -> None:
    """
    Main function containing the argument parser and logic.
    """
    parser = argparse.ArgumentParser(description="Blender Extension Release Script")
    parser.add_argument(
        "--dev",
        "-D",
        action="store_true",
        help="Create a development build with '_dev' suffix.",
    )
    parser.add_argument(
        "--install",
        "-I",
        action="store_true",
        help="Installs the created extension into Blender",
    )
    args = parser.parse_args()

    base_path = get_base_path()

    if check_blender_and_extension_paths(base_path):
        printcol("Cyan", "Found Blender Executable and Extension. Proceeding!")
    else:
        printcol(
            "Cyan",
            (
                "Please set your variables in the provided 'release.toml' ",
                "file to fix the issue.",
            ),
            alert=True,
        )
        return

    if args.dev:
        printcol("Cyan", "Running in development mode. Overwriting dev zip if exists.")

        source_folder = dev_build_setup(base_path)
        version = "dev"
    else:
        version = get_version(base_path)
        if version == "Cancel":
            printcol("LightYellow", "Operation canceled.")
            return
        source_folder = EXTENSION_FOLDER

    if build_extention_zip(base_path, version, source_folder):
        if args.install:
            install_extension(base_path, version)


if __name__ == "__main__":
    # EXTENSION_FOLDER, PATH_TO_BLENDER = release_toml_parser()
    main()
