import os
import sys
import bcrypt
import getpass
import sqlite3
from typing import Any, Iterable, Literal, cast


class SQL:
    SELECT: str = "SELECT {}"
    FROM: str = "FROM {}"
    WHERE: str = "WHERE {}"
    ORDER_BY: str = "ORDER BY {} {}"
    ASCENDING: str = "ASC"
    DECENDING: str = "DESC"

    def __init__(self, database_file: str) -> None:
        self.db_file: str = database_file
        self.db: sqlite3.Connection | None = None

        if not os.path.isfile(self.db_file):
            self.create_database()

    def create_database(self) -> None:
        querey: str = (
            "CREATE TABLE main.accounts (\n"
            + "id INTEGER PRIMARY KEY NOT NULL UNIQUE,\n"
            + "first_name TEXT NOT NULL,\n"
            + "last_name TEXT NOT NULL,\n"
            + "balance REAL NOT NULL DEFAULT 0,\n"
            + "password_hash TEXT NOT NULL\n"
            + ");"
        )

        self.execute(querey)

    def connect(self) -> None:
        self.db = sqlite3.connect(self.db_file)

    def get_cursor(self) -> sqlite3.Cursor:
        if not self.db:
            self.connect()
        
        return cast(sqlite3.Connection, self.db).cursor()

    def close_db(self) -> None:
        if self.db:
            self.db.close()
        
        self.db = None

    def execute(self, command: str, parameters = ()) -> Any:
        if not self.db:
            self.connect()

        cursor: sqlite3.Cursor = self.get_cursor()
        cursor.execute(command, parameters)
        results: list[Any] | None = None
        try:
            results =  cursor.fetchall()
        except Exception as e:
            pass

        cast(sqlite3.Connection, self.db).commit()
        cursor.close()
        self.close_db()
        return results

    def get(
            self, 
            rows: str, 
            table: str, 
            condition: str, 
            order_by: Literal["ASC", "DESC"] | None = None,
            parameters = ()
    ) -> list[Any]:
        message: str = (
            SQL.SELECT.format(rows) + "\n"
            + SQL.FROM.format(table) + "\n"
            + SQL.WHERE.format(condition) + "\n"
        )

        if order_by:
            message += SQL.ORDER_BY.format(order_by)

        return self.execute(message, parameters)
    

class User:
    def __init__(
            self,
            first_name: str,
            last_name: str,
            account_balance: float, 
            password_hash: bytes
    ) -> None:
        self.first_name: str = first_name
        self.last_name: str = last_name
        self.account_balance: float = account_balance
        self.password_hash: bytes = password_hash


def clear_screen() -> None:
    os.system("cls" if os.name == "nt" else "clear")


def get_float(
        message: str, 
        minimum_value: float | None = None,
        maximum_value: float | None = None,
        values: Iterable[float] | None = None
) -> float:
    while True:
        try:
            value: float = float(input(message))
        except ValueError:
            print("Please enter an integer")
            continue

        if values and value not in values:
            print("The inputted value is not valid.")
            continue

        if minimum_value and value < minimum_value:
            print(f"The minimum value is {minimum_value}")
            continue

        if maximum_value and value > maximum_value:
            print(f"The maximum value is {maximum_value}")
            continue

        return value


def get_int(message: str, values: Iterable[int] | None = None) -> int:
    while True:
        try:
            value: int = int(input(message))
        except ValueError:
            print("Please enter an integer")
            continue

        if values and value not in values:
            print("The inputted value is not valid.")
            continue

        return value
    

def hash_pw(message: str) -> bytes:
    with open("salt.txt", "rb") as f:
        salt: bytes = f.read().strip()

    bytes_message: bytes = message.encode()
    
    return bcrypt.hashpw(bytes_message, salt)



def create_user(sql: SQL) -> None:
    clear_screen()

    first_name: str = input("Enter your first name: ").lower()
    last_name: str = input("Enter your last name: ").lower()
    try:
        password: str = getpass.getpass()
    except Exception as e:
        print("Error: Could not get password.")
        print(str(e))
        print("Please try again later")
        return
    
    try:
        password_confirm: str = getpass.getpass("Please confirm your password: ")
    except Exception as e:
        print("Error: Could not get password.")
        print(str(e))
        print("Please try again later")
        return
    
    if password != password_confirm:
        output_menu(
            menu_title="Invalid password",
            options=("The passwords did not match",),
            option_zero=None,
            show_indexes=False
        )
        pause()
        return
    
    if len(password) < 8:
        output_menu(
            menu_title="Invalid password",
            options=("The password must be at least 8 characters",),
            option_zero=None,
            show_indexes=False
        )
        pause()
        return
    
    querey: str = (
        "INSERT INTO main.accounts (first_name, last_name, password_hash)\n"
        + "VALUES (?, ?, ?)"
    )

    sql.execute(querey, (first_name, last_name, hash_pw(password)))
    

