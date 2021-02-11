---
title: Install ifpd
---

<!-- MarkdownTOC -->

- [Using `pipx`](#using-pipx)
- [Using `pip3`](#using-pip3)
- [Using `conda`](#using-conda)
- [Using `poetry`](#using-poetry)

<!-- /MarkdownTOC -->

`ifpd` is fully implemented in Python3, and is distributed through the PyPI network: the Python Package Manager developed and maintained by the Python community, for the Python community. As such, we recommend using `pip3` (PyPI package installer) to install `ifpd`. We also envision to pack it as a `conda` package in the future (*not available yet*).

## Using `pipx`

We recommend installing `ifpd` using [`pipx`](https://github.com/pipxproject/pipx). Check how to install `pipx` [here](https://github.com/pipxproject/pipx#install-pipx) if you don't have it yet!

Once you have `pipx` ready on your system, install the latest stable release of `ifpd` by running: `pipx install ifpd`. If you see the stars (✨ 🌟 ✨), then the installation went well!

## Using `pip3`

If you have Python3 and `pip3` installed on your computer, you can simply run `sudo -H pip3 install ifpd` on a terminal. That's it! As easy as it gets.

You can also install from github (any point in history, although we suggest to stick with release tags) as follows:

```bash
git clone https://github.com/ggirelli/iFISH-probe-design/
cd iFISH-probe-design
sudo -H pip3 install .
```

For a nice guide on installing packages served through PyPI, check out [this tutorial](https://packaging.python.org/tutorials/installing-packages/).

## Using `conda`

If you are a `conda` user, you can install `ifpd` by running the following:

```bash
conda skeleton pypi ifpd
conda build ifpd
```

Please, note that `ifpd` is a Python3 package tested on Python3.6. Thus, you will need to create an appropriate environment using `conda`.

## Using `poetry`

We use `poetry` as our dependency manager of choice and for our development environment. To open a shell (in a separate environment) with `ifpd` installed, simply do the following:

```
git clone https://github.com/ggirelli/iFISH-probe-design/
cd iFISH-probe-design
poetry update
poetry install
poetry shell
```

**Note** that using `poetry` does not support our GUI (accessible via `ifpd serve`). The GUI runs the queries as commands run in subprocesses, which are external to the poetry environment.