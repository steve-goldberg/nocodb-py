from setuptools import setup, find_packages


setup(
   name='nocodb',
   version='3.0.0',
   author='Samuel López Saura',
   author_email='samuellopezsaura@gmail.com',
   packages=find_packages(),
   license='AGPL-3.0',
   url='https://github.com/ElChicoDePython/python-nocodb',
   classifiers=[
       "Programming Language :: Python :: 3",
       "License :: OSI Approved :: GNU Affero General Public License v3",
       "Operating System :: OS Independent",
   ],
   description='A Python client for NocoDB v3 API',
   long_description=open('README.md').read(),
   long_description_content_type="text/markdown",
   install_requires=[
       "requests>=2.0",
   ],
   extras_require={
       "cli": [
           "typer[all]>=0.12.0",
           "rich>=13.0.0",
           "tomli>=2.0.0;python_version<'3.11'",
       ],
       "mcp": [
           "fastmcp>=2.14.0",
       ],
       "all": [
           "typer[all]>=0.12.0",
           "rich>=13.0.0",
           "tomli>=2.0.0;python_version<'3.11'",
           "fastmcp>=2.14.0",
       ],
   },
   entry_points={
       "console_scripts": [
           "nocodb=nocodb.cli.main:app",
       ],
   },
   python_requires=">=3.9",
)