def output_menu(
        menu_title: str, 
        options: tuple[str, ...], 
        option_zero: str | None = "exit",
        show_indexes: bool = True
) -> None:
    clear_screen()

    max_option_length: int = 0
    for option in options:
        if len(option) > max_option_length:
            max_option_length = len(option)

    print('#'*(max_option_length + 9))
    print(f"## {menu_title:^{max_option_length+3}} ##")

    print('#'*(max_option_length + 9))
    
    for i, option in enumerate(options):
        if show_indexes:
            print(f"## {i+1}. {option:<{max_option_length}} ##")
        else:
            print(f"## {option:<{max_option_length+3}} ##")
    
    if option_zero:
        print(f"## 0. {option_zero:<{max_option_length}} ##")
    
    print('#'*(max_option_length + 9))


def show_balance(sql: SQL) -> None:
    clear_screen()

    user: User | None = get_authenticated_user(sql)

    if not user:
        pause()
        return
    
    options: tuple[str, ...] = (
        f"Account holder: {user.first_name.title()} {user.last_name.title()}",
        f"Balance: £{user.account_balance:.2f}"
    )
    output_menu(
        menu_title="Account balance", 
        options=options, 
        option_zero=None, 
        show_indexes=False
    )
    print("Click enter to return")
    input()


def deposit(sql: SQL) -> None:
    clear_screen()

    user: User | None = get_authenticated_user(sql)

    if not user:
        pause()
        return
    
    deposit_amount: float = get_float("Enter the deposit amount: £", minimum_value=0)
    new_balance = user.account_balance + deposit_amount

    querey_two: str = (
        "UPDATE main.accounts\n"
        + "SET balance = ?\n"
        + "WHERE first_name=? and last_name=? and password_hash=?"
    )

    sql.execute(querey_two, (
        new_balance, 
        user.first_name, 
        user.last_name, 
        user.password_hash
    ))
    return


def pause() -> None:
    input("Click enter to continue...")


def withdraw(sql: SQL) -> None:
    clear_screen()

    user: User | None = get_authenticated_user(sql)
    if not user:
        pause()
        return
    
    deposit_amount: float = get_float(
        f"Enter the withdraw amount (maximum £{user.account_balance:.2f}): £",
        minimum_value=0,
        maximum_value=user.account_balance
    )
    new_balance = user.account_balance - deposit_amount

    querey_two: str = (
        "UPDATE main.accounts\n"
        + "SET balance = ?\n"
        + "WHERE first_name=? and last_name=? and password_hash=?"
    )

    sql.execute(querey_two, (
        new_balance, 
        user.first_name, 
        user.last_name, 
        user.password_hash
    ))
    return


def get_authenticated_user(sql: SQL) -> User | None:
    first_name: str = input("Enter your first name: ").lower()
    last_name: str = input("Enter your last name: ").lower()

    try:
        password: str = getpass.getpass()
    except Exception as e:
        print("Error: Could not get password.")
        print(str(e))
        print("Please try again later")
        return
    
    password_hash: bytes = hash_pw(password)

    querey = (
        "SELECT balance, password_hash\n"
        + "FROM main.accounts\n"
        + "WHERE first_name=? and last_name=?"
    )

    result: list[Any] = sql.execute(querey, (first_name, last_name))

    if len(result) < 1:
        output_menu(
            menu_title="User not found", 
            options=("The requested user was not found",), 
            option_zero=None, 
            show_indexes=False
        )
        return
    
    account_balance: float
    account_password_hash: bytes
    account_balance, account_password_hash = result[0]

    if password_hash != account_password_hash:
        output_menu(
            menu_title="User not authenticated", 
            options=("The passwords did not match",), 
            option_zero=None, 
            show_indexes=False
        )
        return
    
    return User(first_name, last_name, account_balance, account_password_hash)


def main(args: list[str]) -> None:
    sql = SQL("bank.db")

    if "--create-db" in args:
        sql.create_database()

    while True:
        options: tuple[str, ...] = (
            "Create new account",
            "Show balance",
            "Deposit",
            "Withdraw"
        )

        output_menu("Main Menu", options)
        selected_option: int = get_int(
            "Enter an option: ",
            values=(0, 1, 2, 3, 4)
        )

        match selected_option:
            case 1:
                create_user(sql)

            case 2:
                show_balance(sql)
            
            case 3:
                deposit(sql)
            
            case 4:
                withdraw(sql)
            
            case 0:
                exit()
            
            case _:
                print("That is an invalid option")
    


if __name__ == "__main__":
    main(sys.argv[1:])