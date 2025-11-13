#!/usr/bin/env python3
"""
Unit tests for the Blood Pressure Tracker
"""

import json
import os
import pytest
from datetime import datetime
from bp_tracker import BPTracker, format_reading


@pytest.fixture
def temp_data_file(tmp_path):
    """Create a temporary data file for testing"""
    return str(tmp_path / "test_bp_data.json")


@pytest.fixture
def tracker(temp_data_file):
    """Create a BPTracker instance with temporary data file"""
    return BPTracker(data_file=temp_data_file)


class TestBPTracker:
    """Test suite for BPTracker class"""
    
    def test_init_creates_empty_tracker(self, tracker):
        """Test that a new tracker starts with no readings"""
        assert len(tracker.readings) == 0
    
    def test_add_reading_basic(self, tracker):
        """Test adding a basic reading with systolic and diastolic"""
        reading = tracker.add_reading(120, 80)
        assert reading["systolic"] == 120
        assert reading["diastolic"] == 80
        assert reading["id"] == 1
        assert "timestamp" in reading
        assert len(tracker.readings) == 1
    
    def test_add_reading_with_pulse(self, tracker):
        """Test adding a reading with pulse"""
        reading = tracker.add_reading(120, 80, pulse=72)
        assert reading["pulse"] == 72
    
    def test_add_reading_with_notes(self, tracker):
        """Test adding a reading with notes"""
        reading = tracker.add_reading(120, 80, notes="Morning reading")
        assert reading["notes"] == "Morning reading"
    
    def test_add_reading_increments_id(self, tracker):
        """Test that IDs increment correctly"""
        reading1 = tracker.add_reading(120, 80)
        reading2 = tracker.add_reading(125, 85)
        assert reading1["id"] == 1
        assert reading2["id"] == 2
    
    def test_add_reading_invalid_systolic_low(self, tracker):
        """Test that invalid systolic values raise ValueError"""
        with pytest.raises(ValueError, match="Systolic pressure"):
            tracker.add_reading(0, 80)
    
    def test_add_reading_invalid_systolic_high(self, tracker):
        """Test that invalid systolic values raise ValueError"""
        with pytest.raises(ValueError, match="Systolic pressure"):
            tracker.add_reading(301, 80)
    
    def test_add_reading_invalid_diastolic_low(self, tracker):
        """Test that invalid diastolic values raise ValueError"""
        with pytest.raises(ValueError, match="Diastolic pressure"):
            tracker.add_reading(120, 0)
    
    def test_add_reading_invalid_diastolic_high(self, tracker):
        """Test that invalid diastolic values raise ValueError"""
        with pytest.raises(ValueError, match="Diastolic pressure"):
            tracker.add_reading(120, 201)
    
    def test_add_reading_invalid_pulse_low(self, tracker):
        """Test that invalid pulse values raise ValueError"""
        with pytest.raises(ValueError, match="Pulse"):
            tracker.add_reading(120, 80, pulse=0)
    
    def test_add_reading_invalid_pulse_high(self, tracker):
        """Test that invalid pulse values raise ValueError"""
        with pytest.raises(ValueError, match="Pulse"):
            tracker.add_reading(120, 80, pulse=301)
    
    def test_get_readings_empty(self, tracker):
        """Test getting readings when none exist"""
        readings = tracker.get_readings()
        assert readings == []
    
    def test_get_readings_returns_all(self, tracker):
        """Test that get_readings returns all readings"""
        tracker.add_reading(120, 80)
        tracker.add_reading(125, 85)
        tracker.add_reading(118, 78)
        readings = tracker.get_readings()
        assert len(readings) == 3
    
    def test_get_readings_sorted_by_timestamp(self, tracker):
        """Test that readings are sorted by timestamp (newest first)"""
        reading1 = tracker.add_reading(120, 80, timestamp="2024-01-01T10:00:00")
        reading2 = tracker.add_reading(125, 85, timestamp="2024-01-02T10:00:00")
        reading3 = tracker.add_reading(118, 78, timestamp="2024-01-03T10:00:00")
        
        readings = tracker.get_readings()
        assert readings[0]["id"] == reading3["id"]
        assert readings[1]["id"] == reading2["id"]
        assert readings[2]["id"] == reading1["id"]
    
    def test_get_readings_with_limit(self, tracker):
        """Test that get_readings respects the limit parameter"""
        tracker.add_reading(120, 80, timestamp="2024-01-01T10:00:00")
        tracker.add_reading(125, 85, timestamp="2024-01-02T10:00:00")
        tracker.add_reading(118, 78, timestamp="2024-01-03T10:00:00")
        
        readings = tracker.get_readings(limit=2)
        assert len(readings) == 2
    
    def test_delete_reading_existing(self, tracker):
        """Test deleting an existing reading"""
        reading = tracker.add_reading(120, 80)
        assert tracker.delete_reading(reading["id"]) is True
        assert len(tracker.readings) == 0
    
    def test_delete_reading_nonexistent(self, tracker):
        """Test deleting a non-existent reading"""
        assert tracker.delete_reading(999) is False
    
    def test_delete_reading_removes_from_list(self, tracker):
        """Test that delete actually removes the reading"""
        reading1 = tracker.add_reading(120, 80)
        reading2 = tracker.add_reading(125, 85)
        
        tracker.delete_reading(reading1["id"])
        assert len(tracker.readings) == 1
        assert tracker.readings[0]["id"] == reading2["id"]
    
    def test_get_statistics_empty(self, tracker):
        """Test statistics with no readings"""
        stats = tracker.get_statistics()
        assert stats["count"] == 0
        assert stats["avg_systolic"] == 0
        assert stats["avg_diastolic"] == 0
    
    def test_get_statistics_single_reading(self, tracker):
        """Test statistics with a single reading"""
        tracker.add_reading(120, 80)
        stats = tracker.get_statistics()
        assert stats["count"] == 1
        assert stats["avg_systolic"] == 120
        assert stats["avg_diastolic"] == 80
        assert stats["min_systolic"] == 120
        assert stats["max_systolic"] == 120
        assert stats["min_diastolic"] == 80
        assert stats["max_diastolic"] == 80
    
    def test_get_statistics_multiple_readings(self, tracker):
        """Test statistics with multiple readings"""
        tracker.add_reading(120, 80)
        tracker.add_reading(130, 85)
        tracker.add_reading(110, 75)
        
        stats = tracker.get_statistics()
        assert stats["count"] == 3
        assert stats["avg_systolic"] == 120.0
        assert stats["avg_diastolic"] == 80.0
        assert stats["min_systolic"] == 110
        assert stats["max_systolic"] == 130
        assert stats["min_diastolic"] == 75
        assert stats["max_diastolic"] == 85
    
    def test_persistence_saves_data(self, tracker, temp_data_file):
        """Test that data is persisted to file"""
        tracker.add_reading(120, 80)
        assert os.path.exists(temp_data_file)
        
        with open(temp_data_file, 'r') as f:
            data = json.load(f)
        assert len(data) == 1
        assert data[0]["systolic"] == 120
    
    def test_persistence_loads_data(self, temp_data_file):
        """Test that data is loaded from file on initialization"""
        # Create a tracker and add data
        tracker1 = BPTracker(data_file=temp_data_file)
        tracker1.add_reading(120, 80)
        
        # Create a new tracker with the same file
        tracker2 = BPTracker(data_file=temp_data_file)
        assert len(tracker2.readings) == 1
        assert tracker2.readings[0]["systolic"] == 120
    
    def test_persistence_handles_corrupt_file(self, temp_data_file):
        """Test that corrupt JSON file is handled gracefully"""
        with open(temp_data_file, 'w') as f:
            f.write("not valid json")
        
        tracker = BPTracker(data_file=temp_data_file)
        assert len(tracker.readings) == 0


class TestFormatReading:
    """Test suite for format_reading function"""
    
    def test_format_basic_reading(self):
        """Test formatting a basic reading"""
        reading = {
            "id": 1,
            "systolic": 120,
            "diastolic": 80,
            "timestamp": "2024-01-01T10:30:00"
        }
        result = format_reading(reading)
        assert "ID: 1" in result
        assert "120/80 mmHg" in result
        assert "2024-01-01" in result
    
    def test_format_reading_with_pulse(self):
        """Test formatting a reading with pulse"""
        reading = {
            "id": 1,
            "systolic": 120,
            "diastolic": 80,
            "pulse": 72,
            "timestamp": "2024-01-01T10:30:00"
        }
        result = format_reading(reading)
        assert "Pulse: 72 bpm" in result
    
    def test_format_reading_with_notes(self):
        """Test formatting a reading with notes"""
        reading = {
            "id": 1,
            "systolic": 120,
            "diastolic": 80,
            "timestamp": "2024-01-01T10:30:00",
            "notes": "Morning reading"
        }
        result = format_reading(reading)
        assert "Notes: Morning reading" in result
