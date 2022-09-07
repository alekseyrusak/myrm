import io

from setuptools import find_packages, setup

with io.open("README.md", mode="rt", encoding="utf-8") as stream_in:
    # Load the readme file and use it as the long description for this python package.
    long_description = stream_in.read()


setup(
    name="myrm",
    version="0.0.0",
    description="Simple remove utility",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Aliaksei Rusak",
    author_email="alex_rsk@tut.by",
    license="MIT",
    url="https://github.com/masteroftheworld/rmlib",
    project_urls={
        "Issue tracker": "https://github.com/masteroftheworld/rmlib/issues",
        "Source code": "https://github.com/masteroftheworld/rmlib",
    },
    python_requires=">=3.6",
    packages=find_packages(exclude=["tests"]),
    classifiers=[
        "Intended Audience :: Developers",
        "Intended Audience :: System Administrators",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Utilities",
    ],
)
