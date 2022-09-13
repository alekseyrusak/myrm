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
    setup_requires=["setuptools", "wheel"],
    extras_require={
        "dev": [
            "black==22.8.0",
            "flake8==5.0.4",
            "isort==5.10.1",
            "mypy==0.971",
            "pre-commit==2.20.0",
            "pylint==2.15.0",
        ],
        "tests": [
            "pyfakefs==4.6.3",
            "pytest-cov==3.0.0",
            "pytest-mock==3.8.2",
            "pytest==7.1.2",
            "tox==3.26.0",
        ],
    },
)
