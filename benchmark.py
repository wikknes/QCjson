#!/usr/bin/env python3
"""
QJson Benchmark Tool

This script benchmarks QJson against other data formats (JSON, BSON, MessagePack, etc.)
in terms of:
- Encoding/decoding speed
- Compression efficiency
- Deserialization accuracy
- Memory usage

The benchmark includes visualization of results using matplotlib.
"""

import json
import time
import os
import gc
import platform
import argparse
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter
import pandas as pd
import sys
from collections import defaultdict
import tempfile
import resource

# Import QJson
from qjson import QJson

# Try to import other data format libraries
try:
    import msgpack
    HAVE_MSGPACK = True
except ImportError:
    HAVE_MSGPACK = False
    print("Warning: MessagePack not installed. Skipping MessagePack benchmarks.")

try:
    import bson
    HAVE_BSON = True
except ImportError:
    HAVE_BSON = False
    print("Warning: BSON not installed. Skipping BSON benchmarks.")

try:
    import cbor2
    HAVE_CBOR = True
except ImportError:
    HAVE_CBOR = False
    print("Warning: CBOR not installed. Skipping CBOR benchmarks.")

try:
    import pickle
    HAVE_PICKLE = True
except ImportError:
    HAVE_PICKLE = False
    print("Warning: Pickle not installed. Skipping Pickle benchmarks.")

try:
    import pyarrow as pa
    HAVE_ARROW = True
except ImportError:
    HAVE_ARROW = False
    print("Warning: PyArrow not installed. Skipping Arrow benchmarks.")


