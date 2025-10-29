# imagelens


**imagelens** is a lightweight, async Python SDK for interacting with your ImageLens FastAPI service deployed on Cloud Run. It wraps common operations (upload/vectorize, face search, CLIP search, event images) into a user-friendly client.


## Features


- Async-first client (httpx)
- Helper utilities for retries and validation
- Example usage and a simple test
- CI workflow for packaging & tests


## Quickstart


```bash
pip install imagelens
# or install local editable for development
pip install -e .
