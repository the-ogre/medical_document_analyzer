# Medical Document Analyzer

A fully open-source system for analyzing medical documents using local language models and OCR.

## Features

- Web-based interface for uploading and analyzing medical PDFs
- Extracts text using open-source OCR (Tesseract or PaddleOCR)
- Analyzes content using local open-source LLMs (Phi-3, Llama 3)
- Provides structured analysis, summary, and validation of medical content
- Runs entirely locally with no API costs or data leaving your system
- Visualizes the analysis pipeline using LangGraph

## Screenshots

![Medical Document Analyzer Interface](https://via.placeholder.com/800x450?text=Medical+Document+Analyzer+Interface)

## Architecture

This system uses a modular architecture with the following components:

- **FastAPI** - Web server and API framework
- **LangGraph** - Workflow orchestration for the analysis pipeline
- **Ollama/llama.cpp** - Local LLM inference engines
- **Tesseract/PaddleOCR** - Open-source OCR engines
- **PyMuPDF** - Direct PDF text extraction

## Requirements

- Python 3.10+
- For OCR: Tesseract (recommended) or PaddleOCR
- For LLMs: Ollama (recommended) or llama.cpp
- 8GB+ RAM recommended (16GB+ for better performance)
- GPU optional but recommended for faster inference

## Installation

### Quick Start

1. Clone the repository:
```bash
git clone https://github.com/yourusername/medical-document-analyzer.git
cd medical-document-analyzer
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Install Tesseract OCR (platform specific):
```bash
# Ubuntu/Debian
sudo apt-get install tesseract-ocr

# macOS
brew install tesseract

# Windows
# Download installer from https://github.com/UB-Mannheim/tesseract/wiki
```

4. Install Ollama from [ollama.ai](https://ollama.ai/download) and download the required models:
```bash
ollama pull phi3
ollama pull llama3
```

5. Start the application:
```bash
python run.py
```

6. Open your browser at [http://localhost:8000](http://localhost:8000)

### Docker Installation

1. Build and start the containers:
```bash
docker-compose up -d
```

2. Pull the required models:
```bash
docker exec -it medical-document-analyzer_ollama_1 ollama pull phi3
docker exec -it medical-document-analyzer_ollama_1 ollama pull llama3
```

3. Access the application at [http://localhost:8000](http://localhost:8000)

## Configuration

Copy the sample environment file and adjust as needed:
```bash
cp .env.sample .env
```

Key configuration options:
- `LLM_BACKEND`: Choose between "ollama" or "llamacpp"
- `OCR_ENGINE`: Choose between "tesseract" or "paddle"
- `OLLAMA_SUMMARY_MODEL`: Model for summary generation
- `OLLAMA_ANALYZER_MODEL`: Model for analysis and validation

## Usage

1. Upload a medical PDF document using the web interface
2. The system will automatically:
   - Extract text from the document
   - Analyze the medical content
   - Generate a summary of key findings
   - Validate the diagnosis and treatment plan
3. View the results in the tabbed interface

## Development

### Project Structure

```
medical-document-analyzer/
├── run.py                  # Main entry point
├── setup.py                # Package setup
├── requirements.txt        # Dependencies
├── Dockerfile              # Docker configuration
├── docker-compose.yml      # Docker Compose setup
├── medical_analyzer/       # Main package
│   ├── app.py              # FastAPI application
│   ├── api/                # API endpoints
│   ├── core/               # Core processing logic
│   ├── services/           # Service implementations
│   ├── templates/          # HTML templates
│   └── static/             # Static assets
```

### Running Tests

```bash
pip install -e ".[dev]"  # Install development dependencies
pytest
```

### Local Development

```bash
python run.py --reload --check  # Start with auto-reload and dependency check
```

## License

MIT License

## Acknowledgements

- This project uses open-source models from Microsoft (Phi-3) and Meta (Llama 3)
- Built with LangGraph for workflow orchestration
- OCR capabilities provided by Tesseract and PaddleOCR