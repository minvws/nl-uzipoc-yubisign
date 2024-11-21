# Local setup

## Requirements
- `python3.13`
- `docker`
- `git`

## Installation
### 1.1 Creating a virtual environment
To create an isolated environment where we can install the Python requirements in, use the below command to use the `venv` package:

```bash
python -m venv .venv
source .venv/bin/activate
```

This will create the environment and activate it.

### 1.2 Installing the requirements
In the root of the project, open up a terminal and run the command underneath.

```bash
pip install -r requirements.txt
```



## Starting up the application
In the root of the project and the virtual environment activated, run the command below. Make sure you also have a Yubikey inserted in your computer.

```bash
python -m app.wizard
```

This will start up the application.

### Flow
1. ...
2. ...