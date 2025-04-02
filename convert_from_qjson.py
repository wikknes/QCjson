#!/usr/bin/env python3
"""
QJson to JSON Converter

Converts QJson hybrid quantum-classical format back to standard JSON or CSV.
This tool helps bridge quantum-ready structures with classical data formats.

Usage:
    python convert_from_qjson.py input_file.qjson --output output_file.json
    python convert_from_qjson.py input_file.qjson --output output_file.csv --delimiter ','
"""

import argparse
import csv
import json
import os
import sys
from typing import Dict, Any, List, Union

import numpy as np
from qjson import QJson


def read_qjson_file(file_path: str) -> Dict[str, Any]:
    """
    Read data from a QJson file
    
    Args:
        file_path: Path to the QJson file
        
    Returns:
        Dictionary containing the parsed QJson data
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            json_string = f.read()
            
        # Parse the QJson string
        qjson_data = json.loads(json_string)
        
        # Create a QJson object from the file
        qjson_obj = QJson.from_json(json_string)
        
        return {
            "qjson_obj": qjson_obj,
            "qjson_data": qjson_data
        }
    except json.JSONDecodeError as e:
        print(f"Error parsing QJson file: {e}")
        sys.exit(1)
    except FileNotFoundError:
        print(f"File not found: {file_path}")
        sys.exit(1)


def convert_to_json(qjson_obj: QJson, qjson_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Convert QJson data to standard JSON format
    
    Args:
        qjson_obj: QJson object
        qjson_data: QJson data dictionary
        
    Returns:
        Dictionary containing standard JSON data
    """
    # Decode the data from hybrid format back to classical representation
    return qjson_obj.decode(qjson_data)


def save_json_file(data: Dict[str, Any], output_path: str) -> None:
    """
    Save JSON data to a file
    
    Args:
        data: JSON data to save
        output_path: Path where the file should be saved
    """
    try:
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2)
        print(f"Successfully saved JSON to: {output_path}")
    except IOError as e:
        print(f"Error saving JSON file: {e}")
        sys.exit(1)


def save_csv_file(data: Dict[str, Any], output_path: str, delimiter: str = ',') -> None:
    """
    Save data to a CSV file
    
    Args:
        data: Data to save in dictionary format
        output_path: Path where the file should be saved
        delimiter: CSV delimiter character
    """
    try:
        # Check if the data structure is compatible with CSV
        # CSV works best with flat data where each key has a list of values
        is_columnar = all(isinstance(v, list) for v in data.values())
        lengths = [len(v) for v in data.values() if isinstance(v, list)]
        is_equal_length = len(set(lengths)) <= 1 if lengths else True
        
        if not is_columnar or not is_equal_length:
            print("Warning: Data structure may not be ideal for CSV format.")
            print("Best results are achieved with flat data where each key has a list of equal-length values.")
        
        # Write to CSV
        with open(output_path, 'w', encoding='utf-8', newline='') as f:
            # Get fieldnames from keys
            fieldnames = list(data.keys())
            writer = csv.DictWriter(f, fieldnames=fieldnames, delimiter=delimiter)
            
            # Write header
            writer.writeheader()
            
            # Determine number of rows
            if lengths:
                num_rows = lengths[0]
            else:
                num_rows = 0
                
            # Write data rows
            for i in range(num_rows):
                row = {}
                for key in fieldnames:
                    if isinstance(data[key], list) and i < len(data[key]):
                        row[key] = data[key][i]
                    else:
                        row[key] = ""
                writer.writerow(row)
                
        print(f"Successfully saved CSV to: {output_path}")
    except IOError as e:
        print(f"Error saving CSV file: {e}")
        sys.exit(1)


def main():
    # Parse command-line arguments
    parser = argparse.ArgumentParser(description='Convert QJson format to JSON or CSV')
    parser.add_argument('input_file', help='Input QJson file path')
    parser.add_argument('--output', help='Output file path (JSON or CSV)', default=None)
    parser.add_argument('--format', choices=['json', 'csv'], help='Output format (default: derived from file extension)')
    parser.add_argument('--delimiter', default=',', help='CSV delimiter (default: comma)')
    
    args = parser.parse_args()
    
    # Load QJson data
    qjson_result = read_qjson_file(args.input_file)
    qjson_obj = qjson_result["qjson_obj"]
    qjson_data = qjson_result["qjson_data"]
    
    # Convert to standard JSON
    json_data = convert_to_json(qjson_obj, qjson_data)
    
    # Determine output file path and format
    if args.output:
        output_path = args.output
        if args.format:
            output_format = args.format
        else:
            # Determine format from file extension
            file_extension = os.path.splitext(args.output)[1].lower()
            if file_extension == '.json':
                output_format = 'json'
            elif file_extension == '.csv':
                output_format = 'csv'
            else:
                print(f"Unrecognized output format: {file_extension}. Using JSON format.")
                output_format = 'json'
    else:
        # Default: replace .qjson with .json
        base_name = os.path.splitext(args.input_file)[0]
        output_path = f"{base_name}.json"
        output_format = 'json'
    
    # Save data in the appropriate format
    if output_format == 'json':
        save_json_file(json_data, output_path)
    else:  # csv
        save_csv_file(json_data, output_path, args.delimiter)
    
    # Print summary
    print(f"Converted {args.input_file} to {output_format.upper()} format")
    print(f"Conversion parameters:")
    print(f"  - Output format: {output_format}")
    if output_format == 'csv':
        print(f"  - CSV delimiter: '{args.delimiter}'")


if __name__ == "__main__":
    main()