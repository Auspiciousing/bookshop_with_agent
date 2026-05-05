import os

from dotenv import load_dotenv
from sqlalchemy import create_engine, text


def main() -> None:
	load_dotenv(override=False)
	database_url = os.getenv("BOOKS_DB_URL")
	if not database_url:
		raise SystemExit("BOOKS_DB_URL is not set in .env")

	engine = create_engine(database_url, pool_pre_ping=True)
	try:
		with engine.connect() as conn:
			conn.execute(text("SELECT 1"))
		print("DB connection OK")
	except Exception as exc:
		print(f"DB connection failed: {exc}")


if __name__ == "__main__":
	main()
