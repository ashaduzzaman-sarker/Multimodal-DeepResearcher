from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="multimodal-deepresearcher",
    version="1.0.0",
    author="Ashaduzzaman Sarker",
    author_email="ashaduzzaman@gmail.com",
    description="AI-powered multimodal research report generator",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/ashaduzzaman-sarker/Multimodal-DeepResearcher",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Researchers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.9",
    install_requires=[
        "openai>=1.12.0",
        "aiohttp>=3.8.0",
        "asyncio-throttle>=1.0.2",
        "pydantic>=2.0.0",
        "pyyaml>=6.0",
        "pandas>=2.0.0",
        "matplotlib>=3.7.0",
        "seaborn>=0.12.0",
        "plotly>=5.15.0",
        "beautifulsoup4>=4.12.0",
        "requests>=2.31.0",
        "python-dotenv>=1.0.0",
        "markdown>=3.4.0",
        "jinja2>=3.1.0",
        "fastapi>=0.100.0",
        "uvicorn>=0.23.0",
        "rich>=13.0.0",
        "typer>=0.9.0",
        "aiofiles>=23.0.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-asyncio>=0.21.0",
            "black>=23.0.0",
            "flake8>=6.0.0",
            "mypy>=1.0.0",
        ]
    },
    entry_points={
        "console_scripts": [
            "deepresearcher=scripts.generate_report:main",
            "deepresearcher-batch=scripts.batch_generate:main",
            "deepresearcher-web=scripts.web_interface:main",
        ],
    },
)