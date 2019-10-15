# urwerk-api-client

## Getting Started

### Prerequisites

Download and install Python version 3.

## Usage

Navigate to the projects root folder to import the API in python3.

Usage example:

```python
import urwerk_api_client.colorsensor as cs
import urwerk_api_client.spectral_imager as si

# [blickwerk-host-id] => numeric part of the sensor's host-name 
color_client = cs.ColorsensorAPI("http://[blickwerk-host-id].ddb/api")
spectral_client = si.SpectralImagerAPI("http://[blickwerk-host-id].ddb/api")

# to show available functions use:
# dir(color_client)
# or
# dir(spectral_client)

# request-example
version_string = color_client.get_firmware_version()
print(version_string)
```
