# Use Python 3.10 as the base image
FROM python:3.10

# Set working directory
WORKDIR /app

# Copy application files
COPY . /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Expose ports for FastAPI (8000) and Streamlit (8501)
EXPOSE 8000 8501

# Run FastAPI and Streamlit correctly
CMD ["sh", "-c", "uvicorn database.routes:app --host 0.0.0.0 --port 8000 & exec streamlit run streamlit_app.py --server.port 8501 --server.address 0.0.0.0"]
