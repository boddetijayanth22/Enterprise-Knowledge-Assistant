from sqlalchemy import inspect, text

from app.database.connection import Base, engine
from app.database.models import User
from app.database.document_models import Document


def migrate_documents_table():
    inspector = inspect(engine)

    if "documents" not in inspector.get_table_names():
        return

    columns = {
        column["name"]
        for column in inspector.get_columns("documents")
    }

    if "status" not in columns:
        with engine.begin() as connection:
            connection.execute(
                text(
                    """
                    ALTER TABLE documents
                    ADD COLUMN status VARCHAR(20)
                    NOT NULL
                    DEFAULT 'processing'
                    """
                )
            )


def init_db():
    Base.metadata.create_all(bind=engine)
    migrate_documents_table()


if __name__ == "__main__":
    init_db()
    print("Database initialized successfully.")