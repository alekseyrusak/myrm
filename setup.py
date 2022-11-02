import io

from setuptools import find_packages, setup

from myrm import __version__

with io.open("README.md", mode="rt", encoding="utf-8") as stream_in:
    # Load the readme file and use it as the long description for this python package.
    long_description = stream_in.read()

setup(
    name="myrm",
    version=__version__,
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
    install_requires=["prettytable>=2.5.0,<3.5.0"],
    extras_require={
        "dev": [
            "black>=22.8.0,<23.0.0",
            "flake8>=5.0.0,<6.0.0",
            "isort>=5.10.0,<5.11.0",
            "mypy==0.971",
            "pre-commit>=2.20.0,<2.21.0",
            "pylint>=2.15.0,<2.16.0",
        ],
        "tests": [
            "pyfakefs>=4.6.0,<4.7.0",
            "pytest-cov>=3.0.0,<3.1.0",
            "pytest-mock>=3.6.0,<4.0.0",
            "pytest>=7.0.0,<8.0.0",
            "tox>=3.26.0,<3.27.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "myrm = myrm.__main__:main",
        ],
    },
)
