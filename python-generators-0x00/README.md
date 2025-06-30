# ALX Backend Python - Generators

This repository contains solutions for the ALX Backend Python project on generators, focusing on efficient data streaming from a MySQL database.

## Directory: python-generators-0x00

### Files
- **seed.py**: Sets up the `ALX_prodev` database, creates the `user_data` table, and populates it with data from `user_data.csv`.
- **0-stream_users.py**: Implements a generator to stream rows one by one from the `user_data` table.
- **1-batch_processing.py**: Implements batch processing to fetch and filter users over 25 years old.
- **2-lazy_paginate.py**: Implements lazy pagination for fetching data in pages.
- **4-stream_ages.py**: Computes the average age of users using a memory-efficient generator.

## Setup
1. Install MySQL and Python MySQL Connector:
   ```bash
   sudo apt-get install mysql-server
   pip install mysql-connector-python
   ```
2. Ensure `user_data.csv` is available in the project directory.
3. Run the scripts in order, starting with `0-main.py` to set up the database.

## Usage
- Run `0-main.py` to initialize the database and table.
- Execute other main scripts (`1-main.py`, `2-main.py`, `3-main.py`) to test the respective functionalities.

## Requirements
- Python 3.8+
- MySQL Server
- MySQL Connector for Python
- `user_data.csv` with columns: name, email, age

## Repository
- **GitHub Repository**: alx-backend-python
- **Directory**: python-generators-0x00
