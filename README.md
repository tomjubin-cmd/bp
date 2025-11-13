# BP Tracker

A simple command-line tool for tracking blood pressure readings.

## Features

- Add blood pressure readings with systolic and diastolic values
- Record pulse rate and notes for each reading
- List all readings or limit to recent ones
- Delete readings by ID
- View statistics (average, min, max)
- Data persistence using JSON storage

## Installation

1. Clone the repository:
```bash
git clone https://github.com/tomjubin-cmd/bp.git
cd bp
```

2. Install dependencies (optional, only needed for testing):
```bash
pip install -r requirements.txt
```

## Usage

### Add a Reading

Add a basic blood pressure reading:
```bash
python bp_cli.py add 120 80
```

Add a reading with pulse rate:
```bash
python bp_cli.py add 120 80 --pulse 72
```

Add a reading with notes:
```bash
python bp_cli.py add 120 80 --notes "Morning reading"
```

Add a complete reading:
```bash
python bp_cli.py add 120 80 --pulse 72 --notes "After exercise"
```

### List Readings

List all readings:
```bash
python bp_cli.py list
```

List the last 5 readings:
```bash
python bp_cli.py list --limit 5
```

### View Statistics

Show statistics for all readings:
```bash
python bp_cli.py stats
```

### Delete a Reading

Delete a reading by its ID:
```bash
python bp_cli.py delete 1
```

## Data Storage

All readings are stored in a `bp_data.json` file in the current directory. This file is created automatically when you add your first reading.

## Development

### Running Tests

Run the test suite:
```bash
pytest test_bp_tracker.py -v
```

## Understanding Blood Pressure

Blood pressure is measured in mmHg (millimeters of mercury) and consists of two numbers:
- **Systolic** (top number): Pressure when your heart beats
- **Diastolic** (bottom number): Pressure when your heart rests between beats

Normal blood pressure is typically around 120/80 mmHg.

## License

This project is provided as-is for personal use.
