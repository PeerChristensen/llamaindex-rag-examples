FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    software-properties-common \
    git \
    && rm -rf /var/lib/apt/lists/*

RUN git clone https://github.com/streamlit/streamlit-example.git .

COPY streamlit-app.py /app/
COPY requirements_docker.txt /app/
COPY .streamlit /app/.streamlit
COPY landsforsøg/chromadb /app/landsforsøg/chromadb
COPY style.css /app/

RUN pip3 install -r requirements_docker.txt

EXPOSE 8501

HEALTHCHECK CMD curl --fail http://localhost:8501/_stcore/health

ENTRYPOINT ["streamlit", "run", "streamlit-app.py", "--server.port=8501", "--server.address=0.0.0.0"]