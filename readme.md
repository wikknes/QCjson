# QJson: Quantum-Classical Hybrid Data Format

QJson is a hybrid data format designed to bridge quantum and classical data processing, addressing key challenges in quantum information transmission, noise mitigation, and feedback control.

## Features

- **Quantum Circuit Representations**: Embed quantum circuits directly within QJson for seamless hybrid workflows
- **Advanced Classical Compression**: Multiple industry-standard compression algorithms (gzip, zlib, PCA)
- **Quantum Error Correction Support**: Fields for error syndrome measurements and logical qubit encodings
- **Integration with Quantum Programming Languages**: Compatible with frameworks like Qiskit/Cirq
- **Quantum-Safe Cryptography**: Post-quantum cryptographic algorithms for data security
- **Adaptive Parameter Management**: Updates parameters based on system performance
- **Time-Tagged Quantum Recording**: Captures quantum measurements with temporal context
- **Quantum Integrity Verification**: Provides data integrity through quantum checksums

## Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/qjson.git
cd qjson

# Install dependencies
pip install numpy
```

## Usage

### Basic Usage

```python
from qjson import QJson

# Create sample data
data = {
    "device_id": "quantum_device_1",
    "quantum_states": [0.707, 0.707, 0, 0],
    "measurements": [0, 1, 1, 0, 1, 0],
    "parameters": {"gate_time": 25e-9, "readout_fidelity": 0.98}
}

# Create a QJson object with 4 qubits, moderate compression using gzip
qjson = QJson(quantum_bits=4, compression_level=0.6, compression_algorithm="gzip")

# Encode the data to hybrid format
hybrid_data = qjson.encode(data)

# Convert to JSON string for storage or transmission
json_str = qjson.to_json()

# Later, load and decode
loaded_qjson = QJson.from_json(json_str)
decoded_data = loaded_qjson.decode(hybrid_data)
```

### Quantum Circuit Integration

```python
# Sample circuit data (this could be from Qiskit, OpenQASM, etc.)
circuit_data = {
    "circuit_type": "openqasm",
    "qubits": 2,
    "operations": [
        {"gate": "h", "target": 0},
        {"gate": "cx", "control": 0, "target": 1},
        {"gate": "measure", "target": [0, 1]}
    ]
}

# Add quantum circuit to QJson
qjson = QJson(quantum_bits=4, compression_level=0.5)
qjson.add_quantum_circuit("bell_state", circuit_data)

# Later, retrieve the circuit
bell_circuit = qjson.get_quantum_circuit("bell_state")
```

### Error Correction Support

```python
# Enable error correction in QJson
qjson = QJson(quantum_bits=8, compression_level=0.5, error_correction=True)

# Add error correction data
error_data = {
    "syndrome_measurements": [0, 1, 0, 0, 1],
    "logical_encoding": {"type": "surface_code", "distance": 3},
    "correction_code": "surface"
}
qjson.add_error_correction_data(error_data)
```

### Choosing Compression Algorithm

```python
# Using gzip (best for general purpose)
qjson_gzip = QJson(compression_algorithm="gzip")

# Using zlib (similar to gzip but with different performance characteristics)
qjson_zlib = QJson(compression_algorithm="zlib")

# Using PCA (best for numerical arrays where approximate values are acceptable)
qjson_pca = QJson(compression_algorithm="pca")
```

### Quantum-Safe Cryptography

```python
# Enable quantum-safe cryptography
qjson = QJson(quantum_safe_crypto=True)

# This will use simulated post-quantum cryptography for checksums
hybrid_data = qjson.encode(data)
```

### Adaptive Parameters

```python
qjson = QJson(quantum_bits=4, compression_level=0.5)

# Update parameters based on performance metrics
performance = 0.75
new_gain = qjson.adaptive_parameters.update_parameters(performance)
```

### Accessing Recorded Measurements

```python
measurements = qjson.measurement_recorder.get_measurements()
for m in measurements:
    print(f"Qubit {m['qubit']}: {m['result']} at time {m['time']}")
```

## Running the Example

To see QJson in action, run the included example:

```bash
python example.py
```

This demonstrates encoding/decoding, compression, adaptive parameters and more with sample quantum data.

## Data Format Structure

```json
{
  "metadata": {
    "id": "317639e7-4c54-468f-b7a0-0b59446f685d",
    "created": 1743440343.956497,
    "modified": 1743440343.956992,
    "schema_version": "1.1",
    "quantum_parameters": {
      "bits": 4,
      "compression": 0.6,
      "algorithm": "gzip",
      "error_correction": true,
      "quantum_safe_crypto": true
    }
  },
  "data": {
    "device_id": "quantum_device_1",
    "quantum_states": {
      "quantum_compressed": true,
      "algorithm": "gzip",
      "compressed_data": "H4sIAAAAAAAA/6pWykvMTVWyUoo2NjRSitZNrShJzUtRqgUAAAD//w==",
      "quantum_parameters": {
        "algorithm": "gzip",
        "original_size": 25,
        "compressed_size": 52
      },
      "compression_quality": 0.52
    },
    "quantum_circuits": {
      "bell_state": {
        "data": {
          "circuit_type": "openqasm",
          "qubits": 2,
          "operations": [
            {"gate": "h", "target": 0},
            {"gate": "cx", "control": 0, "target": 1},
            {"gate": "measure", "target": [0, 1]}
          ]
        },
        "added": 1743440343.956991
      }
    },
    "quantum_integrity": {
      "quantum_checksum": "71f920fa8b9534fad1800498e5af5b5da54b5fb3a2b2103e93e18d5b3d49dad2",
      "classical_checksum": "6684afd15337f...",
      "checksum_type": "post_quantum",
      "timestamp": 1743440343.956991
    }
  }
}
```

## Converting JSON and CSV Data to QJson

QJson provides a converter utility that can transform JSON or CSV files into the QJson format:

```bash
# Convert a JSON file to QJson format
python convert_to_qjson.py example_data.json --output output.qjson

# Convert a CSV file to QJson format
python convert_to_qjson.py example_data.csv --output output.qjson --delimiter ','
```

### Conversion Options

The converter supports several configuration options:

```
usage: convert_to_qjson.py [-h] [--output OUTPUT] [--qubits QUBITS]
                          [--compression COMPRESSION]
                          [--algorithm {gzip,zlib,pca}]
                          [--error-correction] [--quantum-safe]
                          [--delimiter DELIMITER]
                          input_file

positional arguments:
  input_file            Input file path (JSON or CSV)

optional arguments:
  -h, --help            show this help message and exit
  --output OUTPUT       Output file path
  --qubits QUBITS       Number of qubits (default: 8)
  --compression COMPRESSION
                        Compression level 0.0-1.0 (default: 0.5)
  --algorithm {gzip,zlib,pca}
                        Compression algorithm (default: gzip)
  --error-correction    Enable quantum error correction
  --quantum-safe        Use quantum-safe cryptography
  --delimiter DELIMITER
                        CSV delimiter (default: comma)
```

### CSV Conversion Notes

When converting CSV files:

1. The tool automatically attempts to convert numeric values to appropriate types (int or float)
2. The CSV data is structured in a columnar format, with each column name as a key in the resulting QJson object
3. All values in a column are stored as arrays, making them eligible for quantum-aware compression

## Running Tests

```bash
python -m unittest test_qjson.py
```

## License

MIT

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request