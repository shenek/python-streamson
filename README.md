![Code Quality](https://github.com/shenek/python-streamson/workflows/Code%20Quality/badge.svg)
![Security audit](https://github.com/shenek/python-streamson/workflows/Security%20audit/badge.svg)

# Python streamson

Python bindings for streamson. A memory efficient json splitter written in Rust.
The project is still in an early phase, but it seems to be working

## Installation
```bash
pip install streamson
```

## Usage
### Simple
```python
>>> import streamson
>>> data = [b'{"users": ["john","carl","bob"]}']
>>> extracted = streamson.extract_iter((e for e in data), ['{"users"}[]'])
>>> for path, parsed in extracted:
...     path, parsed
...
('{"users"}[0]', 'john')
('{"users"}[1]', 'carl')
('{"users"}[2]', 'bob')
```

## Motivation
This project is meant to be use as a fast json splitter.
Its main purpose is to split raw binary data instead of parsing it.
It is supposed to be fast and memory efficient.

## Developer Docs

### Build
Poetry is used to manage python dev-dependencies. After you [install](https://python-poetry.org/docs/#installation) it you can run:
```bash
poetry install
```

### Precommit deployment
To pass the basic lints you may want to install pre-push hook to
pre-commit to be sure that CI won't fail in the first step.
```bash
poetry run pre-commit install -t pre-push
```
