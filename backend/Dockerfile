FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y build-essential && rm -rf /var/lib/apt/lists/*

RUN python - <<'PY'
open("requirements.txt","w").write("""\
fastapi==0.112.0
uvicorn[standard]==0.30.0
sqlmodel==0.0.22
psycopg[binary]==3.1.18
python-dotenv==1.0.1
""")
PY
RUN pip install --no-cache-dir -r requirements.txt

COPY app /app/app

CMD ["uvicorn", "app.main:app", "--host","0.0.0.0","--port","8000","--reload"]
