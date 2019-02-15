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

setup(name='ifpd',
	version='2.0.2.post1',
	description='''An iFISH probe design pipeline, with web interface included.''',
	long_description=long_description,
	long_description_content_type='text/markdown',
	url='https://github.com/ggirelli/iFISH-Probe-Design',
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
	packages=["ifpd", "ifpd.sections", "ifpd.sections.probe_design"],
	install_requires=[
		"bottle>=0.12.13",
		'ggc>=0.0.3',
		'joblib>=0.11',
		"matplotlib>=3.0.0",
		"numpy>=1.14.2",
		"pandas>=0.22.0",
		"paste>=2.0.3",
		"scipy>=1.0.0"
	],
	scripts=[
		"bin/ifpd_mkdb",
		"bin/ifpd_dbchk",
		"bin/ifpd_query_probe",
		"bin/ifpd_query_set",
		"bin/ifpd_serve"
	],
	package_data={
		'ifpd': [
			'interface/css/bootstrap.css',
			'interface/css/*',
			'interface/fonts/*',
			'interface/images/*',
			'interface/js/*',
			'interface/views/*'
		],
		'ifpd.sections.probe_design': [
			'css/*', 'documents/*', 'views/*']
	},
	test_suite="nose.collector",
	tests_require=["nose"],
)