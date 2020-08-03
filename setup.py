import setuptools
import re
import glob
import version


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

def find_scripts():
    return list(glob.iglob("**/app/**/*.py", recursive=True))

git_version=version.get_git_version()
print("VERSION: ", git_version)

with open("README.md", "r") as fh:
        long_description = fh.read()

setuptools.setup(
    name="conservator-cli",
    version=git_version,
    author="FLIR",
    author_email="someone@somewhere",
    description="Command-line tools using the FLIR Conservator API",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/FLIR/conservator-cli",
    packages=find_namespace_packages(include=["FLIR.*"], exclude=["*.test.*"]),
    scripts=find_scripts(),
    zip_safe=False,
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.5',
    # NOTE: add new requirements to requirements.txt as well
    install_requires=[
        "requests",
        "eventlet"
    ],
)
