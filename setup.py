import setuptools

import version


git_version = version.get_git_version()
print("VERSION: ", git_version)

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="conservator-cli",
    version=git_version,
    author="FLIR",
    author_email="someone@somewhere",
    description="A library for using the FLIR Conservator API, with a nice command line interface.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/FLIR/conservator-cli",
    packages=setuptools.find_namespace_packages(),
    entry_points='''
        [console_scripts]
        conservator=conservator.cli:main
    ''',
    zip_safe=False,
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.5',
    # NOTE: add new requirements to requirements.txt as well
    install_requires=[
        "sphinx",
        "sgqlc",
        "click",
        "tqdm",
        "pytest",
    ],
)
