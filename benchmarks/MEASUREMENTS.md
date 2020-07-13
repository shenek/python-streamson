# Task
We have a huge json file in format:
```
{
	"users": [
		{"name": "user1", "id"},
		...
	],
	"groups": [
		{"name": "group1", ...}
		...
	]
}
```
And we want to extract names of groups and users.

## Libraries

### stdlib (3.8.3)
Uses standard python json module from stdlib.
It parses entire file and creates a huge python dict.

### hyperjson (0.2.4)
Uses Rust's serde and matches the API of standard python json module.

### streamson (2.0.0)
Uses python bindings for streamson (this project).
Works in a stream mode using 1MB input buffer.

### ijson-yajl2 (3.1.post0) + libyajl2 (2.1.0)
Wrapper around YAJL2 library using ctypes.
Works in a stream mode using 1MB input buffer.

### ijson-yajl2_c (3.1.post0)
Native ijson C extension using YAJL2 C library.
Works in a stream mode using 1MB input buffer.

### ijson-yajl2_cffi (3.1.post0) + libyajl2 (2.1.0)
Wrapper around YAJL2 library using cffi.
Works in a stream mode using 1MB input buffer.

### ijson-python (3.1.post0)
Python implementation of ijson API.
Works in a stream mode using 1MB input buffer.

## Results

### Memory Consumption
| Libraries        | 100 000 records | 500 000 records | 1 000 000 records|
|------------------|-----------------|-----------------|------------------|
| stdlib           | 47MB            | 196MB           | 383MB            |
| hyperjson        | 73MB            | 312MB           | 614MB            |
| streamson        | 14MB            | 16MB            | 16MB             |
| ijson-yajl2      | 39MB            | 39MB            | 39MB             |
| ijson-yajl2_c    | 34MB            | 34MB            | 34MB             |
| ijson-yajl2_cffi | 39MB            | 40MB            | 41MB             |
| ijson-python     | 42MB            | 48MB            | 56MB             |

### Time (in seconds)
| Libraries        | 100 000 records | 500 000 records | 1 000 000 records|
|------------------|-----------------|-----------------|------------------|
| stdlib           | 0.06957s        |  0.31471s       |  0.62557s        |
| hyperjson        | 0.10709s        |  0.49982s       |  0.98962s        |
| streamson        | 0.32700s        |  1.62874s       |  3.31072s        |
| ijson-yajl2      | 1.73574s        |  8.84899s       | 17.28310s        |
| ijson-yajl2_c    | 0.20588s        |  1.03259s       |  2.04052s        |
| ijson-yajl2_cffi | 1.63556s        |  8.06540s       | 15.89699s        |
| ijson-python     | 2.71555s        | 13.67734s       | 27.18603s        |
