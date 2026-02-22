# Project Setup

## Set up Repo
In Github:
Create new repo called assignment_5 and make sure it is public

In WSL/VS Code Terminal:
```bash
mkdir assignment_5
cd assignment_5/
git init
git branch -m main
git remote add origin git@github.com:mbel12345/assignment_5.git
vim README.md
git add . -v
git commit -m "Initial commit"
git push -u origin main
```

## Set up virtual environment
In WSL/VS Code Terminal:
```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## Run test cases
In WSL/VS Code Terminal:
```bash
pytest
```

## Run the calculator
In WSL/VS Code Terminal:
```bash
python3 main.py
```
