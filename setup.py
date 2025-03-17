"""
Setup script for the Medical Document Analyzer
"""

from setuptools import setup, find_packages

required_packages = [
    "fastapi>=0.105.0",
    "uvicorn>=0.24.0",
    "python-multipart>=0.0.6",
    "pydantic>=2.5.0",
    "pydantic-settings>=2.1.0",
    "jinja2>=3.1.2",
    "langchain-core>=0.1.0",
    "langgraph>=0.1.0",
    "langchain-ollama>=0.0.1",
    "langchain-community>=0.0.16",
    "python-dotenv>=1.0.0",
    "pymupdf>=1.22.0",  # For direct PDF text extraction
]

# Optional dependencies for different components
tesseract_requires = [
    "pytesseract>=0.3.10",
    "pdf2image>=1.16.3",
]

paddle_requires = [
    "paddleocr>=2.6.0.1",
    "pdf2image>=1.16.3",
]

llamacpp_requires = [
    "llama-cpp-python>=0.2.0",
]

dev_requires = [
    "pytest>=7.0.0",
    "black>=23.0.0",
    "isort>=5.12.0",
    "flake8>=6.0.0",
]

setup(
    name="medical-analyzer",
    version="1.0.0",
    description="Medical Document Analysis using Open Source LLMs and LangGraph",
    author="Your Name",
    author_email="your.email@example.com",
    packages=find_packages(),
    include_package_data=True,
    install_requires=required_packages,
    extras_require={
        "tesseract": tesseract_requires,
        "paddle": paddle_requires,
        "llamacpp": llamacpp_requires,
        "dev": dev_requires,
        "all": tesseract_requires + paddle_requires + llamacpp_requires + dev_requires,
    },
    entry_points={
        "console_scripts": [
            "medical-analyzer=medical_analyzer.app:main",
        ],
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Healthcare Industry",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.10",
)