# Introduction

Hi there, thank you for considering contributing to `iFISH-Probe-Design` to help us make our code a better version of itself!

`iFISH-Probe-Design` is an open source project, and as such any kind of contribution is welcome! There are many ways to contribute, from improving the code, the documentation, submitting bug reports, requesting new features or writing tutorials or blog posts.

# Ground Rules

To see what kinds of behaviour are ucceptable when contributing to `iFISH-Probe-Design`, please refer to our [code of conduct](https://ggirelli.github.io/gpseqc/code_of_conduct).

# Getting started

We host `iFISH-Probe-Design` on github, where we also track issues and feature requests, as well as accept pull requests.

Please, note that any contributions you make will be under the MIT Software License. In other words, all your submissions are understood to be under the same [MIT License](http://choosealicense.com/licenses/mit/) that covers the `iFISH-Probe-Design` project. Feel free to contact us if that's a concern.

## How to submit a contribution

To process code change, we follow the [Github Flow](https://guides.github.com/introduction/flow/index.html). All code changes to our `master` branch happen through pull requests. We actively welcome your pull requests!

## How to report a bug

If you want to reporte a **bug**, please use the github [issue tracker](https://github.com/ggirelli/iFISH-Probe-Design/issues) and follow the issue template that should automatically load up.

## How to suggest a feature or enhancement

If you would like to see a new feature implemented in `iFISH-Probe-Design`, or to have an already existing feature improved, please use the github [issue tracker](https://github.com/ggirelli/iFISH-Probe-Design/issues) and follow the template that should automatically load up.

# Style your contributions

We like to have `ifpd` code styled with [`black`](https://github.com/psf/black) and checked with `mypy`. `mypy`, `flake8`, and `black` conforming checks are automatically ran on all pull requests through GitHub Actions.

# Changing dependencies

If your code changes `ifpd` dependencies, we recommend to change them in the `pyproject.toml` file and then regenerate `requirements.txt` by running:

```
poetry export -f requirements.txt -o requirements.txt --without-hashes
```

See [poetry](https://github.com/python-poetry/poetry)'s documentation for more details on the format of the `pyproject.toml` file.
