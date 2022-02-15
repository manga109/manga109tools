from setuptools import setup, find_packages
from pathlib import Path
import shutil
import re


with open("README.md") as f:
    readme = f.read()

with open("requirements.txt") as f:
    requirements = []
    for line in f:
        requirements.append(line.rstrip())

with open("manga109tools/__init__.py") as f:
    # Version is written in manga109tools/__init__.py
    version = re.search(r"__version__ = \"(.*?)\"", f.read()).group(1)

manga109_home: Path = Path.home() / ".manga109tools"
manga109_home.mkdir(parents=True, exist_ok=True)
shutil.copyfile("exceptions.yaml", manga109_home / "exceptions.yaml")

setup(
    name="manga109tools",
    version=version,
    description="Tools for Manga109",
    long_description=readme,
    long_description_content_type="text/markdown",
    author="Manga109 Maintainers",
    author_email="matsui528@gmail.com",
    url="https://github.com/manga109tools-dev/manga109tools",
    license="MIT",
    packages=find_packages(),
    include_package_data=True,
    install_requires=requirements,
    entry_points={
        "console_scripts": [
            "manga109tools = manga109tools.main:main",
        ]
    },
)
