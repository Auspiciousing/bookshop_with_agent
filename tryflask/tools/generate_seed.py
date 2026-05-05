import pathlib
from datetime import datetime


def parse_sql_values(values_text):
    values = []
    i = 0
    n = len(values_text)
    while i < n:
        ch = values_text[i]
        if ch.isspace() or ch == ",":
            i += 1
            continue
        if ch == "'":
            i += 1
            buf = []
            while i < n:
                ch = values_text[i]
                if ch == "\\":
                    if i + 1 < n:
                        buf.append(values_text[i + 1])
                        i += 2
                        continue
                if ch == "'":
                    if i + 1 < n and values_text[i + 1] == "'":
                        buf.append("'")
                        i += 2
                        continue
                    i += 1
                    break
                buf.append(ch)
                i += 1
            values.append("".join(buf))
        else:
            start = i
            while i < n and values_text[i] != ",":
                i += 1
            token = values_text[start:i].strip()
            values.append(token)
    return values


def sql_escape(value):
    if value is None:
        return "NULL"
    if isinstance(value, str):
        return "'" + value.replace("\\", "\\\\").replace("'", "''") + "'"
    return str(value)


def load_books(sql_path):
    content = sql_path.read_text(encoding="utf-8")
    books = []
    for line in content.splitlines():
        if not line.startswith("INSERT INTO `books` VALUES"):
            continue
        start = line.find("(")
        end = line.rfind(")")
        if start == -1 or end == -1:
            continue
        values_text = line[start + 1:end]
        values = parse_sql_values(values_text)
        if len(values) < 7:
            continue
        book_id = int(values[0])
        title = values[1]
        author = values[2]
        price = values[3]
        description = values[4]
        seller = values[5]
        stock = int(values[6])
        books.append(
            {
                "id": book_id,
                "title": title,
                "author": author,
                "price": price,
                "description": description,
                "seller": seller,
                "stock": stock,
            }
        )
    return books


def main():
    root = pathlib.Path(__file__).resolve().parent.parent
    books_sql = root / "books.sql"
    output_sql = root / "seed.sql"

    books = load_books(books_sql)
    sellers = sorted({book["seller"] for book in books})
    seller_id_map = {name: idx + 1 for idx, name in enumerate(sellers)}

    lines = []
    lines.append("SET NAMES utf8mb4;")
    lines.append("SET FOREIGN_KEY_CHECKS = 0;")
    lines.append("")

    # Users
    lines.append("-- users")
    lines.append("INSERT INTO users (id, username, password, wallet, created_at, change_password_at) VALUES")
    user_values = []
    for name in sellers:
        user_values.append(
            "(" + ", ".join(
                [
                    str(seller_id_map[name]),
                    sql_escape(name),
                    sql_escape("123456"),
                    "0",
                    "NOW()",
                    "NOW()",
                ]
            ) + ")"
        )
    lines.append(",\n".join(user_values) + ";")
    lines.append("")

    # Books
    lines.append("-- books")
    lines.append(
        "INSERT INTO books (id, title, author, publisher, description, price, stock, seller_id, picture_url) VALUES"
    )
    book_values = []
    for book in books:
        book_values.append(
            "(" + ", ".join(
                [
                    str(book["id"]),
                    sql_escape(book["title"]),
                    sql_escape(book["author"]),
                    "NULL",
                    sql_escape(book["description"]),
                    str(book["price"]),
                    str(book["stock"]),
                    str(seller_id_map[book["seller"]]),
                    "NULL",
                ]
            ) + ")"
        )
    lines.append(",\n".join(book_values) + ";")
    lines.append("")

    # Empty tables (explicitly noted)
    lines.append("-- shopping_cart: no seed data")
    lines.append("-- orders: no seed data")
    lines.append("-- order_item: no seed data")
    lines.append("")
    lines.append("SET FOREIGN_KEY_CHECKS = 1;")

    output_sql.write_text("\n".join(lines), encoding="utf-8")
    print(f"Wrote {output_sql}")


if __name__ == "__main__":
    main()
