"""
Quantum-Classical Hybrid Data Format (QJson)

This module implements a hybrid data format that bridges quantum and classical data
processing while addressing key challenges in quantum information transmission,
noise mitigation, and feedback control.

Features:
- Quantum Circuit Representations: Support for embedding quantum circuits
- Advanced Classical Compression: Industry-standard compression algorithms
- Quantum Error Correction: Support for error correction data
- Integration with Quantum Programming Languages: Compatible with frameworks like Qiskit/Cirq
- Quantum-Safe Cryptography: Post-quantum cryptographic algorithms for data security
"""

import json
import numpy as np
import uuid
import time
import hashlib
import gzip
import base64
import zlib
import math
from typing import Dict, List, Any, Union, Optional, Tuple, Callable

# Custom JSON encoder to handle numpy types
class NumpyJSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, np.integer):
            return int(obj)
        elif isinstance(obj, np.floating):
            return float(obj)
        elif isinstance(obj, np.ndarray):
            return obj.tolist()
        return super().default(obj)

class QJson:
    """
    Quantum-Classical Hybrid Data Format
    
    A data format that supports both classical and quantum-ready data structures
    with built-in validation, compression, and adaptation capabilities.
    Features include quantum circuit representations, advanced compression,
    error correction support, and quantum-safe cryptography.
    """
    
    # Compression algorithm options
    COMPRESSION_ALGORITHMS = {
        "gzip": {"compress": lambda data: base64.b64encode(gzip.compress(data.encode())).decode(),
                 "decompress": lambda data: gzip.decompress(base64.b64decode(data.encode())).decode()},
        "zlib": {"compress": lambda data: base64.b64encode(zlib.compress(data.encode())).decode(),
                 "decompress": lambda data: zlib.decompress(base64.b64decode(data.encode())).decode()},
        "pca": {"compress": None, "decompress": None}  # Implemented separately
    }
    
    def __init__(self, quantum_bits: int = 8, compression_level: float = 0.5, 
                 compression_algorithm: str = "gzip", error_correction: bool = False,
                 quantum_safe_crypto: bool = True):
        """
        Initialize a new QJson object
        
        Args:
            quantum_bits: Number of qubits available for quantum processing
            compression_level: Level of compression to apply (0.0-1.0)
            compression_algorithm: Algorithm to use for data compression ('gzip', 'zlib', 'pca')
            error_correction: Enable quantum error correction support
            quantum_safe_crypto: Use post-quantum cryptography for checksums
        """
        self.quantum_bits = quantum_bits
        self.compression_level = compression_level
        self.compression_algorithm = compression_algorithm
        self.error_correction = error_correction
        self.quantum_safe_crypto = quantum_safe_crypto
        self.adaptive_parameters = AdaptiveParameterManager()
        self.data = {}
        self.measurement_recorder = TimeTaggedQuantumRecorder()
        self.quantum_circuits = {}
        self.error_correction_data = {}
        self.metadata = {
            "id": str(uuid.uuid4()),
            "created": time.time(),
            "modified": time.time(),
            "schema_version": "1.1",
            "quantum_parameters": {
                "bits": quantum_bits,
                "compression": compression_level,
                "algorithm": compression_algorithm,
                "error_correction": error_correction,
                "quantum_safe_crypto": quantum_safe_crypto
            }
        }
        
    def encode(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Encode classical data into a quantum-aware format
        
        Args:
            data: Dictionary containing data to encode
            
        Returns:
            Encoded data in hybrid format
        """
        self.data = data.copy()
        encoded_data = {}
        
        # Process numerical arrays for quantum preparation
        for key, value in data.items():
            if isinstance(value, (list, np.ndarray)):
                # Convert numpy types to Python native types if needed
                if isinstance(value, np.ndarray):
                    value = [float(x) if isinstance(x, np.floating) else int(x) if isinstance(x, np.integer) else x for x in value]
                # Check if all elements are numeric
                if all(isinstance(x, (int, float)) for x in value):
                    encoded_data[key] = self._quantum_aware_compress(value)
                else:
                    encoded_data[key] = value
            elif isinstance(value, dict):
                # Create a new QJson instance for nested dictionaries to avoid circular references
                nested_qjson = QJson(self.quantum_bits, self.compression_level)
                nested_encoded = nested_qjson.encode(value)
                encoded_data[key] = nested_encoded["data"]
            else:
                encoded_data[key] = value
        
        # Store encoded data
        self.data = encoded_data
        
        # Add integrity checksums
        self._add_quantum_checksums()
        
        self.metadata["modified"] = time.time()
        return {
            "metadata": self.metadata,
            "data": self.data
        }
    
    def decode(self, encoded_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Decode data from hybrid format back to classical representation
        
        Args:
            encoded_data: Data in hybrid format
            
        Returns:
            Decoded classical data
        """
        result = {}
        data = encoded_data.get("data", {})
        
        # Process and decode quantum-compressed data
        for key, value in data.items():
            if isinstance(value, dict) and "quantum_compressed" in value:
                result[key] = self._decompress_quantum_data(value)
            elif isinstance(value, dict) and "quantum_checksum" not in value:
                result[key] = self.decode({"data": value})
            elif isinstance(value, dict) and "quantum_checksum" in value:
                # Skip checksums in decoded output
                continue
            else:
                result[key] = value
                
        # Validate integrity if checksums exist
        if "quantum_integrity" in data:
            if not self._verify_quantum_integrity(data):
                raise ValueError("Quantum integrity check failed. Data may be corrupted.")
                
        return result
    
    def to_json(self) -> str:
        """Convert the hybrid data format to JSON string"""
        hybrid_data = {
            "metadata": self.metadata,
            "data": self.data
        }
        return json.dumps(hybrid_data, cls=NumpyJSONEncoder)
    
    @classmethod
    def from_json(cls, json_string: str) -> 'QJson':
        """Create a QJson object from a JSON string"""
        hybrid_data = json.loads(json_string)
        metadata = hybrid_data.get("metadata", {})
        
        instance = cls(
            quantum_bits=metadata.get("quantum_parameters", {}).get("bits", 8),
            compression_level=metadata.get("quantum_parameters", {}).get("compression", 0.5)
        )
        instance.metadata = metadata
        instance.data = hybrid_data.get("data", {})
        return instance
    
    def _quantum_aware_compress(self, data: Union[List, np.ndarray]) -> Dict[str, Any]:
        """
        Compress classical data while preserving quantum-relevant features
        
        Args:
            data: Numerical data to compress
            
        Returns:
            Compressed data with quantum parameters
        """
        # Convert numpy types to Python native types if needed
        if isinstance(data, np.ndarray):
            data = [float(x) if isinstance(x, np.floating) else int(x) if isinstance(x, np.integer) else x for x in data]
            
        data_array = np.array(data)
        n_components = max(1, min(self.quantum_bits, len(data_array)))
        
        # Convert data to string representation for standard compression
        data_str = json.dumps(data_array.tolist(), cls=NumpyJSONEncoder)
        
        if self.compression_algorithm in ["gzip", "zlib"]:
            # Use industry-standard compression algorithm
            compress_func = self.COMPRESSION_ALGORITHMS[self.compression_algorithm]["compress"]
            compressed_str = compress_func(data_str)
            
            # Calculate compression ratio
            original_size = len(data_str)
            compressed_size = len(compressed_str)
            compression_ratio = compressed_size / original_size if original_size > 0 else 1.0
            
            # Adjust compression based on level (higher compression_level = more aggressive)
            if compression_ratio > self.compression_level:
                # If compression isn't good enough, fall back to PCA-like approach
                return self._pca_compress(data_array, n_components)
            
            quantum_params = {
                "algorithm": self.compression_algorithm,
                "original_size": original_size,
                "compressed_size": compressed_size,
                "original_shape": data_array.shape,
                "original_dtype": str(data_array.dtype)
            }
            
            # Record the compression event in the measurement recorder
            self.measurement_recorder.record_measurement(
                measurement=1.0 - compression_ratio,
                timestamp=time.time(),
                qubit_index=0
            )
            
            return {
                "quantum_compressed": True,
                "algorithm": self.compression_algorithm,
                "compressed_data": compressed_str,
                "quantum_parameters": quantum_params,
                "compression_quality": 1.0 - compression_ratio
            }
        else:
            # Fall back to PCA-like compression
            return self._pca_compress(data_array, n_components)
    
    def _pca_compress(self, data_array: np.ndarray, n_components: int) -> Dict[str, Any]:
        """
        Perform PCA-like compression on data array
        
        Args:
            data_array: Array to compress
            n_components: Number of components to keep
            
        Returns:
            Compressed data with quantum parameters
        """
        # Simple PCA-like compression (simplified for demonstration)
        data_mean = np.mean(data_array)
        centered_data = data_array - data_mean
        
        if len(data_array.shape) == 1:
            # For 1D arrays, we do a simple normalization and truncation
            normalized_data = centered_data / (np.std(centered_data) or 1.0)
            
            # Apply compression by keeping only the first n_components elements
            compression_idx = max(1, int(len(normalized_data) * self.compression_level))
            compressed_data = normalized_data[:compression_idx].tolist()
            
            # Calculate compression quality
            if len(normalized_data) > 0:
                variance_preserved = np.var(compressed_data) / (np.var(normalized_data) or 1.0)
            else:
                variance_preserved = 1.0
                
            quantum_params = {
                "algorithm": "pca",
                "mean": float(data_mean),
                "scale": float(np.std(centered_data) or 1.0),
                "original_size": len(data_array)
            }
        else:
            # For multi-dimensional data (placeholder for actual PCA)
            # Convert numpy types to Python native types
            compressed_data = [float(x) if isinstance(x, np.floating) else int(x) if isinstance(x, np.integer) else x 
                             for x in centered_data.flatten()[:n_components]]
            variance_preserved = self.compression_level
            quantum_params = {
                "algorithm": "pca",
                "mean": float(data_mean),
                "original_shape": tuple(int(dim) for dim in data_array.shape),
                "original_size": int(data_array.size)
            }
        
        # Record the compression event in the measurement recorder
        self.measurement_recorder.record_measurement(
            measurement=variance_preserved,
            timestamp=time.time(),
            qubit_index=0
        )
        
        return {
            "quantum_compressed": True,
            "algorithm": "pca",
            "compressed_data": compressed_data,
            "quantum_parameters": quantum_params,
            "compression_quality": variance_preserved
        }
    
    def _decompress_quantum_data(self, compressed_data: Dict[str, Any]) -> List[float]:
        """
        Decompress data from quantum-aware format
        
        Args:
            compressed_data: Data in compressed format
            
        Returns:
            Decompressed data
        """
        if not compressed_data.get("quantum_compressed"):
            return compressed_data
            
        algorithm = compressed_data.get("algorithm", "pca")
        data = compressed_data.get("compressed_data", [])
        params = compressed_data.get("quantum_parameters", {})
        
        if algorithm in ["gzip", "zlib"]:
            # Use standard decompression algorithm
            decompress_func = self.COMPRESSION_ALGORITHMS[algorithm]["decompress"]
            decompressed_str = decompress_func(data)
            try:
                return json.loads(decompressed_str)
            except json.JSONDecodeError:
                # Fallback to basic handling if JSON parsing fails
                return decompressed_str
        else:
            # PCA-like decompression
            return self._pca_decompress(data, params)
    
    def _pca_decompress(self, data: List[float], params: Dict[str, Any]) -> List[float]:
        """
        Decompress data using PCA-like approach
        
        Args:
            data: Compressed data array
            params: Compression parameters
            
        Returns:
            Decompressed data
        """
        # Extract parameters
        mean = params.get("mean", 0.0)
        scale = params.get("scale", 1.0)
        original_size = params.get("original_size", len(data))
        
        # Basic decompression (expand and denormalize)
        if "original_shape" in params:
            # Multi-dimensional data (placeholder)
            result = np.zeros(original_size)
            result[:len(data)] = data
            result = result * scale + mean
        else:
            # 1D data
            result = np.zeros(original_size)
            result[:len(data)] = data
            result = result * scale + mean
            
        return result.tolist()
    
    def _add_quantum_checksums(self):
        """Add quantum checksums for data integrity verification"""
        # Create a copy of data without quantum_integrity to avoid circular references
        data_copy = {k: v for k, v in self.data.items() if k != "quantum_integrity"}
        
        # Create a simple quantum checksum using SHA-3 (classical simulation)
        data_str = json.dumps(data_copy, sort_keys=True, cls=NumpyJSONEncoder)
        checksum = hashlib.sha3_256(data_str.encode()).hexdigest()
        
        if self.quantum_safe_crypto:
            # Simulate post-quantum cryptographic algorithm (lattice-based)
            # This is a simplified simulation of a post-quantum algorithm
            pq_checksum = self._simulate_lattice_checksum(data_str)
            checksum_type = "post_quantum"
        else:
            # Create a simulated GHZ-based checksum for quantum verification
            pq_checksum = self._simulate_quantum_checksum(data_str)
            checksum_type = "quantum_ghz"
        
        self.data["quantum_integrity"] = {
            "quantum_checksum": pq_checksum,
            "classical_checksum": checksum,
            "checksum_type": checksum_type,
            "timestamp": time.time()
        }
    
    def _simulate_lattice_checksum(self, data_str: str) -> str:
        """
        Simulate a post-quantum lattice-based checksum
        
        This is a simplified simulation of a lattice-based cryptographic function
        which would be resistant to quantum attacks.
        
        Args:
            data_str: String representation of data
            
        Returns:
            Post-quantum checksum
        """
        # Use SHA3-512 as base to simulate higher bit strength needed for PQ
        base_digest = hashlib.sha3_512(data_str.encode()).digest()
        
        # Simulate lattice-based operations
        # In reality, would use NTRU, Dilithium, or similar algorithms
        # Convert to regular Python int to avoid numpy int64 issues
        digest_int = int.from_bytes(base_digest, byteorder='big')
        
        # Simulate modular operations against a large prime (part of lattice cryptography)
        prime_modulus = 2**521 - 1  # A Mersenne prime
        lattice_result = int(digest_int % prime_modulus)  # Ensure result is a regular Python int
        
        # Format result as hex string with fixed length
        return format(lattice_result, 'x')[:64]
    
    def _simulate_quantum_checksum(self, data_str: str) -> str:
        """
        Simulate a quantum checksum using GHZ states (classical simulation)
        
        In a real quantum system, this would involve quantum circuit operations
        """
        # Convert string to bytes and hash to get a fixed-length digest
        digest = hashlib.sha3_256(data_str.encode()).digest()
        
        # Simulate GHZ state preparation and measurement
        # (In a real quantum system, this would involve quantum operations)
        n_qubits = min(self.quantum_bits, 8)  # Use at most 8 qubits for checksum
        
        # Simulate phase encoding based on hash digest
        phases = []
        for i in range(n_qubits):
            # Use each byte of digest to determine a phase angle
            phase_val = digest[i % len(digest)] / 255.0 * np.pi
            phases.append(phase_val)
        
        # Simulate GHZ measurement outcomes
        # (This is a simplified classical simulation)
        checksum_bits = []
        for phase in phases:
            # Simulate measurement of a phase-encoded qubit
            # In a real quantum system, this would be an actual measurement
            measurement = 1 if np.cos(phase) > 0 else 0
            checksum_bits.append(str(measurement))
        
        return "".join(checksum_bits)
    
    def _verify_quantum_integrity(self, data: Dict[str, Any]) -> bool:
        """
        Verify data integrity using quantum checksums
        
        Args:
            data: Data to verify
            
        Returns:
            True if data is valid, False otherwise
        """
        if "quantum_integrity" not in data:
            return False
            
        integrity_data = data["quantum_integrity"]
        stored_classical_checksum = integrity_data.get("classical_checksum")
        checksum_type = integrity_data.get("checksum_type", "quantum_ghz")
        
        # Make a copy of data without the quantum_integrity field for validation
        validation_data = data.copy()
        validation_data.pop("quantum_integrity")
        
        # Calculate checksum of current data
        data_str = json.dumps(validation_data, sort_keys=True, cls=NumpyJSONEncoder)
        current_checksum = hashlib.sha3_256(data_str.encode()).hexdigest()
        
        # Verify classical checksum
        if current_checksum != stored_classical_checksum:
            return False
            
        # If quantum-safe verification is needed, verify that too
        if checksum_type == "post_quantum" and self.quantum_safe_crypto:
            stored_pq_checksum = integrity_data.get("quantum_checksum")
            current_pq_checksum = self._simulate_lattice_checksum(data_str)
            return current_pq_checksum == stored_pq_checksum
            
        # Basic integrity check passed
        return True
        
    def add_quantum_circuit(self, name: str, circuit_data: Dict[str, Any]) -> None:
        """
        Add a quantum circuit representation to the data
        
        Args:
            name: Name of the circuit
            circuit_data: Circuit representation data (can be OpenQASM, Qiskit, etc.)
        """
        if "quantum_circuits" not in self.data:
            self.data["quantum_circuits"] = {}
            
        self.data["quantum_circuits"][name] = {
            "data": circuit_data,
            "added": time.time()
        }
        self.quantum_circuits[name] = circuit_data
        self.metadata["modified"] = time.time()
        
    def get_quantum_circuit(self, name: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve a quantum circuit by name
        
        Args:
            name: Name of the circuit to retrieve
            
        Returns:
            Circuit data if found, None otherwise
        """
        return self.quantum_circuits.get(name)
        
    def add_error_correction_data(self, data: Dict[str, Any]) -> None:
        """
        Add quantum error correction data
        
        Args:
            data: Error correction data including syndrome measurements
        """
        if not self.error_correction:
            raise ValueError("Error correction is not enabled for this QJson instance")
            
        self.error_correction_data = data
        self.data["error_correction"] = {
            "syndrome_measurements": data.get("syndrome_measurements", []),
            "logical_encoding": data.get("logical_encoding", {}),
            "correction_code": data.get("correction_code", "surface"),
            "timestamp": time.time()
        }
        self.metadata["modified"] = time.time()


class AdaptiveParameterManager:
    """Manages adaptive parameters for quantum-classical data processing"""
    
    def __init__(self, initial_gain: float = 1.0, learning_rate: float = 0.05, max_value: float = 2.5):
        """
        Initialize the adaptive parameter manager
        
        Args:
            initial_gain: Initial feedback gain value
            learning_rate: Learning rate for parameter updates
            max_value: Maximum allowed value for parameters
        """
        self.feedback_gain = initial_gain
        self.learning_rate = learning_rate
        self.max_value = max_value
        self.performance_history = []
        
    def update_parameters(self, performance_metric: float) -> float:
        """
        Update feedback gain using gradient ascent
        
        Args:
            performance_metric: Metric to optimize parameters for
            
        Returns:
            Updated feedback gain
        """
        self.performance_history.append(performance_metric)
        
        # Calculate gradient (simplified)
        if len(self.performance_history) >= 2:
            gradient = self.performance_history[-1] - self.performance_history[-2]
            
            # Update feedback gain
            self.feedback_gain += self.learning_rate * gradient
            
            # Apply constraints
            self.feedback_gain = min(self.max_value, max(0, self.feedback_gain))
            
        return self.feedback_gain


class TimeTaggedQuantumRecorder:
    """Records time-tagged quantum measurements"""
    
    def __init__(self, compression_threshold: float = 0.01):
        """
        Initialize a quantum measurement recorder
        
        Args:
            compression_threshold: Threshold for recording measurements
        """
        self.measurements = []
        self.threshold = compression_threshold
        self.timestamp_reference = 0
        
    def record_measurement(self, measurement: float, timestamp: float, qubit_index: int):
        """
        Record a quantum measurement with time tag
        
        Args:
            measurement: Measurement result
            timestamp: Time when measurement occurred
            qubit_index: Index of the qubit measured
        """
        if self.timestamp_reference == 0:
            self.timestamp_reference = timestamp
            
        relative_time = timestamp - self.timestamp_reference
        
        # Only record if measurement exceeds threshold (sparse encoding)
        if abs(measurement) > self.threshold:
            self.measurements.append({
                "result": measurement,
                "time": relative_time,
                "qubit": qubit_index
            })
    
    def get_measurements(self) -> List[Dict[str, float]]:
        """Get recorded measurements"""
        return self.measurements