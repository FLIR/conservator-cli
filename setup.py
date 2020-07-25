import setuptools


try:
    from setuptools import find_namespace_packages
except ImportError:
    from setuptools import PEP420PackageFinder
    find_namespace_packages = PEP420PackageFinder.find

with open("README.md", "r") as fh:
        long_description = fh.read()

setuptools.setup(
    name="conservator-cli",
    version="0.0.3",
    author="FLIR",
    author_email="someone@somewhere",
    description="Command-line tools using the FLIR Conservator API",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/FLIR/conservator-cli",
    packages=find_namespace_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.5',
)
