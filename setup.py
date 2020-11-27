# -*- coding: utf-8 -*-
from setuptools import setup, find_packages

with open('requirements.txt') as f:
	install_requires = f.read().strip().split('\n')

# get version from __version__ variable in bom_template/__init__.py
from bom_template import __version__ as version

setup(
	name='bom_template',
	version=version,
	description='App for managing processes, raw materials, service providers',
	author='Frappe',
	author_email='info@frappe.io',
	packages=find_packages(),
	zip_safe=False,
	include_package_data=True,
	install_requires=install_requires
)
