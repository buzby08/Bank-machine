# 🏦 Simple CLI Bank App (Python)

A command-line based bank account system written in Python. Users can:

- Create accounts (password-protected)
- View balances
- Deposit & withdraw funds

## 🔐 Security

Passwords are hashed using `bcrypt` with a salt stored in `salt.txt`.

## 💾 Database

SQLite is used. The app creates the `bank.db` file on first run if it doesn't exist.

## 🚀 How to Run

1. Generate a salt:

   ```python
   import bcrypt
   with open("salt.txt", "wb") as f:
       f.write(bcrypt.gensalt())
    ```

    or run the `generate_salt.py` file

    ```bash
    python3 generate_salt.py
    ```

2. Run the app:

    ```bash
    python3 main.py
    ```

3. Optionally force a database creation:

    ```bash
    python3 main.py --create-db
    ```
