#!/usr/bin/env python3
"""
Command-line interface for the Blood Pressure Tracker
"""

import argparse
import sys
from bp_tracker import BPTracker, format_reading


def main():
    """Main entry point for the CLI"""
    parser = argparse.ArgumentParser(
        description="Blood Pressure Tracker - Track your blood pressure readings",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s add 120 80                    Add a reading with 120/80
  %(prog)s add 120 80 --pulse 72         Add a reading with pulse
  %(prog)s add 120 80 --notes "Morning"  Add a reading with notes
  %(prog)s list                          List all readings
  %(prog)s list --limit 5                List last 5 readings
  %(prog)s delete 1                      Delete reading with ID 1
  %(prog)s stats                         Show statistics
        """
    )
    
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    # Add command
    add_parser = subparsers.add_parser("add", help="Add a new blood pressure reading")
    add_parser.add_argument("systolic", type=int, help="Systolic pressure (top number)")
    add_parser.add_argument("diastolic", type=int, help="Diastolic pressure (bottom number)")
    add_parser.add_argument("--pulse", "-p", type=int, help="Pulse rate in bpm")
    add_parser.add_argument("--notes", "-n", type=str, help="Notes about the reading")
    
    # List command
    list_parser = subparsers.add_parser("list", help="List blood pressure readings")
    list_parser.add_argument("--limit", "-l", type=int, help="Limit number of readings to show")
    
    # Delete command
    delete_parser = subparsers.add_parser("delete", help="Delete a reading by ID")
    delete_parser.add_argument("id", type=int, help="ID of the reading to delete")
    
    # Stats command
    subparsers.add_parser("stats", help="Show statistics")
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return 1
    
    tracker = BPTracker()
    
    try:
        if args.command == "add":
            reading = tracker.add_reading(
                systolic=args.systolic,
                diastolic=args.diastolic,
                pulse=args.pulse,
                notes=args.notes
            )
            print(f"✓ Added reading: {format_reading(reading)}")
            return 0
        
        elif args.command == "list":
            readings = tracker.get_readings(limit=args.limit)
            if not readings:
                print("No readings found. Add your first reading with 'bp_cli.py add <systolic> <diastolic>'")
                return 0
            
            print(f"\nBlood Pressure Readings ({len(readings)} total):")
            print("-" * 80)
            for reading in readings:
                print(format_reading(reading))
            return 0
        
        elif args.command == "delete":
            if tracker.delete_reading(args.id):
                print(f"✓ Deleted reading with ID {args.id}")
                return 0
            else:
                print(f"✗ Reading with ID {args.id} not found")
                return 1
        
        elif args.command == "stats":
            stats = tracker.get_statistics()
            if stats["count"] == 0:
                print("No readings found. Add your first reading with 'bp_cli.py add <systolic> <diastolic>'")
                return 0
            
            print("\nBlood Pressure Statistics:")
            print("-" * 40)
            print(f"Total readings: {stats['count']}")
            print(f"\nSystolic (top number):")
            print(f"  Average: {stats['avg_systolic']} mmHg")
            print(f"  Range: {stats['min_systolic']} - {stats['max_systolic']} mmHg")
            print(f"\nDiastolic (bottom number):")
            print(f"  Average: {stats['avg_diastolic']} mmHg")
            print(f"  Range: {stats['min_diastolic']} - {stats['max_diastolic']} mmHg")
            return 0
    
    except ValueError as e:
        print(f"✗ Error: {e}")
        return 1
    except Exception as e:
        print(f"✗ Unexpected error: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
