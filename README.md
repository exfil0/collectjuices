
# CollectJuices - The Ultimate URL and Secrets Extraction Tool

## Introduction

**CollectJuices** is a powerful tool designed to automate the process of fetching, analyzing, and recursively processing JavaScript files to discover URLs and secrets. Leveraging the capabilities of the JSluice tool and advanced Python libraries, CollectJuices is an essential tool for cybersecurity professionals.

## Prerequisites

Before using CollectJuices, ensure you have the following:

1. **Operating System**: Linux, macOS, or Windows (with minor adjustments).
2. **Python 3.x**: Required for running the script.
3. **JSluice Tool**: Required for analyzing JavaScript files.

## Installation

### Installing Python 3.x

1. **Linux**:
   ```bash
   sudo apt-get update
   sudo apt-get install python3 python3-pip
   ```
2. **macOS**:
   ```bash
   brew install python3
   ```
3. **Windows**: Download and install Python from the [official website](https://www.python.org/downloads/).

### Installing Python Packages

Install the necessary Python packages:
```bash
pip3 install aiohttp argparse
```

### Installing JSluice

1. Clone the JSluice repository:
   ```bash
   git clone https://github.com/exfil0/collectjuices.git
   ```
2. Navigate to the JSluice directory and follow the installation instructions provided in the repository.

## Usage Instructions

### Basic Usage

1. **Run the Script**:
   ```bash
   echo "https://example.com/script.js" | python3 CollectJuices.py
   ```
   This command processes the specified URL, runs CollectJuices, and outputs the results.

2. **Modes of Operation**:
   - To analyze URLs only:
     ```bash
     echo "https://example.com/script.js" | python3 CollectJuices.py -m endpoints
     ```
   - To analyze secrets only:
     ```bash
     echo "https://example.com/script.js" | python3 CollectJuices.py -m secrets
     ```
   - To analyze both URLs and secrets (default):
     ```bash
     echo "https://example.com/script.js" | python3 CollectJuices.py -m both
     ```

3. **Verbose Mode**:
   Enable verbose output for detailed processing information:
   ```bash
   echo "https://example.com/script.js" | python3 CollectJuices.py -v
   ```

### Processing Multiple URLs

1. **Using a File**:
   You can process multiple URLs by providing a file containing the URLs:

   ```bash
   cat urls.txt | python3 CollectJuices.py
   ```

2. **Manual Input**:
   You can manually input URLs by echoing them into the script:

   ```bash
   echo -e "https://example.com/script1.js https://example.com/script2.js" | python3 CollectJuices.py
   ```

## Output Interpretation

1. **URLs**:
   - The script outputs a sorted list of discovered URLs when run in `endpoints` or `both` mode.

2. **Secrets**:
   - The script outputs discovered secrets when run in `secrets` or `both` mode. Secrets are sorted by severity and uniqueness.

## Legal and Ethical Considerations

Using this script responsibly is critical. Unauthorized access or interception of data may violate legal regulations. Always obtain proper authorization before conducting any form of scanning or data analysis on external systems.

## Conclusion

This manual provides a comprehensive guide for installing, configuring, and using the CollectJuices script. By following these instructions, you can efficiently analyze JavaScript files for URLs and secrets, making this tool a valuable asset in your cybersecurity toolkit.

For further assistance or advanced configurations, refer to the documentation of each tool or seek help from the cybersecurity community.
