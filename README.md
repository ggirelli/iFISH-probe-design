# iFISH-Probe-Design

[![DOI](https://zenodo.org/badge/143724120.svg)](https://zenodo.org/badge/latestdoi/143724120) ![](https://img.shields.io/librariesio/github/ggirelli/ifish-probe-design.svg?style=flat) ![](https://img.shields.io/github/license/ggirelli/ifish-probe-design.svg?style=flat)  
![](https://github.com/ggirelli/ifish-probe-design/workflows/Python%20package/badge.svg?branch=main&event=push) ![PyPI - Python Version](https://img.shields.io/pypi/pyversions/ifpd) ![PyPI - Format](https://img.shields.io/pypi/format/ifpd) ![PyPI - Status](https://img.shields.io/pypi/status/ifpd)  
![](https://img.shields.io/github/release/ggirelli/ifish-probe-design.svg?style=flat) ![](https://img.shields.io/github/release-date/ggirelli/ifish-probe-design.svg?style=flat) ![](https://img.shields.io/github/languages/code-size/ggirelli/ifish-probe-design.svg?style=flat)  
![](https://img.shields.io/github/watchers/ggirelli/ifish-probe-design.svg?label=Watch&style=social) ![](https://img.shields.io/github/stars/ggirelli/ifish-probe-design.svg?style=social)

[PyPi](https://pypi.org/project/ifpd/) | [docs](https://ggirelli.github.io/iFISH-probe-design/)


**iFISH-Probe-Design** (`ifpd`) is a Python3.6.1+ package containing tools for selection of complementary oligonucleotides to build iFISH probes. It also includes a web interface, which simplifies the procedure by removing any requirement for programming skills. Read the online [documentation](https://ggirelli.github.io/iFISH-probe-design/) for more details.

## Requirements

**iFISH-Probe-Designer** is fully implemented in Python3.6.1+, thus you need Python3 to run it. Check out [here](https://realpython.com/installing-python/) how to install Python3.6.1+ on your machine if you don't have it yet.

`ifpd` has been tested with Python 3.6.1, 3.7, and 3.8. We recommend installing it using `pipx` (see [below](https://github.com/ggirelli/ifish-probe-design#install)) to avoid dependency conflicts with other packages. The packages it depends on are listed in our [dependency graph](https://github.com/ggirelli/ifish-probe-design/network/dependencies). We use [`poetry`](https://github.com/python-poetry/poetry) to handle our dependencies.

## Installation

We recommend installing `ifpd` using [`pipx`](https://github.com/pipxproject/pipx). Check how to install `pipx` [here](https://github.com/pipxproject/pipx#install-pipx) if you don't have it yet!

Once you have `pipx` ready on your system, install the latest stable release of `ifpd` by running: `pipx install ifpd`. If you see the stars (✨ 🌟 ✨), then the installation went well!

## Usage

More details on how to run **iFISH-Probe-Design** are available in the online [documentation](https://ggirelli.github.io/iFISH-probe-design/usage).

## Contributing

We welcome any contributions to `ifpd`. In short, we use [`black`](https://github.com/psf/black) to standardize code format. Any code change also needs to pass `mypy` checks. For more details, please refer to our [contribution guidelines](https://github.com/ggirelli/ifish-probe-design/blob/main/CONTRIBUTING.md) if this is your first time contributing! Also, check out our [code of conduct](https://github.com/ggirelli/ifish-probe-design/blob/main/CODE_OF_CONDUCT.md).

### Reference

* Gelali, E., Girelli, G., Matsumoto, M., Wernersson, E., Custodio, J., Mota, A., ... & Bienko, M. (2019). iFISH is a publically available resource enabling versatile DNA FISH to study genome architecture. Nature communications, 10(1), 1-15. ([link](https://www.nature.com/articles/s41467-019-09616-w))

## License

`MIT License - Copyright (c) 2016-21 Gabriele Girelli`
