#!/usr/bin/env python3
"""
Example demonstrating how to use the QJson converter programmatically.
This shows bidirectional conversion between JSON, CSV, and QJson formats.
"""

import json
from convert_to_qjson import read_json_file, read_csv_file, convert_to_qjson
from qjson import QJson

def convert_json_example():
    """Example of converting between JSON and QJson format"""
    print("\n=== Converting JSON to QJson and back ===")
    
    # Read JSON data
    json_data = read_json_file("example_data.json")
    print(f"Original JSON data has {len(json_data)} keys")
    
    # Convert to QJson (JSON → QJson)
    qjson_str = convert_to_qjson(
        json_data,
        quantum_bits=4,
        compression_level=0.6,
        compression_algorithm="gzip"
    )
    
    # Parse the QJson string for inspection
    qjson_data = json.loads(qjson_str)
    print(f"QJson metadata: {json.dumps(qjson_data['metadata'], indent=2)}")
    
    # Load QJson back into a QJson object and decode (QJson → JSON)
    qjson_obj = QJson.from_json(qjson_str)
    decoded_data = qjson_obj.decode(qjson_data)
    
    # Verify data matches original
    print(f"Decoded data has {len(decoded_data)} keys")
    print(f"Keys preserved: {set(json_data.keys()) == set(decoded_data.keys())}")
    
    # Save the standard JSON result
    with open("example_roundtrip.json", "w") as f:
        json.dump(decoded_data, f, indent=2)
    print("Saved round-trip converted data to 'example_roundtrip.json'")

def convert_csv_example():
    """Example of converting between CSV and QJson format"""
    print("\n=== Converting CSV to QJson and back ===")
    
    # Read CSV data
    csv_data = read_csv_file("example_data.csv")
    print(f"Original CSV data has {len(csv_data)} columns")
    
    # Show sample of data
    sample_column = next(iter(csv_data.keys()))
    print(f"Sample column '{sample_column}' has {len(csv_data[sample_column])} rows")
    print(f"First few values: {csv_data[sample_column][:3]}")
    
    # Convert to QJson with PCA compression (good for numerical data)
    qjson_str = convert_to_qjson(
        csv_data,
        quantum_bits=8,
        compression_level=0.7,
        compression_algorithm="pca"
    )
    
    # Parse the QJson string for inspection
    qjson_data = json.loads(qjson_str)
    print(f"Compression algorithm: {qjson_data['metadata']['quantum_parameters']['algorithm']}")
    
    # Check a specific column in the QJson data
    if "data" in qjson_data and sample_column in qjson_data["data"]:
        column_data = qjson_data["data"][sample_column]
        if "quantum_compressed" in column_data:
            print(f"Column '{sample_column}' was compressed using {column_data['algorithm']}")
            print(f"Compression quality: {column_data.get('compression_quality', 'N/A')}")
    
    # Save the QJson string to a file
    with open("example_data.qjson", "w") as f:
        f.write(qjson_str)
    print("Saved QJson data to 'example_data.qjson'")
    
    # Load QJson back into a QJson object and decode (QJson → CSV-like structure)
    qjson_obj = QJson.from_json(qjson_str)
    decoded_data = qjson_obj.decode(qjson_data)
    
    # Verify data matches original
    print(f"Decoded data has {len(decoded_data)} columns")
    print(f"Keys preserved: {set(csv_data.keys()) == set(decoded_data.keys())}")
    
    if sample_column in decoded_data:
        sample_values = decoded_data[sample_column][:3]
        print(f"First few values from decoded data: {sample_values}")
        
    # This could be saved back to a CSV file using a CSV writer
    print("The decoded data could be saved as CSV by using csv.writer")

def direct_qjson_to_json_example():
    """Example of directly converting QJson to standard JSON"""
    print("\n=== Direct QJson to JSON conversion ===")
    
    # Create a QJson object with some data
    qjson = QJson(quantum_bits=8, compression_level=0.6)
    
    # Sample data with numerical arrays that benefit from quantum compression
    test_data = {
        "experiment_name": "Quantum Simulation",
        "timestamp": time.time(),
        "measurements": [random.random() for _ in range(100)],  # Random measurements
        "parameters": {
            "temperature": 0.01,
            "iterations": 1000,
            "threshold": 0.5
        }
    }
    
    # Encode to QJson format
    encoded_data = qjson.encode(test_data)
    
    print(f"Encoded QJson data with {len(encoded_data['data'])} keys")
    
    # Convert directly back to standard JSON
    standard_json = qjson.decode(encoded_data)
    
    print(f"Converted back to standard JSON with {len(standard_json)} keys")
    print(f"Original data structure preserved: {set(test_data.keys()) == set(standard_json.keys())}")
    
    # Verify specific elements are preserved
    if "measurements" in standard_json:
        print(f"Measurements array length: {len(standard_json['measurements'])}")
        print(f"First few measurements: {standard_json['measurements'][:3]}")
    
    # This demonstrates that you can convert between formats without file I/O
    print("Direct conversion complete - no files were read or written in this example")


if __name__ == "__main__":
    import random
    import time
    
    convert_json_example()
    convert_csv_example()
    direct_qjson_to_json_example()
    print("\nConversion examples completed successfully.")