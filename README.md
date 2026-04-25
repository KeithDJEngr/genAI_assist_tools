# Setup
## Once
uv venv --python 3.12 --seed
source .venv/bin/activate
uv pip install fastapi uvicorn pydantic
uv pip install openai
uv pip install asyncio playwright markdownify beautifulsoup4 httpx && playwright install chromium
uv pip install docker

## Every time
source .venv/bin/activate
uvicorn connect_tools_to_llamacpp:app --reload --host XXX.XXX.XXX.XXX --port 8001
