"""Setup configuration for my-tiny-data-collider."""
from setuptools import setup, find_packages

setup(
    name="my-tiny-data-collider",
    version="0.1.0",
    description="YAML-driven tool generation framework with FastAPI and Google Workspace integrations",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    python_requires=">=3.11",
    install_requires=[
        "pydantic>=2.0.0",
        "fastapi>=0.100.0",
        "uvicorn>=0.23.0",
        "pyyaml>=6.0",
        "jinja2>=3.1.0",
        "google-auth>=2.0.0",
        "google-api-python-client>=2.0.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-asyncio>=0.21.0",
            "black>=23.0.0",
            "ruff>=0.0.280",
        ],
    },
    entry_points={
        "console_scripts": [
            "generate-tools=src.pydantic_ai_integration.tools.factory:generate_tools_cli",
        ],
    },
)
