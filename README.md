# FISH-ProDe v0.1.0

**FISH Pro**be **De**sign (**FISH-ProDe**, pronounced "pro‧de", "brave" or "valiant" in *italian*) is a Python3 package suite of tools for selection of complementary oligonucleotides to build FISH probes. It also includes a web interface to simplify the selection and remove any need for programming skills.

Read the [documentation](https://ggirelli.github.io/fish-prode/) for more details.

Installation
---

1. Clone the git repository locally.

```bash
git clone https://github.com/ggirelli/fish-prode/
cd fish-prode
```

2. Install Python2 dependencies (requires pip2, installed with `sudo apt install python-pip` or similar).

```bash
sudo -H pip2 install sqlite3 matplotlib numpy pandas scipy shutil urllib2 xml zipfile
```

3. Install Python3 dependencies (requires pip3 and python3, installed with `sudo apt install python3 python3-pip` or similar).

```bash
sudo -H pip3 install bottle numpy pandas paste
```

4. Download/Extract databases. More details in the [documentation](https://ggirelli.github.io/fish-prode/database).

Usage
---

More details on how to run **FISH-ProDe** are available in the [documentation](https://ggirelli.github.io/fish-prode/usage).

Contributing
---

We welcome any contributions to `FISH-ProDe`. Please, refer to the [contribution guidelines](https://ggirelli.github.io/fish-prode/contributing) if this is your first time contributing! Also, check out our [code of conduct](https://ggirelli.github.io/fish-prode/code_of_conduct).

License
---

```
MIT License
Copyright (c) 2017-2018 Gabriele Girelli
```