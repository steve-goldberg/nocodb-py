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
           # CLI is now auto-generated from MCP server
           # Uses cyclopts (via fastmcp) instead of typer
           "fastmcp>=3.0.0rc1",
           "tomli>=2.0.0;python_version<'3.11'",
       ],
       "mcp": [
           "fastmcp>=3.0.0rc1",
       ],
       "all": [
           "fastmcp>=3.0.0rc1",
           "tomli>=2.0.0;python_version<'3.11'",
       ],
   },
   entry_points={
       "console_scripts": [
           "nocodb=nocodb.cli.main:main",
       ],
   },
   python_requires=">=3.9",
)