class BenchmarkRunner:
    """Runs benchmarks comparing QJson with other data formats"""

    def __init__(self, iterations=5, data_size='medium'):
        """
        Initialize benchmark runner
        
        Args:
            iterations: Number of iterations for each benchmark
            data_size: Size of test data ('small', 'medium', 'large')
        """
        self.iterations = iterations
        self.data_size = data_size
        self.results = defaultdict(lambda: defaultdict(dict))
        self.formats = ['json', 'qjson_gzip', 'qjson_zlib', 'qjson_pca']
        
        # Add available optional formats
        if HAVE_MSGPACK:
            self.formats.append('msgpack')
        if HAVE_BSON:
            self.formats.append('bson')
        if HAVE_CBOR:
            self.formats.append('cbor')
        if HAVE_PICKLE:
            self.formats.append('pickle')
        if HAVE_ARROW:
            self.formats.append('arrow')
            
        # Generate test data
        self.data = self._generate_test_data(data_size)
        
        # Create various QJson instances with different settings
        self.qjson_gzip = QJson(compression_algorithm="gzip", compression_level=0.5)
        self.qjson_zlib = QJson(compression_algorithm="zlib", compression_level=0.5)
        self.qjson_pca = QJson(compression_algorithm="pca", compression_level=0.5)
        
    def _generate_test_data(self, size):
        """
        Generate test data of specified size
        
        Args:
            size: Data size ('small', 'medium', 'large')
            
        Returns:
            Dictionary containing test data
        """
        # Base sizes for different data configurations
        if size == 'small':
            array_size = 100
            nested_depth = 2
            num_arrays = 3
        elif size == 'medium':
            array_size = 1000
            nested_depth = 3
            num_arrays = 5
        elif size == 'large':
            array_size = 10000
            nested_depth = 4
            num_arrays = 10
        else:
            raise ValueError(f"Unknown data size: {size}")
            
        data = {
            "metadata": {
                "id": f"benchmark_{size}",
                "timestamp": time.time(),
                "description": f"Benchmark test data ({size})",
                "system": platform.system(),
                "python_version": platform.python_version()
            }
        }
        
        # Add numeric arrays (good for testing compression)
        for i in range(num_arrays):
            if i % 3 == 0:
                # Random floats between 0 and 1
                data[f"float_array_{i}"] = list(np.random.rand(array_size))
            elif i % 3 == 1:
                # Random integers - convert numpy int types to regular Python integers
                data[f"int_array_{i}"] = [int(x) for x in np.random.randint(0, 100, array_size)]
            else:
                # Sine wave (highly compressible)
                x = np.linspace(0, 10, array_size)
                data[f"sine_array_{i}"] = list(np.sin(x))
        
        # Add nested structures
        nested = {}
        current = nested
        for i in range(nested_depth):
            current["level"] = i
            current["array"] = list(range(min(100, array_size // 10)))
            current["timestamp"] = time.time()
            current["next"] = {}
            current = current["next"]
        
        data["nested"] = nested
        
        # Add string data
        data["text"] = "This is a sample text that will be repeated. " * 20
        
        # Add quantum-like data
        qubits = min(16, array_size // 100)
        data["quantum_circuits"] = []
        for i in range(qubits):
            circuit = {
                "id": f"circuit_{i}",
                "qubits": qubits,
                "gates": [
                    {"type": "h", "target": q} for q in range(qubits)
                ] + [
                    {"type": "cx", "control": q % qubits, "target": (q + 1) % qubits} 
                    for q in range(qubits)
                ]
            }
            data["quantum_circuits"].append(circuit)
            
        return data
        
    def _measure_time(self, func, *args, **kwargs):
        """Measure execution time of a function"""
        start = time.time()
        result = func(*args, **kwargs)
        end = time.time()
        return end - start, result
        
    def _measure_memory(self, obj):
        """Estimate memory usage of an object in bytes"""
        if isinstance(obj, str):
            return len(obj.encode('utf-8'))
        elif isinstance(obj, bytes):
            return len(obj)
        else:
            # For complex objects, use sys.getsizeof as an approximation
            # Note: This doesn't account for all nested references
            return sys.getsizeof(obj)
            
    def run_serialization_benchmark(self):
        """Benchmark serialization performance"""
        print(f"\nRunning serialization benchmark ({self.iterations} iterations)...")
        
        format_data = {}  # To store serialized data for later benchmarks
        
        for fmt in self.formats:
            print(f"Testing {fmt}...")
            serialize_times = []
            deserialize_times = []
            serialized_sizes = []
            
            for i in range(self.iterations):
                # Serialize
                if fmt == 'json':
                    time_taken, serialized = self._measure_time(json.dumps, self.data)
                elif fmt == 'qjson_gzip':
                    time_taken, encoded = self._measure_time(self.qjson_gzip.encode, self.data)
                    serialized = self.qjson_gzip.to_json()
                elif fmt == 'qjson_zlib':
                    time_taken, encoded = self._measure_time(self.qjson_zlib.encode, self.data)
                    serialized = self.qjson_zlib.to_json()
                elif fmt == 'qjson_pca':
                    time_taken, encoded = self._measure_time(self.qjson_pca.encode, self.data)
                    serialized = self.qjson_pca.to_json()
                elif fmt == 'msgpack':
                    time_taken, serialized = self._measure_time(msgpack.packb, self.data, use_bin_type=True)
                elif fmt == 'bson':
                    time_taken, serialized = self._measure_time(bson.encode, self.data)
                elif fmt == 'cbor':
                    time_taken, serialized = self._measure_time(cbor2.dumps, self.data)
                elif fmt == 'pickle':
                    time_taken, serialized = self._measure_time(pickle.dumps, self.data, protocol=pickle.HIGHEST_PROTOCOL)
                elif fmt == 'arrow':
                    # PyArrow requires special handling for complex nested structures
                    try:
                        time_taken, arrow_table = self._measure_time(pa.Table.from_pydict, 
                                                                     {k: v for k, v in self.data.items() 
                                                                      if not isinstance(v, dict)})
                        _, serialized = self._measure_time(pa.ipc.new_stream, arrow_table)
                        serialized = serialized.write_to_memory()
                    except Exception as e:
                        print(f"  Error with Arrow: {e}")
                        continue
                
                serialize_times.append(time_taken)
                serialized_sizes.append(self._measure_memory(serialized))
                
                # Store first serialized result for deserialize benchmark
                if i == 0:
                    format_data[fmt] = serialized
                
                # Deserialize
                if fmt == 'json':
                    time_taken, _ = self._measure_time(json.loads, serialized)
                elif fmt.startswith('qjson_'):
                    time_taken, _ = self._measure_time(json.loads, serialized)
                elif fmt == 'msgpack':
                    time_taken, _ = self._measure_time(msgpack.unpackb, serialized, raw=False)
                elif fmt == 'bson':
                    time_taken, _ = self._measure_time(bson.decode, serialized)
                elif fmt == 'cbor':
                    time_taken, _ = self._measure_time(cbor2.loads, serialized)
                elif fmt == 'pickle':
                    time_taken, _ = self._measure_time(pickle.loads, serialized)
                elif fmt == 'arrow':
                    try:
                        reader = pa.ipc.open_stream(serialized)
                        time_taken, _ = self._measure_time(reader.read_all)
                    except Exception as e:
                        print(f"  Error deserializing Arrow: {e}")
                        continue
                
                deserialize_times.append(time_taken)
                
                # Force garbage collection to reduce interference
                gc.collect()
            
            # Calculate average results
            avg_serialize_time = np.mean(serialize_times)
            avg_deserialize_time = np.mean(deserialize_times)
            avg_size = np.mean(serialized_sizes)
            
            # Store results
            self.results['serialization'][fmt] = {
                'serialize_time': avg_serialize_time,
                'deserialize_time': avg_deserialize_time,
                'size': avg_size
            }
            
            print(f"  Avg Serialize Time: {avg_serialize_time:.6f}s")
            print(f"  Avg Deserialize Time: {avg_deserialize_time:.6f}s")
            print(f"  Avg Size: {avg_size/1024:.2f} KB")
        
        # Store format_data for other benchmarks
        self.format_data = format_data
    
    def run_disk_io_benchmark(self):
        """Benchmark disk I/O performance"""
        print(f"\nRunning disk I/O benchmark ({self.iterations} iterations)...")
        
        for fmt in self.formats:
            if fmt not in self.format_data:
                print(f"Skipping {fmt} - no serialized data available")
                continue
                
            print(f"Testing {fmt}...")
            write_times = []
            read_times = []
            
            serialized = self.format_data[fmt]
            
            for i in range(self.iterations):
                # Create a temporary file
                with tempfile.NamedTemporaryFile(delete=False) as tmp:
                    tmp_name = tmp.name
                
                # Write to disk
                time_taken, _ = self._measure_time(
                    lambda data, filename: open(filename, 'wb').write(data) if isinstance(data, bytes) 
                    else open(filename, 'w').write(data),
                    serialized, tmp_name
                )
                write_times.append(time_taken)
                
                # Read from disk
                time_taken, _ = self._measure_time(
                    lambda filename: open(filename, 'rb').read() if isinstance(serialized, bytes)
                    else open(filename, 'r').read(),
                    tmp_name
                )
                read_times.append(time_taken)
                
                # Clean up
                os.unlink(tmp_name)
                gc.collect()
            
            # Calculate average results
            avg_write_time = np.mean(write_times)
            avg_read_time = np.mean(read_times)
            
            # Store results
            self.results['disk_io'][fmt] = {
                'write_time': avg_write_time,
                'read_time': avg_read_time
            }
            
            print(f"  Avg Write Time: {avg_write_time:.6f}s")
            print(f"  Avg Read Time: {avg_read_time:.6f}s")
    
    def run_memory_usage_benchmark(self):
        """Benchmark memory usage during operations"""
        print(f"\nRunning memory usage benchmark...")
        
        for fmt in self.formats:
            if fmt not in self.format_data:
                print(f"Skipping {fmt} - no serialized data available")
                continue
                
            print(f"Testing {fmt}...")
            serialized = self.format_data[fmt]
            
            # Measure baseline memory
            gc.collect()
            baseline = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
            
            # Deserialize and measure peak memory
            if fmt == 'json':
                json.loads(serialized)
            elif fmt.startswith('qjson_'):
                json.loads(serialized)
            elif fmt == 'msgpack':
                msgpack.unpackb(serialized, raw=False)
            elif fmt == 'bson':
                bson.decode(serialized)
            elif fmt == 'cbor':
                cbor2.loads(serialized)
            elif fmt == 'pickle':
                pickle.loads(serialized)
            elif fmt == 'arrow':
                try:
                    reader = pa.ipc.open_stream(serialized)
                    reader.read_all()
                except Exception as e:
                    print(f"  Error with Arrow: {e}")
                    continue
            
            # Measure memory after operation
            peak = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
            memory_used = peak - baseline
            
            # Store results
            self.results['memory'][fmt] = {
                'usage': memory_used
            }
            
            print(f"  Memory Usage: {memory_used} KB")
            
            # Force garbage collection
            gc.collect()
    
    def run_full_qjson_benchmark(self):
        """Run QJson-specific benchmarks including encode/decode cycle"""
        print(f"\nRunning full QJson benchmarks...")
        
        qjson_variants = {
            'qjson_gzip': self.qjson_gzip,
            'qjson_zlib': self.qjson_zlib,
            'qjson_pca': self.qjson_pca
        }
        
        for fmt, qjson in qjson_variants.items():
            print(f"Testing {fmt} full cycle...")
            encode_times = []
            decode_times = []
            end_to_end_times = []
            fidelity_scores = []
            
            for i in range(self.iterations):
                # Measure encode time
                encode_start = time.time()
                encoded = qjson.encode(self.data)
                encode_end = time.time()
                encode_time = encode_end - encode_start
                encode_times.append(encode_time)
                
                # Measure decode time
                decode_start = time.time()
                decoded = qjson.decode(encoded)
                decode_end = time.time()
                decode_time = decode_end - decode_start
                decode_times.append(decode_time)
                
                # Calculate end-to-end time
                end_to_end_times.append(encode_time + decode_time)
                
                # Calculate fidelity (how well original data is preserved)
                # For numeric arrays, we'll check how close the values are
                fidelity = self._calculate_fidelity(self.data, decoded)
                fidelity_scores.append(fidelity)
                
                gc.collect()
            
            # Calculate average results
            avg_encode_time = np.mean(encode_times)
            avg_decode_time = np.mean(decode_times)
            avg_end_to_end = np.mean(end_to_end_times)
            avg_fidelity = np.mean(fidelity_scores)
            
            # Store results
            self.results['qjson_full'][fmt] = {
                'encode_time': avg_encode_time,
                'decode_time': avg_decode_time,
                'end_to_end_time': avg_end_to_end,
                'fidelity': avg_fidelity
            }
            
            print(f"  Avg Encode Time: {avg_encode_time:.6f}s")
            print(f"  Avg Decode Time: {avg_decode_time:.6f}s")
            print(f"  Avg End-to-End Time: {avg_end_to_end:.6f}s")
            print(f"  Avg Fidelity Score: {avg_fidelity:.4f} (1.0 is perfect)")
    
    def _calculate_fidelity(self, original, decoded):
        """
        Calculate how faithfully the original data is preserved after encoding/decoding
        
        Returns a score between 0.0 and 1.0, where 1.0 means perfect preservation
        """
        if not isinstance(original, dict) or not isinstance(decoded, dict):
            return 0.0  # Can't compare non-dictionaries
            
        # Count matching keys
        original_keys = set(original.keys())
        decoded_keys = set(decoded.keys())
        common_keys = original_keys.intersection(decoded_keys)
        key_score = len(common_keys) / len(original_keys) if original_keys else 1.0
        
        value_scores = []
        for key in common_keys:
            orig_val = original[key]
            decoded_val = decoded[key]
            
            # Skip integrity checksums
            if key == "quantum_integrity":
                continue
                
            # Handle different data types
            if isinstance(orig_val, (list, np.ndarray)) and isinstance(decoded_val, (list, np.ndarray)):
                # For arrays, compare length and values
                if len(orig_val) != len(decoded_val):
                    value_scores.append(0.5 * min(len(orig_val), len(decoded_val)) / max(len(orig_val), len(decoded_val)))
                else:
                    # For numeric arrays, calculate RMSE and normalize to [0, 1]
                    try:
                        orig_array = np.array(orig_val, dtype=float)
                        decoded_array = np.array(decoded_val, dtype=float)
                        rmse = np.sqrt(np.mean((orig_array - decoded_array) ** 2))
                        # Convert RMSE to similarity score (1.0 for identical, approaching 0.0 for very different)
                        max_val = max(np.max(np.abs(orig_array)), 1e-10)  # Avoid division by zero
                        value_scores.append(max(0.0, 1.0 - min(1.0, rmse / max_val)))
                    except (ValueError, TypeError):
                        # Non-numeric arrays, count matching elements
                        matches = sum(1 for a, b in zip(orig_val, decoded_val) if a == b)
                        value_scores.append(matches / len(orig_val) if orig_val else 1.0)
            elif isinstance(orig_val, dict) and isinstance(decoded_val, dict):
                # Recursively calculate fidelity for nested dictionaries
                value_scores.append(self._calculate_fidelity(orig_val, decoded_val))
            elif orig_val == decoded_val:
                # Exact match for non-collection types
                value_scores.append(1.0)
            else:
                # Different values
                value_scores.append(0.0)
        
        # Average value scores
        avg_value_score = np.mean(value_scores) if value_scores else 1.0
        
        # Combine key and value scores (weight keys less since QJson adds metadata keys)
        return 0.3 * key_score + 0.7 * avg_value_score
    
    def visualize_results(self):
        """Create visualizations of benchmark results"""
        print("\nGenerating visualizations...")
        
        # Set up plot style
        plt.style.use('ggplot')
        plt.rcParams['figure.figsize'] = [12, 8]
        
        # 1. Serialization Speed Comparison
        self._plot_serialization_speed()
        
        # 2. Size Comparison
        self._plot_size_comparison()
        
        # 3. Disk I/O Performance
        self._plot_disk_io()
        
        # 4. Memory Usage
        self._plot_memory_usage()
        
        # 5. QJson Variants Comparison
        self._plot_qjson_variants()
        
        # 6. Speed vs Size Trade-off
        self._plot_speed_vs_size()
        
        # 7. Combined Performance Radar Chart
        self._plot_performance_radar()
        
        print("Visualizations complete. Results saved as PNG files.")
    
    def _plot_serialization_speed(self):
        """Plot serialization and deserialization speed comparison"""
        if not self.results.get('serialization'):
            return
            
        data = self.results['serialization']
        formats = list(data.keys())
        
        serialize_times = [data[fmt]['serialize_time'] for fmt in formats]
        deserialize_times = [data[fmt]['deserialize_time'] for fmt in formats]
        
        fig, ax = plt.subplots()
        width = 0.35
        x = np.arange(len(formats))
        
        ax.bar(x - width/2, serialize_times, width, label='Serialize')
        ax.bar(x + width/2, deserialize_times, width, label='Deserialize')
        
        ax.set_title('Serialization Speed Comparison (Lower is Better)')
        ax.set_xlabel('Format')
        ax.set_ylabel('Time (seconds)')
        ax.set_xticks(x)
        ax.set_xticklabels(formats, rotation=45)
        ax.legend()
        
        plt.tight_layout()
        plt.savefig('benchmark_serialization_speed.png')
        plt.close()
    
    def _plot_size_comparison(self):
        """Plot serialized data size comparison"""
        if not self.results.get('serialization'):
            return
            
        data = self.results['serialization']
        formats = list(data.keys())
        sizes = [data[fmt]['size'] / 1024 for fmt in formats]  # Convert to KB
        
        fig, ax = plt.subplots()
        ax.bar(formats, sizes)
        
        ax.set_title('Serialized Data Size Comparison (Lower is Better)')
        ax.set_xlabel('Format')
        ax.set_ylabel('Size (KB)')
        plt.xticks(rotation=45)
        
        # Format y-axis labels
        def kb_formatter(x, pos):
            return f'{x:.1f} KB'
        ax.yaxis.set_major_formatter(FuncFormatter(kb_formatter))
        
        plt.tight_layout()
        plt.savefig('benchmark_size_comparison.png')
        plt.close()
    
    def _plot_disk_io(self):
        """Plot disk I/O performance"""
        if not self.results.get('disk_io'):
            return
            
        data = self.results['disk_io']
        formats = list(data.keys())
        
        write_times = [data[fmt]['write_time'] for fmt in formats]
        read_times = [data[fmt]['read_time'] for fmt in formats]
        
        fig, ax = plt.subplots()
        width = 0.35
        x = np.arange(len(formats))
        
        ax.bar(x - width/2, write_times, width, label='Write')
        ax.bar(x + width/2, read_times, width, label='Read')
        
        ax.set_title('Disk I/O Performance (Lower is Better)')
        ax.set_xlabel('Format')
        ax.set_ylabel('Time (seconds)')
        ax.set_xticks(x)
        ax.set_xticklabels(formats, rotation=45)
        ax.legend()
        
        plt.tight_layout()
        plt.savefig('benchmark_disk_io.png')
        plt.close()
    
    def _plot_memory_usage(self):
        """Plot memory usage during operations"""
        if not self.results.get('memory'):
            return
            
        data = self.results['memory']
        formats = list(data.keys())
        memory_usage = [data[fmt]['usage'] for fmt in formats]
        
        fig, ax = plt.subplots()
        ax.bar(formats, memory_usage)
        
        ax.set_title('Memory Usage (Lower is Better)')
        ax.set_xlabel('Format')
        ax.set_ylabel('Memory (KB)')
        plt.xticks(rotation=45)
        
        plt.tight_layout()
        plt.savefig('benchmark_memory_usage.png')
        plt.close()
    
    def _plot_qjson_variants(self):
        """Compare different QJson variants"""
        if not self.results.get('qjson_full'):
            return
            
        data = self.results['qjson_full']
        formats = list(data.keys())
        
        encode_times = [data[fmt]['encode_time'] for fmt in formats]
        decode_times = [data[fmt]['decode_time'] for fmt in formats]
        fidelity_scores = [data[fmt]['fidelity'] for fmt in formats]
        
        # Create figure with multiple subplots
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))
        
        # Plot 1: Encode/Decode Times
        width = 0.35
        x = np.arange(len(formats))
        
        ax1.bar(x - width/2, encode_times, width, label='Encode')
        ax1.bar(x + width/2, decode_times, width, label='Decode')
        
        ax1.set_title('QJson Variants - Processing Time (Lower is Better)')
        ax1.set_xlabel('Format')
        ax1.set_ylabel('Time (seconds)')
        ax1.set_xticks(x)
        ax1.set_xticklabels([fmt.split('_')[1] for fmt in formats])
        ax1.legend()
        
        # Plot 2: Fidelity Scores
        ax2.bar(formats, fidelity_scores)
        ax2.set_title('QJson Variants - Data Fidelity (Higher is Better)')
        ax2.set_xlabel('Format')
        ax2.set_ylabel('Fidelity Score (0-1)')
        ax2.set_ylim([0, 1])
        ax2.set_xticklabels([fmt.split('_')[1] for fmt in formats])
        
        plt.tight_layout()
        plt.savefig('benchmark_qjson_variants.png')
        plt.close()
    
    def _plot_speed_vs_size(self):
        """Plot speed vs size trade-off"""
        if not self.results.get('serialization'):
            return
            
        data = self.results['serialization']
        formats = list(data.keys())
        
        # Calculate total processing time (serialize + deserialize)
        times = [data[fmt]['serialize_time'] + data[fmt]['deserialize_time'] for fmt in formats]
        sizes = [data[fmt]['size'] / 1024 for fmt in formats]  # Convert to KB
        
        fig, ax = plt.subplots()
        ax.scatter(sizes, times, s=100)
        
        # Add format labels to each point
        for i, fmt in enumerate(formats):
            ax.annotate(fmt, (sizes[i], times[i]), 
                        xytext=(7, 0), textcoords='offset points')
        
        ax.set_title('Speed vs Size Trade-off (Lower Left is Better)')
        ax.set_xlabel('Size (KB)')
        ax.set_ylabel('Total Processing Time (seconds)')
        
        # Add quadrant lines and annotations
        size_mid = np.median(sizes)
        time_mid = np.median(times)
        
        ax.axhline(time_mid, color='gray', linestyle='--', alpha=0.5)
        ax.axvline(size_mid, color='gray', linestyle='--', alpha=0.5)
        
        # Add quadrant labels
        ax.text(np.min(sizes), np.min(times), "Optimal\n(Fast & Small)", 
                verticalalignment='bottom', horizontalalignment='left')
        ax.text(np.max(sizes), np.min(times), "Fast but Large",
                verticalalignment='bottom', horizontalalignment='right')
        ax.text(np.min(sizes), np.max(times), "Slow but Small",
                verticalalignment='top', horizontalalignment='left')
        ax.text(np.max(sizes), np.max(times), "Suboptimal\n(Slow & Large)",
                verticalalignment='top', horizontalalignment='right')
        
        plt.tight_layout()
        plt.savefig('benchmark_speed_vs_size.png')
        plt.close()
    
    def _plot_performance_radar(self):
        """Create a radar chart for overall performance comparison"""
        if not self.results.get('serialization'):
            return
            
        # Prepare data from multiple benchmark categories
        formats = []
        metrics = ['Serialization Speed', 'Deserialization Speed', 'Size Efficiency', 
                  'Write Speed', 'Read Speed', 'Memory Efficiency']
        
        # Find common formats across benchmarks
        ser_formats = set(self.results['serialization'].keys())
        io_formats = set(self.results['disk_io'].keys() if 'disk_io' in self.results else [])
        mem_formats = set(self.results['memory'].keys() if 'memory' in self.results else [])
        
        formats = list(ser_formats.intersection(io_formats).intersection(mem_formats))
        
        if not formats:
            print("Not enough data for radar chart")
            return
        
        # Prepare data for each format
        # We'll normalize each metric to be between 0 and 1 (1 is best)
        data = {}
        for fmt in formats:
            data[fmt] = []
            
            # Serialization metrics (convert times to speeds by taking inverse)
            ser_time = self.results['serialization'][fmt]['serialize_time']
            deser_time = self.results['serialization'][fmt]['deserialize_time']
            data[fmt].append(1.0 / ser_time if ser_time else 0)
            data[fmt].append(1.0 / deser_time if deser_time else 0)
            
            # Size efficiency (smaller is better, so take inverse)
            size = self.results['serialization'][fmt]['size']
            data[fmt].append(1.0 / size if size else 0)
            
            # Disk I/O metrics (convert times to speeds)
            if 'disk_io' in self.results and fmt in self.results['disk_io']:
                write_time = self.results['disk_io'][fmt]['write_time']
                read_time = self.results['disk_io'][fmt]['read_time']
                data[fmt].append(1.0 / write_time if write_time else 0)
                data[fmt].append(1.0 / read_time if read_time else 0)
            else:
                data[fmt].extend([0, 0])
            
            # Memory efficiency (smaller is better)
            if 'memory' in self.results and fmt in self.results['memory']:
                mem_usage = self.results['memory'][fmt]['usage']
                data[fmt].append(1.0 / mem_usage if mem_usage else 0)
            else:
                data[fmt].append(0)
        
        # Normalize data across formats
        normalized_data = {}
        for m in range(len(metrics)):
            max_val = max(data[fmt][m] for fmt in formats)
            if max_val > 0:
                for fmt in formats:
                    if fmt not in normalized_data:
                        normalized_data[fmt] = []
                    normalized_data[fmt].append(data[fmt][m] / max_val)
            else:
                for fmt in formats:
                    if fmt not in normalized_data:
                        normalized_data[fmt] = []
                    normalized_data[fmt].append(0)
        
        # Plot radar chart
        fig = plt.figure(figsize=(10, 10))
        ax = fig.add_subplot(111, polar=True)
        
        # Number of metrics
        N = len(metrics)
        
        # Angle of each axis
        angles = [n / float(N) * 2 * np.pi for n in range(N)]
        angles += angles[:1]  # Close the loop
        
        # Plot each format
        colors = plt.cm.tab10(np.linspace(0, 1, len(formats)))
        for i, fmt in enumerate(formats):
            values = normalized_data[fmt]
            values += values[:1]  # Close the loop
            ax.plot(angles, values, 'o-', linewidth=2, color=colors[i], label=fmt)
            ax.fill(angles, values, color=colors[i], alpha=0.25)
        
        # Fix axis to go in the right order and start at 12 o'clock
        ax.set_theta_offset(np.pi / 2)
        ax.set_theta_direction(-1)
        
        # Draw axis lines for each angle and label
        ax.set_xticks(angles[:-1])
        ax.set_xticklabels(metrics)
        
        # Draw y-axis labels
        ax.set_yticks([0.25, 0.5, 0.75, 1])
        ax.set_yticklabels(["0.25", "0.5", "0.75", "1.0"])
        ax.set_ylim(0, 1)
        
        # Add legend
        plt.legend(loc='upper right', bbox_to_anchor=(0.1, 0.1))
        
        plt.title('Performance Comparison (Higher is Better)', size=20, y=1.05)
        plt.tight_layout()
        plt.savefig('benchmark_performance_radar.png')
        plt.close()

def main():
    """Main function"""
    parser = argparse.ArgumentParser(description='Benchmark QJson against other data formats')
    parser.add_argument('--size', choices=['small', 'medium', 'large'], default='medium',
                        help='Size of test data')
    parser.add_argument('--iterations', type=int, default=5,
                        help='Number of iterations for each benchmark')
    parser.add_argument('--skip-io', action='store_true',
                        help='Skip disk I/O benchmarks')
    parser.add_argument('--skip-memory', action='store_true',
                        help='Skip memory usage benchmarks')
    
    args = parser.parse_args()
    
    # Print system info
    print("Benchmark Configuration:")
    print(f"  Python: {platform.python_version()}")
    print(f"  OS: {platform.system()} {platform.release()}")
    print(f"  Data Size: {args.size}")
    print(f"  Iterations: {args.iterations}")
    
    # Run benchmarks
    benchmark = BenchmarkRunner(iterations=args.iterations, data_size=args.size)
    benchmark.run_serialization_benchmark()
    
    if not args.skip_io:
        benchmark.run_disk_io_benchmark()
    
    if not args.skip_memory:
        benchmark.run_memory_usage_benchmark()
    
    benchmark.run_full_qjson_benchmark()
    
    # Visualize results
    benchmark.visualize_results()
    
    print("\nBenchmark complete!")

if __name__ == "__main__":
    main()