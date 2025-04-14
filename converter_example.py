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


def weather_data_example():
    """Example of converting weather data to and from QJson format"""
    print("\n=== Converting Weather Dataset to QJson and back ===")
    
    # Create sample weather data (non-quantum related)
    weather_data = {
        "metadata": {
            "dataset": "Daily Weather Records",
            "location": "San Francisco, CA",
            "time_period": "Jan-Dec 2023",
            "units": "metric"
        },
        "daily_records": [
            {
                "date": "2023-01-01",
                "temperature": 12.5,
                "humidity": 65,
                "pressure": 1015.2,
                "precipitation": 0.0,
                "wind_speed": 8.3,
                "wind_direction": "NE"
            },
            {
                "date": "2023-01-02",
                "temperature": 14.2,
                "humidity": 68,
                "pressure": 1012.8,
                "precipitation": 2.3,
                "wind_speed": 10.1,
                "wind_direction": "NW"
            },
            {
                "date": "2023-01-03",
                "temperature": 13.8,
                "humidity": 70,
                "pressure": 1011.5,
                "precipitation": 5.2,
                "wind_speed": 12.7,
                "wind_direction": "W"
            }
        ],
        "statistics": {
            "avg_temperature": 13.5,
            "max_temperature": 14.2,
            "min_temperature": 12.5,
            "total_precipitation": 7.5
        }
    }
    
    print(f"Original weather data has {len(weather_data)} main sections")
    print(f"Contains {len(weather_data['daily_records'])} daily records")
    
    # Create QJson object and encode the data
    qjson = QJson(quantum_bits=6, compression_level=0.7, compression_algorithm="zlib")
    encoded_weather = qjson.encode(weather_data)
    
    # Convert to a JSON string to show the QJson format
    qjson_str = json.dumps(encoded_weather)
    
    print(f"QJson encoded data size: {len(qjson_str)} bytes")
    print(f"Compression algorithm: {encoded_weather['metadata']['quantum_parameters']['algorithm']}")
    
    # Save the QJson data
    with open("weather_data.qjson", "w") as f:
        f.write(qjson_str)
    print("Saved QJson data to 'weather_data.qjson'")
    
    # Decode back to standard format
    decoded_weather = qjson.decode(encoded_weather)
    
    # Verify data is preserved
    print(f"Decoded data has {len(decoded_weather)} main sections")
    print(f"Contains {len(decoded_weather['daily_records'])} daily records")
    
    # Check if structure and values match
    print(f"First record temperature: Original={weather_data['daily_records'][0]['temperature']}, Decoded={decoded_weather['daily_records'][0]['temperature']}")
    print(f"Metadata preserved: {weather_data['metadata'] == decoded_weather['metadata']}")
    
    # Save the decoded data as standard JSON
    with open("weather_data_decoded.json", "w") as f:
        json.dump(decoded_weather, f, indent=2)
    print("Saved decoded data to 'weather_data_decoded.json'")


if __name__ == "__main__":
    import random
    import time
    
    convert_json_example()
    convert_csv_example()
    direct_qjson_to_json_example()
    weather_data_example()
    print("\nConversion examples completed successfully.")