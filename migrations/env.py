from alembic import context
from flask import current_app

migration = current_app.extensions["migrate"]
engine = migration.db.engine

if context.is_offline_mode():
    context.configure(
        url=engine.url.render_as_string(hide_password=False),
        target_metadata=migration.db.metadata,
        literal_binds=True,
    )
    with context.begin_transaction():
        context.run_migrations()
else:
    with engine.connect() as connection:
        context.configure(connection=connection, target_metadata=migration.db.metadata)
        with context.begin_transaction():
            context.run_migrations()

