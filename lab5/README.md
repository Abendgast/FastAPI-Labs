## Lab 5

### Run locally

```bash
cd lab5
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
gunicorn -w 2 -b 127.0.0.1:8000 app:app
```

Open:

- `http://127.0.0.1:8000/`
- `http://127.0.0.1:8000/apidocs/`

### Example requests

```bash
curl -s -X POST http://127.0.0.1:8000/authors -H 'Content-Type: application/json' -d '{"name":"John Doe"}'
```
