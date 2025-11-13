#!/usr/bin/env python3
"""
Blood Pressure Tracker - A simple CLI tool to track blood pressure readings
"""

import json
import os
from datetime import datetime
from typing import List, Dict, Optional


class BPTracker:
    """Blood Pressure Tracker for managing BP readings"""
    
    def __init__(self, data_file: str = "bp_data.json"):
        """
        Initialize the BP tracker
        
        Args:
            data_file: Path to the JSON file for storing readings
        """
        self.data_file = data_file
        self.readings = self._load_readings()
    
    def _load_readings(self) -> List[Dict]:
        """Load readings from JSON file"""
        if os.path.exists(self.data_file):
            try:
                with open(self.data_file, 'r') as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError):
                return []
        return []
    
    def _save_readings(self) -> None:
        """Save readings to JSON file"""
        with open(self.data_file, 'w') as f:
            json.dump(self.readings, f, indent=2)
    
    def add_reading(self, systolic: int, diastolic: int, pulse: Optional[int] = None, 
                   notes: Optional[str] = None, timestamp: Optional[str] = None) -> Dict:
        """
        Add a new blood pressure reading
        
        Args:
            systolic: Systolic pressure (top number)
            diastolic: Diastolic pressure (bottom number)
            pulse: Optional pulse rate
            notes: Optional notes about the reading
            timestamp: Optional timestamp (defaults to current time)
            
        Returns:
            The created reading
            
        Raises:
            ValueError: If systolic or diastolic values are invalid
        """
        if systolic <= 0 or systolic > 300:
            raise ValueError("Systolic pressure must be between 1 and 300")
        if diastolic <= 0 or diastolic > 200:
            raise ValueError("Diastolic pressure must be between 1 and 200")
        if pulse is not None and (pulse <= 0 or pulse > 300):
            raise ValueError("Pulse must be between 1 and 300")
        
        reading = {
            "id": len(self.readings) + 1,
            "systolic": systolic,
            "diastolic": diastolic,
            "timestamp": timestamp or datetime.now().isoformat()
        }
        
        if pulse is not None:
            reading["pulse"] = pulse
        if notes:
            reading["notes"] = notes
        
        self.readings.append(reading)
        self._save_readings()
        return reading
    
    def get_readings(self, limit: Optional[int] = None) -> List[Dict]:
        """
        Get all readings, optionally limited to the most recent ones
        
        Args:
            limit: Maximum number of readings to return (most recent first)
            
        Returns:
            List of readings
        """
        sorted_readings = sorted(self.readings, key=lambda x: x["timestamp"], reverse=True)
        if limit:
            return sorted_readings[:limit]
        return sorted_readings
    
    def delete_reading(self, reading_id: int) -> bool:
        """
        Delete a reading by ID
        
        Args:
            reading_id: The ID of the reading to delete
            
        Returns:
            True if deleted, False if not found
        """
        for i, reading in enumerate(self.readings):
            if reading["id"] == reading_id:
                self.readings.pop(i)
                self._save_readings()
                return True
        return False
    
    def get_statistics(self) -> Dict:
        """
        Calculate statistics from all readings
        
        Returns:
            Dictionary with statistics (average, min, max)
        """
        if not self.readings:
            return {
                "count": 0,
                "avg_systolic": 0,
                "avg_diastolic": 0,
                "min_systolic": 0,
                "max_systolic": 0,
                "min_diastolic": 0,
                "max_diastolic": 0
            }
        
        systolic_values = [r["systolic"] for r in self.readings]
        diastolic_values = [r["diastolic"] for r in self.readings]
        
        return {
            "count": len(self.readings),
            "avg_systolic": round(sum(systolic_values) / len(systolic_values), 1),
            "avg_diastolic": round(sum(diastolic_values) / len(diastolic_values), 1),
            "min_systolic": min(systolic_values),
            "max_systolic": max(systolic_values),
            "min_diastolic": min(diastolic_values),
            "max_diastolic": max(diastolic_values)
        }


def format_reading(reading: Dict) -> str:
    """Format a reading for display"""
    timestamp = datetime.fromisoformat(reading["timestamp"]).strftime("%Y-%m-%d %H:%M:%S")
    result = f"ID: {reading['id']} | {timestamp} | {reading['systolic']}/{reading['diastolic']} mmHg"
    
    if "pulse" in reading:
        result += f" | Pulse: {reading['pulse']} bpm"
    if "notes" in reading:
        result += f" | Notes: {reading['notes']}"
    
    return result
