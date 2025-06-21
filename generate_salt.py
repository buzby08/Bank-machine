import bcrypt

def main() -> None:
    with open("salt.txt", "wb") as f:
        f.write(bcrypt.gensalt())


if __name__ == "__main__":
    main()