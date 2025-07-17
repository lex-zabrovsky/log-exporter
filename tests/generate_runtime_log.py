import json
import os

TEST_LOG_PATH = os.path.join(os.path.dirname(__file__), 'test_log_runtime.jsonl')

log_entries = [
    {"event": "start", "timestamp": 1},
    {"event": "process", "timestamp": 2},
    {"event": "end", "timestamp": 3}
]

def main():
    with open(TEST_LOG_PATH, 'w') as f:
        for entry in log_entries:
            f.write(json.dumps(entry) + '\n')
    print(f"Initial runtime test log written to {TEST_LOG_PATH}")

if __name__ == "__main__":
    main() 