import json
import os
import time

TEST_LOG_PATH = os.path.join(os.path.dirname(__file__), 'test_log_runtime.jsonl')

log_entries = [
    {"event": "midway", "timestamp": 4},
    {"event": "finish", "timestamp": 5}
]

def main():
    print(f"Appending to {TEST_LOG_PATH}...")
    for entry in log_entries:
        with open(TEST_LOG_PATH, 'a') as f:
            f.write(json.dumps(entry) + '\n')
        print(f"Appended: {entry}")
        time.sleep(2)  # Wait 2 seconds between appends
    print("Done appending.")

if __name__ == "__main__":
    main() 