#!/usr/bin/env python3
"""
QJson Format Converter

Converts JSON or CSV data to the QJson hybrid quantum-classical format.
This tool helps bridge classical data formats with quantum-ready structures.

Usage:
    python convert_to_qjson.py input_file.json --output output_file.qjson
    python convert_to_qjson.py input_file.csv --output output_file.qjson --delimiter ','
"""

import argparse
import csv
import json
import os
import sys
from typing import Dict, Any, List, Union

import numpy as np
from qjson import QJson


def read_json_file(file_path: str) -> Dict[str, Any]:
    """
    Read data from a JSON file
    
    Args:
        file_path: Path to the JSON file
        
    Returns:
        Dictionary containing the parsed JSON data
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except json.JSONDecodeError as e:
        print(f"Error parsing JSON file: {e}")
        sys.exit(1)
    except FileNotFoundError:
        print(f"File not found: {file_path}")
        sys.exit(1)


def read_csv_file(file_path: str, delimiter: str = ',') -> Dict[str, List]:
    """
    Read data from a CSV file and convert to dict format compatible with QJson
    
    Args:
        file_path: Path to the CSV file
        delimiter: CSV delimiter character
        
    Returns:
        Dictionary containing the parsed CSV data with columns as keys
    """
    try:
        data = {}
        with open(file_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f, delimiter=delimiter)
            # Convert CSV into columnar format
            for row in reader:
                for key, value in row.items():
                    if key not in data:
                        data[key] = []
                    # Try to convert numeric strings to numbers
                    try:
                        if '.' in value:
                            data[key].append(float(value))
                        else:
                            data[key].append(int(value))
                    except ValueError:
                        data[key].append(value)
        
        if not data:
            print(f"Warning: No data found in CSV file: {file_path}")
            
        return data
    except FileNotFoundError:
        print(f"File not found: {file_path}")
        sys.exit(1)


def convert_to_qjson(
    data: Dict[str, Any], 
    quantum_bits: int = 8, 
    compression_level: float = 0.5,
    compression_algorithm: str = "gzip",
    error_correction: bool = False,
    quantum_safe_crypto: bool = True
) -> str:
    """
    Convert dictionary data to QJson format
    
    Args:
        data: Dictionary containing data to convert
        quantum_bits: Number of qubits to use
        compression_level: Level of compression (0.0-1.0)
        compression_algorithm: Algorithm to use for compression
        error_correction: Enable quantum error correction
        quantum_safe_crypto: Use quantum-safe cryptography
        
    Returns:
        QJson format as a JSON string
    """
    qjson = QJson(
        quantum_bits=quantum_bits,
        compression_level=compression_level,
        compression_algorithm=compression_algorithm,
        error_correction=error_correction,
        quantum_safe_crypto=quantum_safe_crypto
    )
    
    # Encode the data to hybrid format
    qjson.encode(data)
    
    # Convert to JSON string
    return qjson.to_json()


def save_qjson_file(qjson_str: str, output_path: str) -> None:
    """
    Save QJson string to a file
    
    Args:
        qjson_str: QJson string to save
        output_path: Path where the file should be saved
    """
    try:
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(qjson_str)
        print(f"Successfully saved QJson to: {output_path}")
    except IOError as e:
        print(f"Error saving QJson file: {e}")
        sys.exit(1)


def main():
    # Parse command-line arguments
    parser = argparse.ArgumentParser(description='Convert JSON or CSV to QJson format')
    parser.add_argument('input_file', help='Input file path (JSON or CSV)')
    parser.add_argument('--output', help='Output file path', default=None)
    parser.add_argument('--qubits', type=int, default=8, help='Number of qubits (default: 8)')
    parser.add_argument('--compression', type=float, default=0.5, 
                        help='Compression level 0.0-1.0 (default: 0.5)')
    parser.add_argument('--algorithm', choices=['gzip', 'zlib', 'pca'], default='gzip',
                        help='Compression algorithm (default: gzip)')
    parser.add_argument('--error-correction', action='store_true', 
                        help='Enable quantum error correction')
    parser.add_argument('--quantum-safe', action='store_true', default=True,
                        help='Use quantum-safe cryptography')
    parser.add_argument('--delimiter', default=',', help='CSV delimiter (default: comma)')
    
    args = parser.parse_args()
    
    # Determine file type from extension
    file_extension = os.path.splitext(args.input_file)[1].lower()
    
    # Load data based on file type
    if file_extension == '.json':
        data = read_json_file(args.input_file)
    elif file_extension == '.csv':
        data = read_csv_file(args.input_file, args.delimiter)
    else:
        print(f"Unsupported file type: {file_extension}. Please use .json or .csv files.")
        sys.exit(1)
    
    # Convert to QJson
    qjson_str = convert_to_qjson(
        data,
        quantum_bits=args.qubits,
        compression_level=args.compression,
        compression_algorithm=args.algorithm,
        error_correction=args.error_correction,
        quantum_safe_crypto=args.quantum_safe
    )
    
    # Determine output file path
    if args.output:
        output_path = args.output
    else:
        base_name = os.path.splitext(args.input_file)[0]
        output_path = f"{base_name}.qjson"
    
    # Save QJson to file
    save_qjson_file(qjson_str, output_path)
    
    # Print summary
    print(f"Converted {args.input_file} to QJson format")
    print(f"QJson parameters:")
    print(f"  - Qubits: {args.qubits}")
    print(f"  - Compression level: {args.compression}")
    print(f"  - Algorithm: {args.algorithm}")
    print(f"  - Error correction: {'Enabled' if args.error_correction else 'Disabled'}")
    print(f"  - Quantum-safe crypto: {'Enabled' if args.quantum_safe else 'Disabled'}")


if __name__ == "__main__":
    main()