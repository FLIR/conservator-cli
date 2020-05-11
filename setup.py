import setuptools


with open("README.md", "r") as fh:
        long_description = fh.read()

setuptools.setup(
    name="conservator-cli",
    version="0.0.2",
    author="FLIR",
    author_email="someone@somewhere",
    description="Command-line tools using the FLIR Conservator API",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/FLIR/conservator-cli",
    packages=["FLIR.conservator_cli.lib", "FLIR.conservator_cli.app"],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.5',
)
