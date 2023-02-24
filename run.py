"""Flask CLI/Application entry point."""
import os

from flask_api_assets import create_app, db
from flask_api_assets.models.asset import Asset

# from flask_api_extension.models.category import Category

app = create_app(os.getenv("FLASK_ENV", "True"))


@app.shell_context_processor
def shell():
    return {
        "db": db,
        "Asset": Asset,
    }
