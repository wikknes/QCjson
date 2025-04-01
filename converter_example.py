#!/usr/bin/env python3
"""
Example demonstrating how to use the QJson converter programmatically.
This shows both JSON and CSV conversion to QJson format.
"""

import json
from convert_to_qjson import read_json_file, read_csv_file, convert_to_qjson
from qjson import QJson

def convert_json_example():
    """Example of converting a JSON file to QJson format"""
    print("\n=== Converting JSON file to QJson ===")
    
    # Read JSON data
    json_data = read_json_file("example_data.json")
    print(f"Original JSON data has {len(json_data)} keys")
    
    # Convert to QJson
    qjson_str = convert_to_qjson(
        json_data,
        quantum_bits=4,
        compression_level=0.6,
        compression_algorithm="gzip"
    )
    
    # Parse the QJson string for inspection
    qjson_data = json.loads(qjson_str)
    print(f"QJson metadata: {json.dumps(qjson_data['metadata'], indent=2)}")
    
    # Load QJson back into a QJson object and decode
    qjson_obj = QJson.from_json(qjson_str)
    decoded_data = qjson_obj.decode(qjson_data)
    
    # Verify data matches original
    print(f"Decoded data has {len(decoded_data)} keys")
    print(f"Keys preserved: {set(json_data.keys()) == set(decoded_data.keys())}")

def convert_csv_example():
    """Example of converting a CSV file to QJson format"""
    print("\n=== Converting CSV file to QJson ===")
    
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
    
    # Load QJson back into a QJson object and decode
    qjson_obj = QJson.from_json(qjson_str)
    decoded_data = qjson_obj.decode(qjson_data)
    
    # Verify data matches original
    print(f"Decoded data has {len(decoded_data)} columns")
    print(f"Keys preserved: {set(csv_data.keys()) == set(decoded_data.keys())}")
    
    if sample_column in decoded_data:
        sample_values = decoded_data[sample_column][:3]
        print(f"First few values from decoded data: {sample_values}")

if __name__ == "__main__":
    convert_json_example()
    convert_csv_example()
    print("\nConversion examples completed successfully.")