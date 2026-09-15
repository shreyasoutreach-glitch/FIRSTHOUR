import sqlite3
conn = sqlite3.connect("first_hour.db")
conn.execute("DROP TABLE IF EXISTS alembic_version")
conn.commit()
conn.close()
