"""
Unit tests for the QJson converter functionality
"""

import json
import os
import tempfile
import unittest
from pathlib import Path

import numpy as np
from qjson import QJson
from convert_to_qjson import (
    read_json_file,
    read_csv_file,
    convert_to_qjson,
    save_qjson_file
)

class TestConverter(unittest.TestCase):
    """Test cases for QJson converter functionality"""
    
    def setUp(self):
        """Set up test data"""
        # Create temporary files for testing
        self.temp_dir = tempfile.TemporaryDirectory()
        self.temp_path = Path(self.temp_dir.name)
        
        # Create test JSON data
        self.json_data = {
            "id": "test123",
            "values": [1, 2, 3, 4, 5],
            "nested": {
                "data": [0.1, 0.2, 0.3]
            }
        }
        self.json_file = self.temp_path / "test.json"
        with open(self.json_file, 'w') as f:
            json.dump(self.json_data, f)
            
        # Create test CSV data
        self.csv_file = self.temp_path / "test.csv"
        with open(self.csv_file, 'w') as f:
            f.write("id,value1,value2\n")
            f.write("1,10,0.1\n")
            f.write("2,20,0.2\n")
            f.write("3,30,0.3\n")
        
        # Output file paths
        self.json_output = self.temp_path / "test_json.qjson"
        self.csv_output = self.temp_path / "test_csv.qjson"
    
    def tearDown(self):
        """Clean up after tests"""
        self.temp_dir.cleanup()
        
    def test_read_json_file(self):
        """Test reading a JSON file"""
        data = read_json_file(self.json_file)
        self.assertEqual(data["id"], "test123")
        self.assertEqual(data["values"], [1, 2, 3, 4, 5])
        self.assertEqual(data["nested"]["data"], [0.1, 0.2, 0.3])
        
    def test_read_csv_file(self):
        """Test reading a CSV file"""
        data = read_csv_file(self.csv_file)
        
        # Check that columns were parsed correctly
        self.assertIn("id", data)
        self.assertIn("value1", data)
        self.assertIn("value2", data)
        
        # Check that data was converted to appropriate types
        self.assertEqual(data["id"], [1, 2, 3])
        self.assertEqual(data["value1"], [10, 20, 30])
        self.assertEqual(data["value2"], [0.1, 0.2, 0.3])
        
    def test_convert_json_to_qjson(self):
        """Test converting JSON data to QJson format"""
        qjson_str = convert_to_qjson(
            self.json_data,
            quantum_bits=4,
            compression_level=0.5,
            compression_algorithm="gzip"
        )
        
        # Verify the output is valid JSON
        qjson_data = json.loads(qjson_str)
        
        # Check that metadata exists and is correctly set
        self.assertIn("metadata", qjson_data)
        self.assertEqual(qjson_data["metadata"]["quantum_parameters"]["bits"], 4)
        self.assertEqual(qjson_data["metadata"]["quantum_parameters"]["algorithm"], "gzip")
        
        # Check that data exists
        self.assertIn("data", qjson_data)
        
        # Save the QJson and load it back
        save_qjson_file(qjson_str, self.json_output)
        self.assertTrue(os.path.exists(self.json_output))
        
        # Load the saved QJson
        with open(self.json_output, 'r') as f:
            loaded_qjson = json.load(f)
            
        # Deserialize into a QJson object and decode
        qjson_obj = QJson.from_json(qjson_str)
        decoded_data = qjson_obj.decode(loaded_qjson)
        
        # Verify the decoded data matches the original
        self.assertEqual(decoded_data["id"], self.json_data["id"])
        self.assertEqual(len(decoded_data["values"]), len(self.json_data["values"]))
        
    def test_convert_csv_to_qjson(self):
        """Test converting CSV data to QJson format"""
        # First read the CSV
        csv_data = read_csv_file(self.csv_file)
        
        # Convert to QJson
        qjson_str = convert_to_qjson(
            csv_data,
            quantum_bits=8,
            compression_level=0.5,
            compression_algorithm="pca"
        )
        
        # Verify the output is valid JSON
        qjson_data = json.loads(qjson_str)
        
        # Check that metadata exists and is correctly set
        self.assertIn("metadata", qjson_data)
        self.assertEqual(qjson_data["metadata"]["quantum_parameters"]["bits"], 8)
        self.assertEqual(qjson_data["metadata"]["quantum_parameters"]["algorithm"], "pca")
        
        # Check that data exists
        self.assertIn("data", qjson_data)
        
        # Save the QJson and load it back
        save_qjson_file(qjson_str, self.csv_output)
        self.assertTrue(os.path.exists(self.csv_output))
        
        # Load the saved QJson
        with open(self.csv_output, 'r') as f:
            loaded_qjson = json.load(f)
            
        # Deserialize into a QJson object and decode
        qjson_obj = QJson.from_json(qjson_str)
        decoded_data = qjson_obj.decode(loaded_qjson)
        
        # Verify the decoded data matches the original
        self.assertIn("id", decoded_data)
        self.assertIn("value1", decoded_data)
        self.assertIn("value2", decoded_data)
        
        # Check column data
        self.assertEqual(len(decoded_data["id"]), 3)
        # PCA compression might alter values slightly, so we check approximately
        self.assertAlmostEqual(decoded_data["value1"][0], 10, delta=1)
        self.assertAlmostEqual(decoded_data["value2"][0], 0.1, delta=0.05)


if __name__ == "__main__":
    unittest.main()