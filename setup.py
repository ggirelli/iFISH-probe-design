"""A setuptools based setup module.

See:
https://packaging.python.org/en/latest/distributing.html
https://github.com/pypa/sampleproject
"""

# Always prefer setuptools over distutils
from setuptools import setup, find_packages

# Get the long description from the README file
with open('README.md', "r") as f:
	long_description = f.read()

setup(name='fish_prode',
	version='1.1.0.post1',
	description='''A FISH probe design web interface.''',
	long_description=long_description,
	long_description_content_type='text/markdown',
	url='https://github.com/ggirelli/fish-prode',
	author='Gabriele Girelli',
	author_email='gabriele.girelli@scilifelab.se',
	license='MIT',
	classifiers=[
		'Development Status :: 4 - Beta',
		'Intended Audience :: Science/Research',
		'Topic :: Scientific/Engineering :: Bio-Informatics',
		'License :: OSI Approved :: MIT License',
		'Programming Language :: Python :: 3 :: Only',
	],
	keywords='biology cell DNA RNA FISH fluorescence hybridization bioimaging genome',
	packages=["fish_prode", "fish_prode.sections", "fish_prode.sections.probe_design"],
	install_requires=[
		"bottle>=0.12.13",
		"matplotlib>=2.2.2",
		"numpy>=1.14.2",
		"pandas>=0.22.0",
		"paste>=2.0.3",
		"scipy>=1.0.0"
	],
	scripts=["bin/fprode_dbextract", "bin/fprode_dbquery", "bin/fprode_serve"],
	package_data={
		'fish_prode': ['css/bootstrap.css', 'css/*', 'fonts/*', 'js/*', 'views/*'],
		'fish_prode.sections.probe_design': ['css/*', 'documents/*', 'views/*']
	},
	test_suite="nose.collector",
	tests_require=["nose"],
)