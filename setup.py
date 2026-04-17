"""
Setup configuration for packaging.
"""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="inflation-sentiment-engine",
    version="1.0.0",
    author="Data Engineering Team",
    author_email="data-team@sarb.co.za",
    description="AI-Powered Inflation Sentiment Engine for SARB",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/sarb/inflation-sentiment-engine",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.11",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: Financial and Insurance Industry",
        "Topic :: Office/Business :: Financial :: Point-of-Sale",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Topic :: Scientific/Engineering :: Information Analysis",
    ],
    python_requires=">=3.11",
    install_requires=[
        "python-dotenv>=1.0.0",
        "requests>=2.31.0",
        "tweepy>=4.14.0",
        "beautifulsoup4>=4.12.2",
        "psycopg2-binary>=2.9.9",
        "sqlalchemy>=2.0.23",
        "transformers>=4.35.2",
        "torch>=2.1.1",
        "numpy>=1.24.3",
        "pandas>=2.1.3",
        "boto3>=1.29.7",
        "fastapi>=0.109.0",
        "uvicorn>=0.27.0",
        "pydantic>=2.5.0",
        "pydantic-settings>=2.1.0",
    ],
    entry_points={
        "console_scripts": [
            "sentiment-engine=main:main",
            "sentiment-mcp=run_mcp_server:main",
        ],
    },
    include_package_data=True,
    package_data={
        "": ["*.md", ".env.example"],
    },
)
