# urwerk-api-client

## Getting Started

### Prerequisites

Download and install Python version 3.

## Usage

Navigate to the projects root folder to import the API in python3.

Usage example:

```python
import urwerk_api_client.colorsensor as cs

# [blickwerk-host-id] => numeric part of the sensor's host-name 
api = cs.ColorsensorAPI("http://[blickwerk-host-id].ddb/api")

# to show available functions use:
# dir(api)

# request-example
version_string = api.get_firmware_version()
print(version_string)
```
