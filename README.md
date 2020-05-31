# Python streamson

Python bindings for streamson. A memory efficient json splitter.

## Installation
TODO

## Examples
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
