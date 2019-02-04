# iFISH-Probe-Design v2.0.1.post5

**iFISH-Probe-Design** (`ifpd`) is a Python3 package containing tools for selection of complementary oligonucleotides to build iFISH probes. It also includes a web interface, which simplifies the procedure by removing any requirement for programming skills. Read the online [documentation](https://ggirelli.github.io/iFISH-probe-design/) for more details.

Installation
---

If you have Python3 and `pip3` installed on your computer, you can simply run `sudo -H pip3 install ifpd` on a terminal. That's it! As easy as it gets.

You can also install from github (any point in history, although we suggest to stick with release tags) as follows:

```bash
git clone https://github.com/ggirelli/iFISH-probe-design/
cd iFISH-probe-design
sudo -H pip3 install .
```

For a nice guide on installing packages served through PyPI, check out [this tutorial](https://packaging.python.org/tutorials/installing-packages/).

Requirements
---

**iFISH-Probe-Designer** is fully implemented in Python3, thus you need Python3 to run it. Check out [here](https://realpython.com/installing-python/) how to install Python3 on your machine if you don't have it yet.

If you installed this package using `pip3` (as explained [above](#installation)), then all required libraries were also automatically installed. Nonetheless, here is a list (with version) of the required libraries:

* `bottle>=0.12.13` and `paste>=2.0.3`: to run the web server interface.
* `ggc>=0.0.3`: for functionalities common to all my packages.
* `matplotlib>=3.0.0`: to plot.
* `numpy>=1.14.2`, `pandas>=0.22.0`, and `scipy>=1.0.0`: for data manipulation.

Usage
---

More details on how to run **iFISH-Probe-Design** are available in the online [documentation](https://ggirelli.github.io/iFISH-probe-design/usage).

Contributing
---

We welcome any contributions to `iFISH-Probe-Design`. Please, refer to the [contribution guidelines](https://ggirelli.github.io/iFISH-probe-design/contributing) if this is your first time contributing! Also, check out our [code of conduct](https://ggirelli.github.io/iFISH-probe-design/code_of_conduct).

License
---

```
MIT License
Copyright (c) 2016-2019 Gabriele Girelli
```
