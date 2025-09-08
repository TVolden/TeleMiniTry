# TeleMiniTry
[![DOI](https://zenodo.org/badge/898652756.svg)](https://doi.org/10.5281/zenodo.17077340)

A small telemetry service in Python

## Installation

1. Clone the repository
2. Install requirements
3. Start flask

### 1. Clone the repository
Clone this repository and enter the folder.

### 2. Install requirements
It's recommended that you create a virtual environment:

``` bash
python -m venv .venv
\.venv\scripts\activate
```

Update pip and install requirements
```bash
python -m pip install --upgrade pip
pip install -r requirements.txt
```

### 3. Start flask
Now start the server with the flask debugger.

```bash
flask run
```

## Getting started
Browse the example folder: `/test`\
for example: `http://127.0.0.1:5000/test`\
Username and password: `test`

Browse `/new` to create clients.

Post messages to `/echo` to see what the server receives.
