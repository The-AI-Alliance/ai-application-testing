"""
Unit tests for the appointment management tool.
Following TDD (Test-Driven Development) approach.
"""

import unittest
import json
import tempfile
import os
from datetime import datetime, timedelta
from pathlib import Path

from apps.chatbot.appointment_manager import AppointmentManager, AppointmentError


class TestAppointmentManager(unittest.TestCase):
    """Test cases for AppointmentManager"""

    def _make_tool(self, file_name: str = '') -> AppointmentManager:
        if not file_name:
            file_name = self.temp_file.name
        self.tool = AppointmentManager(file_name)
        return self.tool

    def setUp(self):
        """Set up test fixtures"""
        # Create a temporary file for testing
        self.temp_file = tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.jsonl')
        self.temp_file.close()
        self._make_tool()

    def tearDown(self):
        """Clean up test fixtures"""
        if os.path.exists(self.temp_file.name):
            os.unlink(self.temp_file.name)

    def test_initialization_creates_file(self):
        """Test that initialization creates the appointments file if it doesn't exist"""
        self.assertTrue(os.path.exists(self.temp_file.name))

    def test_create_appointment_success(self):
        """Test creating a valid appointment"""
        # Monday at 10 AM, one week from now
        next_monday = datetime.now() + timedelta(days=(7 - datetime.now().weekday()))
        appointment_time = next_monday.replace(hour=10, minute=0, second=0, microsecond=0)
        
        result = self.tool.create_appointment(
            patient_name="John Doe",
            appointment_time=appointment_time,
            reason="Annual checkup"
        )
        
        self.assertTrue(result['success'])
        self.assertIn('appointment_id', result)
        self.assertEqual(result['patient_name'], "John Doe")

    def test_create_appointment_weekend_fails(self):
        """Test that creating an appointment on weekend fails"""
        # Next Saturday
        next_saturday = datetime.now() + timedelta(days=(5 - datetime.now().weekday()) % 7)
        appointment_time = next_saturday.replace(hour=10, minute=0, second=0, microsecond=0)
        
        with self.assertRaises(AppointmentError) as context:
            self.tool.create_appointment(
                patient_name="John Doe",
                appointment_time=appointment_time,
                reason="Checkup"
            )
        self.assertIn("weekday", str(context.exception).lower())

    def test_create_appointment_not_on_hour_fails(self):
        """Test that appointments must be on the hour"""
        next_monday = datetime.now() + timedelta(days=(7 - datetime.now().weekday()))
        appointment_time = next_monday.replace(hour=10, minute=30, second=0, microsecond=0)
        
        with self.assertRaises(AppointmentError) as context:
            self.tool.create_appointment(
                patient_name="John Doe",
                appointment_time=appointment_time,
                reason="Checkup"
            )
        self.assertIn("hour", str(context.exception).lower())

    def test_create_appointment_duplicate_time_fails(self):
        """Test that creating two appointments at the same time fails"""
        next_monday = datetime.now() + timedelta(days=(7 - datetime.now().weekday()))
        appointment_time = next_monday.replace(hour=10, minute=0, second=0, microsecond=0)
        
        # First appointment should succeed
        self.tool.create_appointment(
            patient_name="John Doe",
            appointment_time=appointment_time,
            reason="Checkup"
        )
        
        # Second appointment at same time should fail
        with self.assertRaises(AppointmentError) as context:
            self.tool.create_appointment(
                patient_name="Jane Smith",
                appointment_time=appointment_time,
                reason="Consultation"
            )
        self.assertIn("already booked", str(context.exception).lower())

    def test_cancel_appointment_success(self):
        """Test canceling an existing appointment"""
        next_monday = datetime.now() + timedelta(days=(7 - datetime.now().weekday()))
        appointment_time = next_monday.replace(hour=10, minute=0, second=0, microsecond=0)
        
        result = self.tool.create_appointment(
            patient_name="John Doe",
            appointment_time=appointment_time,
            reason="Checkup"
        )
        appointment_id = result['appointment_id']
        
        cancel_result = self.tool.cancel_appointment(appointment_id)
        self.assertTrue(cancel_result['success'])
        self.assertEqual(cancel_result['status'], 'cancelled')

    def test_cancel_nonexistent_appointment_fails(self):
        """Test that canceling a non-existent appointment fails"""
        with self.assertRaises(AppointmentError) as context:
            self.tool.cancel_appointment("nonexistent-id")
        self.assertIn("not found", str(context.exception).lower())

    def test_list_appointments(self):
        """Test listing all appointments"""
        next_monday = datetime.now() + timedelta(days=(7 - datetime.now().weekday()))
        
        # Create two appointments
        time1 = next_monday.replace(hour=10, minute=0, second=0, microsecond=0)
        time2 = next_monday.replace(hour=14, minute=0, second=0, microsecond=0)
        
        self.tool.create_appointment("John Doe", time1, "Checkup")
        self.tool.create_appointment("Jane Smith", time2, "Consultation")
        
        appointments = self.tool.list_appointments()
        self.assertEqual(len(appointments), 2)

    def test_confirm_appointment_success(self):
        """Test confirming an existing appointment"""
        next_monday = datetime.now() + timedelta(days=(7 - datetime.now().weekday()))
        appointment_time = next_monday.replace(hour=10, minute=0, second=0, microsecond=0)
        
        result = self.tool.create_appointment(
            patient_name="John Doe",
            appointment_time=appointment_time,
            reason="Checkup"
        )
        appointment_id = result['appointment_id']
        
        confirm_result = self.tool.confirm_appointment(appointment_id)
        self.assertTrue(confirm_result['success'])
        self.assertEqual(confirm_result['status'], 'confirmed')

    def test_change_appointment_success(self):
        """Test changing an appointment to a new time"""
        next_monday = datetime.now() + timedelta(days=(7 - datetime.now().weekday()))
        old_time = next_monday.replace(hour=10, minute=0, second=0, microsecond=0)
        new_time = next_monday.replace(hour=14, minute=0, second=0, microsecond=0)
        
        result = self.tool.create_appointment(
            patient_name="John Doe",
            appointment_time=old_time,
            reason="Checkup"
        )
        appointment_id = result['appointment_id']
        
        change_result = self.tool.change_appointment(appointment_id, new_time)
        self.assertTrue(change_result['success'])
        self.assertEqual(change_result['new_time'], new_time.isoformat())

    def test_persistence_across_instances(self):
        """Test that appointments persist across tool instances"""
        next_monday = datetime.now() + timedelta(days=(7 - datetime.now().weekday()))
        appointment_time = next_monday.replace(hour=10, minute=0, second=0, microsecond=0)
        
        # Create appointment with first instance
        result = self.tool.create_appointment(
            patient_name="John Doe",
            appointment_time=appointment_time,
            reason="Checkup"
        )
        appointment_id = result['appointment_id']
        
        # Create new instance and verify appointment exists
        new_tool = self._make_tool()
        appointments = new_tool.list_appointments()
        self.assertEqual(len(appointments), 1)
        self.assertEqual(appointments[0]['appointment_id'], appointment_id)


if __name__ == '__main__':
    unittest.main()

# Made with Bob
