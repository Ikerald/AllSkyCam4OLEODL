# All Sky Camera System for Optical Low Earth Orbit Satellite DownLinks [![python version](https://img.shields.io/badge/python-3.7+-blue.svg)](https://www.python.org/downloads/)

This project has been developed in colaboration with DLR-IKN in Oberpfaffenhofen as a part of my Bachelor Thesis for tracking and assesing the quality of OLEODL as a validation tool for an Optical Ground Station based on Allied Vision Cameras.

See also 
- [AllSkyCam4OLEODL documentation](https://allskycam4oleodl.readthedocs.io/en/latest/) for a the full docuemntation of the package.
- [VmbPy GitHub](https://github.com/alliedvision/VmbPy) for the GitHub branch of the Allied Vision API.
- [VmbPy Documentation](https://docs.alliedvision.com/Vimba_X/Vimba_X_DeveloperGuide/pythonAPIManual.html) for the documentation of the the Allied Vision API.

---
# Installation

## Vmbpy API

To use this project the an installation of Vimba X and Python >= 3.7 are required. A ready-to-install packaged
`.whl` file of VmbPy can be found as part of the Vimba X installation, or be downloaded from our
[github release page](https://github.com/alliedvision/VmbPy/releases). The `.whl` can be installed
as usual via the [`pip install`](https://pip.pypa.io/en/stable/cli/pip_install/) command.

> **NOTE**  
> Depending on the some systems the command might instead be called `pip3`. Check your systems
> Python documentation for details.
>

```bash
pip install './data/vmbpy-1.0.4-py3-none-any.whl[numpy,opencv]'
```
## AllSkyCam4OLEODL package

Git needs to be installed first.

1. Install the Pypi package
```bash
pip install allskycam4oleodl
```
2. Clone the AllSkyCam4OLEODL git repository
```bash
git clone https://github.com/Ikerald/AllSkyCam4OLEODL.git
```
3. Navigate to the AllSkyCam4OLEODL sub-directory
```bash
cd AllSkyCam4OLEODL/
```
4. Here you can manually install the Vmbpy API
```bash
pip install './data/vmbpy-1.0.4-py3-none-any.whl[numpy,opencv]'
```









# Usage

```py
from project_name import BaseClass
from project_name import base_function

BaseClass().base_method()
base_function()
```

```bash
$ python -m project_name
#or
$ project_name
```