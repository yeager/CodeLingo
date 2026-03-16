"""Setup script for CodeLingo."""

from setuptools import find_packages, setup

setup(
    name="codelingo",
    version="0.1.0",
    description="Lär barn programmera på svenska - Learn programming in Swedish",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    author="CodeLingo",
    author_email="info@codelingo.se",
    url="https://github.com/codelingo/codelingo",
    license="MIT",
    packages=find_packages(),
    python_requires=">=3.10",
    install_requires=[
        "PyGObject>=3.42",
        "RestrictedPython>=7.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0",
            "pytest-cov",
        ],
    },
    entry_points={
        "console_scripts": [
            "codelingo=codelingo.app:main",
        ],
    },
    package_data={
        "codelingo": [],
    },
    data_files=[
        ("share/applications", ["data/codelingo.desktop"]),
        (
            "share/icons/hicolor/scalable/apps",
            ["data/icons/hicolor/scalable/apps/se.codelingo.CodeLingo.svg"],
        ),
    ],
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Environment :: X11 Applications :: GTK",
        "Intended Audience :: Education",
        "License :: OSI Approved :: MIT License",
        "Natural Language :: Swedish",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Education",
    ],
)
