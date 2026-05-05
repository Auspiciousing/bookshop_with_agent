CREATE DATABASE IF NOT EXISTS secondhand_books
  DEFAULT CHARACTER SET utf8mb4
  DEFAULT COLLATE utf8mb4_general_ci;

USE secondhand_books;

DROP VIEW IF EXISTS book_inventory;
DROP TABLE IF EXISTS order_item;
DROP TABLE IF EXISTS orders;
DROP TABLE IF EXISTS books;
DROP TABLE IF EXISTS shopping_cart;
DROP TABLE IF EXISTS users;

CREATE TABLE users (
  id INT AUTO_INCREMENT PRIMARY KEY,
  username VARCHAR(50) NOT NULL UNIQUE,
  password VARCHAR(100) NOT NULL,
  wallet FLOAT NOT NULL DEFAULT 0,
  avatar_url VARCHAR(100),
  nickname VARCHAR(50),
  gender VARCHAR(8),
  birthday VARCHAR(20),
  self_statement TEXT,
  email VARCHAR(100),
  phone VARCHAR(20),
  address VARCHAR(200),
  created_at DATETIME,
  change_password_at DATETIME
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE shopping_cart (
  user_id INT,
  seller_id INT,
  seller_username VARCHAR(100),
  item_id INT AUTO_INCREMENT PRIMARY KEY,
  amount INT,
  id INT,
  title VARCHAR(100),
  author VARCHAR(100),
  publisher VARCHAR(100),
  description TEXT,
  price FLOAT,
  picture_url VARCHAR(500),
  chosen TINYINT(1)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE books (
  id INT AUTO_INCREMENT PRIMARY KEY,
  title VARCHAR(200) NOT NULL,
  author VARCHAR(100),
  publisher VARCHAR(100),
  description TEXT,
  price FLOAT NOT NULL,
  stock INT,
  seller_id INT NOT NULL,
  picture_url VARCHAR(500),
  CONSTRAINT fk_books_seller_id
    FOREIGN KEY (seller_id) REFERENCES users (id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE orders (
  id INT AUTO_INCREMENT PRIMARY KEY,
  user_id INT,
  user_address VARCHAR(100),
  total_price FLOAT,
  status VARCHAR(20),
  created_at DATETIME,
  payment_deadline DATETIME,
  paid_at DATETIME,
  completed_at DATETIME,
  cancelled_at DATETIME,
  CONSTRAINT fk_orders_user_id
    FOREIGN KEY (user_id) REFERENCES users (id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE order_item (
  id INT AUTO_INCREMENT PRIMARY KEY,
  order_id INT,
  seller_id INT,
  status VARCHAR(20),
  seller_username VARCHAR(100),
  seller_address VARCHAR(100),
  book_price FLOAT,
  book_amount INT,
  book_id INT,
  book_title VARCHAR(100),
  book_author VARCHAR(100),
  CONSTRAINT fk_order_item_order_id
    FOREIGN KEY (order_id) REFERENCES orders (id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

ALTER TABLE shopping_cart
  ADD CONSTRAINT fk_shopping_cart_user_id
  FOREIGN KEY (user_id) REFERENCES users (id);

ALTER TABLE books
  ADD FULLTEXT INDEX idx_book_title_fulltext (title);

ALTER TABLE books
  ADD FULLTEXT INDEX idx_book_description_fulltext (description);

ALTER TABLE books
  ADD FULLTEXT INDEX idx_book_author_fulltext (author);

ALTER TABLE books
  ADD FULLTEXT INDEX idx_fulltext_combined (title, author, description);

CREATE OR REPLACE VIEW book_inventory AS
SELECT
  b.id AS book_id,
  b.title,
  b.author,
  b.price,
  b.stock AS total_stock,
  COALESCE(SUM(
    CASE WHEN o.status IN ('pending_payment', 'paid', 'shipped')
      THEN oi.book_amount ELSE 0 END
  ), 0) AS reserved_quantity,
  b.stock - COALESCE(SUM(
    CASE WHEN o.status IN ('pending_payment', 'paid', 'shipped')
      THEN oi.book_amount ELSE 0 END
  ), 0) AS available_stock
FROM books b
LEFT JOIN order_item oi ON b.id = oi.book_id
LEFT JOIN orders o ON oi.order_id = o.id
GROUP BY b.id, b.title, b.author, b.price, b.stock;
