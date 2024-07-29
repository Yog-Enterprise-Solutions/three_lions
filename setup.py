from setuptools import setup, find_packages

with open("requirements.txt") as f:
	install_requires = f.read().strip().split("\n")

# get version from __version__ variable in three_lions/__init__.py
from three_lions import __version__ as version

setup(
	name="three_lions",
	version=version,
	description="for trading ",
	author="yog",
	author_email="yogenterprisesolutions@gmail.com",
	packages=find_packages(),
	zip_safe=False,
	include_package_data=True,
	install_requires=install_requires
)
