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
from convert_from_qjson import (
    read_qjson_file,
    convert_to_json,
    save_json_file
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
        
        # Paths for converted QJson back to JSON
        self.json_reconverted = self.temp_path / "reconverted.json"
        
        # Create a QJson file for testing conversion back to standard formats
        qjson = QJson(quantum_bits=6, compression_level=0.6)
        encoded_data = qjson.encode(self.json_data)
        qjson_str = qjson.to_json()
        
        self.test_qjson_file = self.temp_path / "test_direct.qjson"
        with open(self.test_qjson_file, 'w') as f:
            f.write(qjson_str)
    
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


    def test_qjson_to_json_conversion(self):
        """Test converting from QJson back to standard JSON format"""
        # Read the QJson file
        qjson_result = read_qjson_file(self.test_qjson_file)
        qjson_obj = qjson_result["qjson_obj"]
        qjson_data = qjson_result["qjson_data"]
        
        # Convert to standard JSON
        json_data = convert_to_json(qjson_obj, qjson_data)
        
        # Verify conversion preserved all keys
        self.assertEqual(set(self.json_data.keys()), set(json_data.keys()))
        
        # Check specific values
        self.assertEqual(json_data["id"], self.json_data["id"])
        
        # Check arrays (numeric arrays may have slight differences due to compression)
        self.assertEqual(len(json_data["values"]), len(self.json_data["values"]))
        for i in range(len(self.json_data["values"])):
            self.assertAlmostEqual(json_data["values"][i], self.json_data["values"][i], delta=0.1)
        
        # Check nested structure
        self.assertIn("nested", json_data)
        self.assertIn("data", json_data["nested"])
        self.assertEqual(len(json_data["nested"]["data"]), len(self.json_data["nested"]["data"]))
        
        # Save the converted JSON to a file
        save_json_file(json_data, self.json_reconverted)
        self.assertTrue(os.path.exists(self.json_reconverted))
        
        # Verify saved file content
        with open(self.json_reconverted, 'r') as f:
            loaded_json = json.load(f)
        
        self.assertEqual(loaded_json["id"], self.json_data["id"])
    
    def test_round_trip_conversion(self):
        """Test complete round-trip: JSON → QJson → JSON"""
        # Step 1: JSON → QJson
        qjson_str = convert_to_qjson(
            self.json_data,
            quantum_bits=4,
            compression_level=0.7
        )
        
        # Save to file
        qjson_file = self.temp_path / "roundtrip.qjson"
        save_qjson_file(qjson_str, qjson_file)
        
        # Step 2: QJson → JSON
        qjson_result = read_qjson_file(qjson_file)
        qjson_obj = qjson_result["qjson_obj"]
        qjson_data = qjson_result["qjson_data"]
        
        json_data = convert_to_json(qjson_obj, qjson_data)
        
        # Save reconverted data
        reconverted_file = self.temp_path / "roundtrip.json"
        save_json_file(json_data, reconverted_file)
        
        # Verify round-trip preserved the data
        self.assertEqual(set(self.json_data.keys()), set(json_data.keys()))
        self.assertEqual(json_data["id"], self.json_data["id"])
        
        # Nested structures should be preserved
        self.assertIn("nested", json_data)
        self.assertIn("data", json_data["nested"])


if __name__ == "__main__":
    unittest.main()