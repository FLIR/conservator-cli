import sys
import platform
import re
import setuptools

current_platform = platform.system()

if current_platform.lower() == "windows":
    print("Conservator-CLI is currently only supported on Windows through WSL.")
    print(
        "Please see https://flir.github.io/conservator-cli/usage/installation.html#installation-on-windows for details"
    )
    sys.exit(1)


try:
    from setuptools import find_namespace_packages
except ImportError:
    from setuptools import PEP420PackageFinder

    # don't mistake 'build' area for a place to find packages
    def fix_PEP420PackageFinder_find(**args):
        pkgs = PEP420PackageFinder.find(**args)
        regex = re.compile("build")
        selected_pkgs = list(filter(lambda p: not regex.match(p), pkgs))
        return selected_pkgs

    find_namespace_packages = fix_PEP420PackageFinder_find

# if this is run from git repo, create updated version file,
# otherwise there should be a previously created version file
try:
    import version

    version = version.get_git_version()
    print("GIT VERSION: ", version)
    with open("FLIR/conservator/version.py", "w", encoding="utf-8") as fp:
        fp.write(f'version = "{version}"\n')
except:
    from FLIR.conservator.version import version

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()


# NOTE: These dependencies are necessary for CLI to function, and will be
# installed when a user runs pip install.
# Packages only used for developing (pytest, black, etc.) should be placed
# in requirements.txt instead.
INSTALL_REQUIRES = [
    "graphql-core == 3.2.1; python_version<'3.7'",
    "sgqlc >= 13; python_version>='3.7'",
    "sgqlc == 16.0; python_version<'3.7'",
    "click >= 8",
    "tqdm",
    "requests",
    "Pillow",
    "jsonschema",
    "dataclasses; python_version<'3.7'",
    "pyreadline; platform_system=='Windows'",
    "semver == 2.13.0",
]

setuptools.setup(
    name="conservator-cli",
    version=version,
    author="Teledyne FLIR LLC",
    description="A library for using the FLIR Conservator API, with a nice command line interface.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/FLIR/conservator-cli",
    packages=find_namespace_packages(include=["FLIR.*"], exclude=["*.test.*"]),
    package_data={
        "FLIR.conservator": ["configs/*.json"],
    },
    entry_points="""
        [console_scripts]
        conservator=FLIR.conservator.cli:main
        cvc=FLIR.conservator.cli.cvc:main
    """,
    zip_safe=False,
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
    install_requires=INSTALL_REQUIRES,
    setup_requires=["wheel"],
)
