from setuptools import setup, find_packages

setup(
    name="DocsVerse",
    version="1.0.0",
    packages=find_packages(),
    install_requires=[
        "fastapi>=0.104.1",
        "sqlalchemy>=2.0.40",
        "pydantic>=2.4.2",
        "pydantic-settings>=2.1.0",
        "uvicorn>=0.23.2",
        "python-dotenv>=1.0.0",
        "sqlalchemy-utils>=0.41.2",
        "alembic>=1.15.2"
    ],
    python_requires=">=3.8"
)
