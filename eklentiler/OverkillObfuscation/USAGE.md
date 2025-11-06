# Pegasus Overkill Obfuscation Tools Usage Guide

## Overview

This guide explains how to use the Pegasus Overkill obfuscation tools that have been integrated into the Loki.RAT system. These tools provide code obfuscation capabilities to help evade detection by security software.

## Python Implementation

The obfuscation utilities have been ported to Python and integrated with the Loki.RAT system. The main components are:

1. **pegasus_obfuscation.py** - Python implementation of the obfuscation utilities
2. **API endpoints** - Web API for obfuscating files
3. **Web interface** - User-friendly web interface for the obfuscation tool

## Using the Python Module

### Direct Usage

You can use the obfuscation utilities directly in your Python code:

```python
from agent.pegasus_obfuscation import obfuscate_payload

# Obfuscate a payload file
success = obfuscate_payload("input_payload.exe", "obfuscated_payload.exe")

if success:
    print("Payload obfuscated successfully!")
else:
    print("Failed to obfuscate payload")
```

### Integration with Builder

The payload builder has been updated to support obfuscation:

```python
from agent.builder import build_agent

# Build and obfuscate an agent
build_agent(
    output="agent.exe",
    server_url="http://localhost:8080",
    platform="windows",
    hello_interval=5,
    idle_time=60,
    max_failed_connections=10,
    persist=True,
    obfuscate=True  # Enable obfuscation
)
```

## Web API

### Obfuscate File Endpoint

**Endpoint**: `POST /api/obfuscate`

**Description**: Obfuscate a file

**Parameters**:
- `file` (multipart/form-data): The file to obfuscate

**Response**:
- On success: The obfuscated file as an attachment
- On error: JSON with error message

**Example**:
```bash
curl -X POST -F "file=@payload.exe" http://localhost:8080/api/obfuscate -o obfuscated_payload.exe
```

## Web Interface

### Accessing the Tool

1. Start the Loki.RAT server
2. Navigate to `http://localhost:8080/tools/obfuscation` (or the appropriate URL)
3. Use the web interface to obfuscate payloads

### Using the Web Interface

1. Select a payload file to obfuscate
2. Choose obfuscation options:
   - Obfuscation level (Basic, Intermediate, Advanced)
   - Rename variables
   - Add junk code
3. Click "Obfuscate Payload"
4. Download the obfuscated payload when the process completes

## Command Line Usage

You can also use the obfuscation utilities from the command line:

```bash
# Using the Python module directly
python -c "from agent.pegasus_obfuscation import obfuscate_payload; obfuscate_payload('input.exe', 'output.exe')"
```

## C# Implementation

The original C# implementation is also available in the `eklentiler/OverkillObfuscation/Project` directory. You can build and use it independently:

```bash
cd eklentiler/OverkillObfuscation/Project
dotnet build
dotnet run input.exe obfuscated.exe
```

## Customization

You can customize the obfuscation process by modifying:

1. **Character set** in `Randomizer.CHARS` - Change the characters used for generating random names
2. **String length** in `MemberRenamer.string_length()` - Adjust the length of generated names
3. **Analysis rules** in the analyzer classes - Modify which members get renamed
4. **Obfuscation techniques** in `MemberRenamer.rename_python_code()` - Add more sophisticated obfuscation methods

## Integration with Build Process

The obfuscation tools can be integrated into the Loki.RAT build process to automatically obfuscate payloads during the build phase. This can help evade detection by security software.

To enable automatic obfuscation during the build process, use the `obfuscate=True` parameter when calling the build functions.

## Security Considerations

1. Only use these tools in accordance with applicable laws and regulations
2. Do not use these tools for malicious purposes
3. Be aware that obfuscation is not a guarantee of evasion from detection
4. Test payloads in isolated environments before deployment

## Troubleshooting

If you encounter issues:

1. Make sure all dependencies are installed
2. Check that the input file exists and is accessible
3. Verify that you have write permissions to the output location
4. Check the server logs for error messages