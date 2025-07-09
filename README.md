# log-exporter

Application for exporting log data into OpenSearch.

## Setup Instructions

### 1. Clone the repository
```sh
git clone <repo-url>
cd log-exporter
```

### 2. Set up the Python environment

#### Unix
Run the provided setup script:
```sh
bash environment_setup.sh
```

#### Windows
Run the provided setup script in Command Prompt:
```bat
environment_setup.bat
```

Both scripts will:
- Check for Python and pip
- Create a virtual environment in `.venv` if it doesn't exist
- Activate the virtual environment
- Install dependencies from `requirements.txt`

### 3. Configure environment variables

The application uses environment variables for configuration. You can set them in your shell or create a `.env` file in the project root. The application will automatically load variables from `.env` if present.

#### Required environment variables:
- `OPENSEARCH_HOST`   - Hostname or IP address of your OpenSearch instance (e.g., `localhost`)
- `OPENSEARCH_PORT`   - Port for OpenSearch (default: `9200`)
- `OPENSEARCH_INDEX`  - Name of the OpenSearch index to use/create
- `BATCH_SIZE`        - (Optional) Number of log lines to batch before sending to OpenSearch (default: `100`)
- `LOG_FILE_PATH`     - Full path to the log file to be exported (e.g., `/path/to/your/logfile.log`)
- `LOG_LEVEL=INFO`    - (Optional) Log level `INFO` (default) Shows high-level progress and errors, log level `DEBUG` shows detailed connection info and full OpenSearch responses.

#### Example `.env` file:
```
OPENSEARCH_HOST=localhost
OPENSEARCH_PORT=9200
OPENSEARCH_INDEX=my-logs
BATCH_SIZE=100
LOG_FILE_PATH=/path/to/your/logfile.log
LOG_LEVEL=INFO
```

### 4. Run the exporter

After activating the virtual environment and setting environment variables, run:
```sh
python log_exporter.py
```

The script will:
- Connect to OpenSearch
- Create the index if it does not exist
- Read the log file line by line and send data in batches