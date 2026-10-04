# What is the VendorsApp?

It is an application for distribution companies so that they can connect their stock, vendors, clients, and generate orders with only one click, and being sure that the order comes with available product. In Costa Rica this process is really manual, and there are usually many problems with the orders, due to the fact that most of the vendors ask for unavailable products.

## Feature domains:

- **auth:** We have a login, which the users are already defined, because this should not be a public page.
- **catalog:** The posibility to search by code and description and find the product you want, and shows the stock of active products with available stock.
- **sales:** Vendor can see teh details of the order before generating it, and generates an order and relates the product, order, client, and vendor all in one.

To use the project you should have a github account to clone the repository and python installed in your computer.

## Steps to use the application:

### 1. Clone the repository using:

```bash
git clone https://github.com/Toby2200/SDAD-VendorsApp.git
```

cd `SDAD-VendorsAPP`

### 2. Create a virtual environment which ever you want to use.

Instructions to do it with venv:

**Mac:**

```bash
python3 -m venv venv

source venv/bin/activate
```

**Windows:**

```bash
python -m venv venv
```

(Command Prompt)

```bat
venv\Scripts\activate
```

(Powershell)

```powershell
venv\Scripts\Activate.ps1
```

### 3. Install Requirements

To run the app you should install flask, werkzeug, pytest, and pytest-cov. But they are already in the `requirements.txt`. So just run the command:

```bash
pip install -r requirements.txt
```

### 4. Run the application

To run the application you just write the command:

```bash
python app.py
```

### 5. Browse the url:

http://127.0.0.1:5000 or `http://127.0.0.1:PORT`

When run the app automaticlaly creates the databse if it does not exist with the tables, and then if the tables are empty it generates the mock data.

The environment variables are `PORT=5000`, `DATA_DIR=./data`, `SECRET_KEY=dev-secret-key`, `FLASK_DEBUG=0`. WE have default variables.

To assign any other values to this variables:

**Windows (Powershell):**

```powershell
$env:PORT="8080"; $env:DATA_DIR="C:\vendors-data"; python app.py
```

**Mac (BASH):**

```bash
PORT=8080 DATA_DIR=/tmp/vendors-data python app.py
```

The database will be located in the main root inside the data folder. To find it also: `SDAD-VendorsApp/data/app.db`

To reset the data from the database just delete the data folder or the one you pu in DATA_DIR.

## The users or vendors are:

**Vendor 1:**
- email: `andres@test.com`
- password: `123456`

**Vendor 2:**
- email: `maria@test.com`
- password: `abcdef`

**Vendor 3 incative should not be able to enter:**
- email: `carlos@test.com`
- password: `password123`

## Tests and coverage

Each test runs against its own temporary copy of a seeded SQLite database
(`tests/conftest.py`), so results are the same.

Run the tests:

```bash
python -m pytest -q
```

Run the tests with coverage:

```bash
python -m pytest --cov=auth --cov=catalog --cov=sales --cov=database --cov-report=term-missing
```

### Result:

```
============================================================ tests coverage ============================================================
______________________________________________________________________________ coverage: platform win32, python 3.12.6-final-0 ______________________________________________________________________________

Name                   Stmts   Miss  Cover   Missing
----------------------------------------------------
auth\__init__.py           0      0   100%
auth\decorators.py         9      0   100%
auth\routes.py            18      0   100%
auth\service.py           16      0   100%
catalog\routes.py         25      0   100%
catalog\service.py        35      0   100%
database\database.py      24      0   100%
database\seed.py          50      1    98%   113
sales\routes.py           41      2    95%   51, 73
sales\service.py          69      5    93%   143, 152-155
----------------------------------------------------
TOTAL                    287      8    97%
============================================================ 69 passed in 1.37s ============================================================
```

## Project structure:

```
SDAD-VendorsApp/
├── app.py              # Entry point: creates the app, DB and blueprints
├── README.md           # HERE
├── requirements.txt
├── auth/               # Domain: login, logout, login_required
├── catalog/            # Domain: products, search, stock validation
├── sales/              # Domain: clients, cart, checkout / orders
├── database/           # SQLite connection, schema and seed data
├── templates/          # Jinja2 HTML templates (base.html + pages)
├── static/css/         # Styles
├── tests/              # pytest tests + conftest.py
├── ADR.md              # Architecture Decision Records
└── AI_USAGE.md         # AI usage log
```