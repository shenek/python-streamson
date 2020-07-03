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
### Select users
```python
>>> import streamson
>>> data = [b'{"users": ["john","carl","bob"], "groups": ["admins", "staff"], "org": "university"}']
>>> matcher = streamson.SimpleMatcher('{"users"}[]'])
>>> extracted = streamson.extract_iter((e for e in data), matcher)
>>> for path, parsed in extracted:
...     path, parsed
...
('{"users"}[0]', 'john')
('{"users"}[1]', 'carl')
('{"users"}[2]', 'bob')
```

### Select users and groups
```python
>>> import streamson
>>> data = [b'{"users": ["john","carl","bob"], "groups": ["admins", "staff"], "org": "university"}']
>>> matcher = streamson.SimpleMatcher('{"users"}[]']) | streamson.SimpleMatcher('{"groups"}[]'])
>>> extracted = streamson.extract_iter((e for e in data), matcher)
>>> for path, parsed in extracted:
...     path, parsed
...
('{"users"}[0]', 'john')
('{"users"}[1]', 'carl')
('{"users"}[2]', 'bob')
('{"groups"}[0]', 'admins')
('{"groups"}[1]', 'staff')
```

### Select only first level parts
```python
>>> import streamson
>>> data = [b'{"users": ["john","carl","bob"], "groups": ["admins", "staff"], "org": "university"}']
>>> matcher = streamson.DepthMatcher(1, 1)
>>> extracted = streamson.extract_iter((e for e in data), matcher)
>>> for path, parsed in extracted:
...     path, parsed
...
('{"users"}', ['john', 'carl', 'bob'])
('{"groups"}', ['admins', 'staff'])
('{"org"}', 'university')
```

### Select second first level parts exclude first records
```python
>>> import streamson
>>> data = [b'{"users": ["john","carl","bob"], "groups": ["admins", "staff"], "org": "university"}']
>>> matcher = streamson.DepthMatcher(2, 2) & ~streamson.SimpleMatcher('{}[0]')
>>> extracted = streamson.extract_iter((e for e in data), matcher)
>>> for path, parsed in extracted:
...     path, parsed
...
('{"users"}[1]', 'carl')
('{"users"}[2]', 'bob')
('{"groups"}[1]', 'staff')
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

This project also requires the nighly version of Rust.
First you need to [install rustup](https://rustup.rs/).
```bash
rustup install nightly
```

And you might need to set it as a default toolchain.
```bash
rustup default nightly
```

### Precommit deployment
To pass the basic lints you may want to install pre-push hook to
pre-commit to be sure that CI won't fail in the first step.
```bash
poetry run pre-commit install -t pre-push
```
