"""A setuptools based setup module.

See:
https://packaging.python.org/en/latest/distributing.html
https://github.com/pypa/sampleproject
"""

# Always prefer setuptools over distutils
from setuptools import setup, find_packages

# To use a consistent encoding
from codecs import open
import os

here = os.path.abspath(os.path.dirname(__file__))
bindir = os.path.join(here, "bin/")

# Get the long description from the README file
with open(os.path.join(here, 'README.md'), encoding='utf-8') as f:
	long_description = f.read()

setup(name='fish_prode',
	version='0.0.1',
	description='A FISH probe design web interface',
	long_description=long_description,
	long_description_content_type='text/markdown',
	url='https://github.com/ggirelli/fish-prode',
	author='Gabriele Girelli',
	author_email='gabriele.girelli@scilifelab.se',
	license='MIT',
	classifiers=[
		'Development Status :: 3 - Alpha',
		'Intended Audience :: Science/Research',
		'Topic :: Scientific/Engineering :: Bio-Informatics',
		'License :: OSI Approved :: MIT License',
		'Programming Language :: Python :: 3 :: Only',
	],
	keywords='biology cell DNA RNA FISH fluorescence hybridization bioimaging genome',
	packages=find_packages(),
	install_requires=[
		"bottle>=0.12.13",
		"numpy>=1.14.2",
		"pandas>=0.22.0"
	],
	scripts=[os.path.join(bindir, fp) for fp in os.listdir(bindir)],
	test_suite="nose.collector",
	tests_require=["nose"],
)
