# Architecture

1. **Root Directory Files**:
   - `run.py`: Main startup script with CLI options
   - `setup.py`: Package setup with dependencies
   - `Dockerfile` & `docker-compose.yml`: Docker configuration
   - `.env.sample`: Sample environment variables

2. **Main Package**:
   - `medical_analyzer/__init__.py`: Package initialization
   - `medical_analyzer/app.py`: FastAPI application entry point

3. **API Module**:
   - `medical_analyzer/api/routes.py`: API endpoints and controllers
   - `medical_analyzer/api/schemas.py`: Pydantic schemas for data validation

4. **Core Module**:
   - `medical_analyzer/core/config.py`: Application configuration settings
   - `medical_analyzer/core/processor.py`: Document processing logic
   - `medical_analyzer/core/llm_chain.py`: LangGraph workflow implementation

5. **Services Module**:
   - `medical_analyzer/services/document.py`: Document handling
   - `medical_analyzer/services/llm.py`: LLM interfacing with Ollama/llama.cpp
   - `medical_analyzer/services/ocr.py`: OCR processing with Tesseract/PaddleOCR

6. **Templates**:
   - `medical_analyzer/templates/index.html`: Web interface

The system uses open-source components instead of proprietary APIs, making it completely self-contained and free to run.