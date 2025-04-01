"""
Example usage of QJson hybrid data format
Demonstrates advanced features including quantum circuit representation,
compression algorithms, error correction, and quantum-safe cryptography.
"""

import json
import numpy as np
from qjson import QJson

def main():
    # Create sample data
    sample_data = {
        "device_id": "quantum_device_1",
        "timestamps": [1617293571, 1617293572, 1617293573, 1617293574, 1617293575],
        "quantum_states": [0.707, 0.707, 0, 0],
        "measurements": [0, 1, 1, 0, 1, 0, 0, 1],
        "classical_parameters": {
            "gate_time": 25e-9,
            "readout_fidelity": 0.98,
            "temperature": 0.015
        },
        "calibration_matrix": [
            [0.98, 0.02, 0.01, 0.01],
            [0.01, 0.97, 0.01, 0.01],
            [0.01, 0.01, 0.96, 0.01],
            [0.01, 0.01, 0.01, 0.95]
        ]
    }
    
    # Generate some large data to demonstrate compression
    large_data = list(np.random.rand(1000))
    sample_data["large_array"] = large_data
    
    print("========== BASIC USAGE ==========")
    # Create a QJson object with 4 qubits and moderate compression using gzip
    qjson = QJson(quantum_bits=4, compression_level=0.6, compression_algorithm="gzip", quantum_safe_crypto=True)
    
    # Encode the data to hybrid format
    hybrid_data = qjson.encode(sample_data)
    print("Encoded hybrid data (metadata):")
    print(json.dumps(hybrid_data["metadata"], indent=2))
    
    # Convert to JSON string for storage or transmission
    json_str = qjson.to_json()
    print(f"\nJSON string length: {len(json_str)} bytes")
    
    # Load from JSON
    loaded_qjson = QJson.from_json(json_str)
    
    # Decode back to classical format
    decoded_data = loaded_qjson.decode(hybrid_data)
    print("\nDecoded data preview (first 5 entries of large_array):")
    print(f"large_array: {decoded_data['large_array'][:5]}...")
    
    print("\n========== COMPRESSION COMPARISON ==========")
    # Compare different compression algorithms
    algos = ["gzip", "zlib", "pca"]
    for algo in algos:
        algo_qjson = QJson(quantum_bits=4, compression_level=0.6, compression_algorithm=algo)
        algo_data = algo_qjson.encode(sample_data)
        algo_json = algo_qjson.to_json()
        print(f"{algo.upper()} compressed size: {len(algo_json)} bytes")
    
    print("\n========== QUANTUM CIRCUIT REPRESENTATION ==========")
    # Add a quantum circuit
    bell_circuit = {
        "circuit_type": "openqasm",
        "qubits": 2,
        "operations": [
            {"gate": "h", "target": 0},
            {"gate": "cx", "control": 0, "target": 1},
            {"gate": "measure", "target": [0, 1]}
        ]
    }
    qjson.add_quantum_circuit("bell_state", bell_circuit)
    
    # Get the circuit back
    retrieved_circuit = qjson.get_quantum_circuit("bell_state")
    print("Retrieved Bell state circuit:")
    print(json.dumps(retrieved_circuit, indent=2))
    
    print("\n========== ERROR CORRECTION SUPPORT ==========")
    # Create a QJson object with error correction enabled
    ec_qjson = QJson(quantum_bits=8, error_correction=True)
    # Add error correction data
    error_data = {
        "syndrome_measurements": [0, 1, 0, 0, 1],
        "logical_encoding": {"type": "surface_code", "distance": 3},
        "correction_code": "surface"
    }
    try:
        ec_qjson.add_error_correction_data(error_data)
        print("Error correction data added successfully:")
        print(json.dumps(ec_qjson.data.get("error_correction", {}), indent=2))
    except ValueError as e:
        print(f"Error: {e}")
    
    print("\n========== ADAPTIVE PARAMETERS ==========")
    # Demonstrate adaptive parameter update
    for i in range(5):
        # Simulate performance metric (improving)
        performance = 0.5 + i * 0.1
        new_gain = qjson.adaptive_parameters.update_parameters(performance)
        print(f"Iteration {i+1}: Performance={performance:.2f}, Feedback Gain={new_gain:.4f}")
    
    print("\n========== RECORDED MEASUREMENTS ==========")
    # Access recorded measurements
    measurements = qjson.measurement_recorder.get_measurements()
    for m in measurements:
        print(f"Qubit {m['qubit']}: {m['result']:.4f} at time {m['time']:.6f}")

if __name__ == "__main__":
    main()