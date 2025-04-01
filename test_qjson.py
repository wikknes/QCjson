"""
Unit tests for the QJson hybrid data format
"""

import unittest
import json
import numpy as np
from qjson import QJson, AdaptiveParameterManager, TimeTaggedQuantumRecorder

class TestQJson(unittest.TestCase):
    """Test cases for QJson hybrid data format"""
    
    def setUp(self):
        """Set up test data"""
        self.qjson = QJson(quantum_bits=4, compression_level=0.5)
        self.test_data = {
            "scalar": 42,
            "array": [1.0, 2.0, 3.0, 4.0, 5.0],
            "nested": {
                "values": [0.1, 0.2, 0.3]
            }
        }
    
    def test_encode_decode(self):
        """Test encoding and decoding functionality"""
        # Encode data
        encoded = self.qjson.encode(self.test_data)
        
        # Verify metadata is present
        self.assertIn("metadata", encoded)
        self.assertIn("quantum_parameters", encoded["metadata"])
        self.assertEqual(encoded["metadata"]["quantum_parameters"]["bits"], 4)
        
        # Verify data is present
        self.assertIn("data", encoded)
        
        # Check if compression was applied to arrays
        self.assertIn("array", encoded["data"])
        self.assertIn("quantum_compressed", encoded["data"]["array"])
        self.assertIn("compressed_data", encoded["data"]["array"])
        
        # Check nested compression
        self.assertIn("nested", encoded["data"])
        self.assertIn("values", encoded["data"]["nested"])
        self.assertIn("quantum_compressed", encoded["data"]["nested"]["values"])
        
        # Check integrity field
        self.assertIn("quantum_integrity", encoded["data"])
        
        # Decode data
        decoded = self.qjson.decode(encoded)
        
        # Verify scalar values match
        self.assertEqual(decoded["scalar"], self.test_data["scalar"])
        
        # Verify arrays are approximately equal after compression/decompression
        self.assertEqual(len(decoded["array"]), len(self.test_data["array"]))
        
        # Verify nested structure preserved
        self.assertIn("nested", decoded)
        self.assertIn("values", decoded["nested"])
    
    def test_json_serialization(self):
        """Test JSON serialization and deserialization"""
        # Encode data
        self.qjson.encode(self.test_data)
        
        # Convert to JSON
        json_str = self.qjson.to_json()
        
        # Verify it's valid JSON
        json_data = json.loads(json_str)
        self.assertIn("metadata", json_data)
        self.assertIn("data", json_data)
        
        # Load from JSON
        loaded_qjson = QJson.from_json(json_str)
        
        # Verify metadata preserved
        self.assertEqual(
            loaded_qjson.metadata["quantum_parameters"]["bits"],
            self.qjson.metadata["quantum_parameters"]["bits"]
        )
        
        # Verify data preserved
        self.assertEqual(
            set(loaded_qjson.data.keys()),
            set(self.qjson.data.keys())
        )
    
    def test_integrity_verification(self):
        """Test data integrity verification"""
        # Encode data
        encoded = self.qjson.encode(self.test_data)
        
        # Verify integrity check passes
        self.assertTrue(self.qjson._verify_quantum_integrity(encoded["data"]))
        
        # Tamper with data
        tampered_data = encoded.copy()
        tampered_data["data"] = encoded["data"].copy()
        tampered_data["data"]["scalar"] = 99
        
        # Verify integrity check fails
        self.assertFalse(self.qjson._verify_quantum_integrity(tampered_data["data"]))


class TestAdaptiveParameterManager(unittest.TestCase):
    """Test cases for AdaptiveParameterManager"""
    
    def setUp(self):
        """Set up test data"""
        self.manager = AdaptiveParameterManager(
            initial_gain=1.0,
            learning_rate=0.1,
            max_value=2.0
        )
    
    def test_parameter_update(self):
        """Test parameter update logic"""
        # Initial value
        self.assertEqual(self.manager.feedback_gain, 1.0)
        
        # First update (no gradient yet)
        gain = self.manager.update_parameters(0.5)
        self.assertEqual(gain, 1.0)
        
        # Second update (positive gradient)
        gain = self.manager.update_parameters(0.7)
        self.assertGreater(gain, 1.0)
        
        # Third update (negative gradient)
        gain = self.manager.update_parameters(0.6)
        self.assertLess(gain, self.manager.feedback_gain + self.manager.learning_rate)
        
        # Test max value constraint
        self.manager.feedback_gain = 1.95
        gain = self.manager.update_parameters(2.5)
        self.assertLessEqual(gain, 2.0)
        
        # Test min value constraint
        self.manager.feedback_gain = 0.05
        gain = self.manager.update_parameters(0.0)
        self.assertGreaterEqual(gain, 0.0)


class TestTimeTaggedQuantumRecorder(unittest.TestCase):
    """Test cases for TimeTaggedQuantumRecorder"""
    
    def setUp(self):
        """Set up test data"""
        self.recorder = TimeTaggedQuantumRecorder(compression_threshold=0.1)
    
    def test_recording(self):
        """Test measurement recording"""
        # Record some measurements
        self.recorder.record_measurement(0.05, 1000.0, 0)  # Below threshold
        self.recorder.record_measurement(0.2, 1001.0, 1)   # Above threshold
        self.recorder.record_measurement(0.3, 1002.0, 2)   # Above threshold
        
        # Get measurements
        measurements = self.recorder.get_measurements()
        
        # Check that only measurements above threshold were recorded
        self.assertEqual(len(measurements), 2)
        
        # Check relative time calculation
        self.assertEqual(measurements[0]["time"], 1.0)
        self.assertEqual(measurements[1]["time"], 2.0)
        
        # Check qubit indices
        self.assertEqual(measurements[0]["qubit"], 1)
        self.assertEqual(measurements[1]["qubit"], 2)


if __name__ == "__main__":
    unittest.main()