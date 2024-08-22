# All Sky Camera System for Optical Low Earth Orbit Satellite DownLinks [![python version](https://img.shields.io/badge/python-3.7+-blue.svg)](https://www.python.org/downloads/)

This project was developed in collaboration with DLR-IKN in Oberpfaffenhofen as part of my Bachelor Thesis. The goal is to track and assess the quality of Optical Low Earth Orbit Satellite DownLinks (OLEODL) as a validation tool for an Optical Ground Station using Allied Vision cameras.

## Documentation and Resources

- [AllSkyCam4OLEODL documentation](https://allskycam4oleodl.readthedocs.io/en/latest/): Comprehensive documentation of the package.
- [VmbPy GitHub Repository](https://github.com/alliedvision/VmbPy): Official GitHub repository for the Allied Vision API.
- [VmbPy Documentation](https://docs.alliedvision.com/Vimba_X/Vimba_X_DeveloperGuide/pythonAPIManual.html): Detailed documentation for the Allied Vision API.


---

## Installation

### Prerequisites

Ensure Git is installed on your system.

### Installing the AllSkyCam4OLEODL Package

Git needs to be installed first.

1. Install the PyPI package:
```bash
pip install allskycam4oleodl
```
2. Clone the AllSkyCam4OLEODL Git repository:
```bash
git clone https://github.com/Ikerald/AllSkyCam4OLEODL.git
```
3. Navigate to the AllSkyCam4OLEODL directory:
```bash
cd AllSkyCam4OLEODL/
```
4. Manually install the VmbPy API:
```bash
pip install './data/vmbpy-1.0.4-py3-none-any.whl[numpy,opencv]'
```
> **NOTE**  
> If you prefer to install VmbPy separately, the `.whl` file can be downloaded from the [github release page](https://github.com/alliedvision/VmbPy/releases). It can then be installed through the usual via the [`pip install`](https://pip.pypa.io/en/stable/cli/pip_install/) command.
>

---
## Usage

To run the program, execute the main file in the AllSkyCam4OLEODL directory:
```bash
python main.py
```
