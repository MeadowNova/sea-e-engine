#!/usr/bin/env python3
"""
SEA-E Stress Test Runner

Long-running stress tests and performance benchmarks.
"""

import os
import sys
import time
import json
import psutil
import threading
from pathlib import Path
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed

# Add src to path for imports
sys.path.append(str(Path(__file__).parent.parent / "src"))
sys.path.append(str(Path(__file__).parent.parent))

try:
    from sea_engine import SEAEngine, ProductData
    from unittest.mock import Mock, patch
    import tempfile
    import shutil
except ImportError as e:
    print(f"Import error: {e}")
    print("Please ensure all dependencies are installed")
    sys.exit(1)


class StressTestRunner:
    """Comprehensive stress test runner for SEA-E engine."""
    
    def __init__(self, output_dir="reports"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        self.results = {}
        self.start_time = time.time()
        
    def setup_test_engine(self):
        """Set up a test engine with mocked APIs."""
        temp_dir = Path(tempfile.mkdtemp())
        config_dir = temp_dir / "config"
        config_dir.mkdir()
        
        # Copy config files
        original_config = Path(__file__).parent.parent / "config"
        if original_config.exists():
            shutil.copytree(original_config, config_dir, dirs_exist_ok=True)
        
        # Mock environment variables
        os.environ.update({
            'ETSY_API_KEY': 'stress_test_etsy_key',
            'ETSY_REFRESH_TOKEN': 'stress_test_refresh_token',
            'ETSY_SHOP_ID': 'stress_test_shop_id',
            'PRINTIFY_API_KEY': 'stress_test_printify_key',
            'PRINTIFY_SHOP_ID': 'stress_test_printify_shop_id'
        })
        
        try:
            engine = SEAEngine(config_dir=str(config_dir))
            
            # Mock API clients for stress testing
            engine.etsy_client = Mock()
            engine.printify_client = Mock()
            engine.sheets_client = Mock()
            engine.mockup_generator = Mock()
            
            # Configure fast mock responses
            engine.etsy_client.create_listing.return_value = {"listing_id": "stress_test_listing"}
            engine.printify_client.create_product.return_value = {"id": "stress_test_product"}
            engine.printify_client.upload_image.return_value = {"id": "stress_test_image"}
            engine.mockup_generator.generate_mockup.return_value = "stress_test_mockup.png"
            
            return engine, temp_dir
        except Exception as e:
            print(f"Failed to setup test engine: {e}")
            return None, None
    
    def create_test_products(self, count=100):
        """Create test products for stress testing."""
        temp_dir = Path(tempfile.mkdtemp())
        design_path = temp_dir / "stress_test_design.png"
        
        # Create minimal PNG file
        png_data = b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x02\x00\x00\x00\x90wS\xde\x00\x00\x00\tpHYs\x00\x00\x0b\x13\x00\x00\x0b\x13\x01\x00\x9a\x9c\x18\x00\x00\x00\x0cIDATx\x9cc```\x00\x00\x00\x04\x00\x01\xdd\x8d\xb4\x1c\x00\x00\x00\x00IEND\xaeB`\x82'
        
        with open(design_path, 'wb') as f:
            f.write(png_data)
        
        products = []
        product_types = ["t-shirt", "sweatshirt", "poster"]
        
        for i in range(count):
            product_type = product_types[i % len(product_types)]
            products.append(ProductData(
                design_name=f"Stress Test Product {i:04d}",
                design_file_path=str(design_path),
                product_type=product_type
            ))
        
        return products, temp_dir
    
    def monitor_system_resources(self, duration=300):
        """Monitor system resources during stress testing."""
        monitoring_data = {
            "cpu_usage": [],
            "memory_usage": [],
            "timestamps": []
        }
        
        start_time = time.time()
        
        while time.time() - start_time < duration:
            try:
                cpu_percent = psutil.cpu_percent(interval=1)
                memory_info = psutil.virtual_memory()
                
                monitoring_data["cpu_usage"].append(cpu_percent)
                monitoring_data["memory_usage"].append(memory_info.percent)
                monitoring_data["timestamps"].append(time.time())
                
                time.sleep(5)  # Monitor every 5 seconds
            except Exception as e:
                print(f"Monitoring error: {e}")
                break
        
        return monitoring_data
    
    def stress_test_single_product_processing(self, engine, iterations=1000):
        """Stress test single product processing."""
        print(f"🔥 Running single product stress test ({iterations} iterations)")
        
        products, temp_dir = self.create_test_products(1)
        test_product = products[0]
        
        start_time = time.time()
        errors = []
        successful_iterations = 0
        
        for i in range(iterations):
            try:
                result = engine.process_product(test_product)
                if result:
                    successful_iterations += 1
            except Exception as e:
                errors.append(f"Iteration {i}: {str(e)}")
            
            if i % 100 == 0:
                print(f"  Progress: {i}/{iterations} ({i/iterations*100:.1f}%)")
        
        end_time = time.time()
        duration = end_time - start_time
        
        # Cleanup
        shutil.rmtree(temp_dir)
        
        return {
            "test_name": "single_product_stress",
            "iterations": iterations,
            "successful_iterations": successful_iterations,
            "errors": len(errors),
            "error_rate": len(errors) / iterations,
            "duration": duration,
            "throughput": iterations / duration,
            "avg_time_per_iteration": duration / iterations,
            "error_samples": errors[:10]  # First 10 errors
        }
    
    def stress_test_batch_processing(self, engine, batch_size=50, num_batches=10):
        """Stress test batch processing."""
        print(f"🔥 Running batch processing stress test ({num_batches} batches of {batch_size})")
        
        start_time = time.time()
        batch_results = []
        total_products = 0
        total_errors = 0
        
        for batch_num in range(num_batches):
            print(f"  Processing batch {batch_num + 1}/{num_batches}")
            
            products, temp_dir = self.create_test_products(batch_size)
            batch_start = time.time()
            
            try:
                results = engine.process_products_batch(products)
                batch_end = time.time()
                
                batch_results.append({
                    "batch_number": batch_num + 1,
                    "products_processed": len(results) if results else 0,
                    "duration": batch_end - batch_start,
                    "success": True
                })
                
                total_products += len(results) if results else 0
                
            except Exception as e:
                batch_end = time.time()
                batch_results.append({
                    "batch_number": batch_num + 1,
                    "products_processed": 0,
                    "duration": batch_end - batch_start,
                    "success": False,
                    "error": str(e)
                })
                total_errors += 1
            
            # Cleanup
            shutil.rmtree(temp_dir)
        
        end_time = time.time()
        total_duration = end_time - start_time
        
        return {
            "test_name": "batch_processing_stress",
            "num_batches": num_batches,
            "batch_size": batch_size,
            "total_products": total_products,
            "successful_batches": sum(1 for r in batch_results if r["success"]),
            "failed_batches": total_errors,
            "total_duration": total_duration,
            "avg_batch_duration": total_duration / num_batches,
            "throughput": total_products / total_duration,
            "batch_results": batch_results
        }
    
    def stress_test_concurrent_processing(self, engine, num_workers=5, products_per_worker=20):
        """Stress test concurrent processing."""
        print(f"🔥 Running concurrent processing stress test ({num_workers} workers, {products_per_worker} products each)")
        
        def worker_function(worker_id):
            worker_results = {
                "worker_id": worker_id,
                "products_processed": 0,
                "errors": 0,
                "start_time": time.time()
            }
            
            products, temp_dir = self.create_test_products(products_per_worker)
            
            for i, product in enumerate(products):
                try:
                    result = engine.process_product(product)
                    if result:
                        worker_results["products_processed"] += 1
                except Exception:
                    worker_results["errors"] += 1
            
            worker_results["end_time"] = time.time()
            worker_results["duration"] = worker_results["end_time"] - worker_results["start_time"]
            
            # Cleanup
            shutil.rmtree(temp_dir)
            
            return worker_results
        
        start_time = time.time()
        
        with ThreadPoolExecutor(max_workers=num_workers) as executor:
            futures = [executor.submit(worker_function, i) for i in range(num_workers)]
            worker_results = [future.result() for future in as_completed(futures)]
        
        end_time = time.time()
        total_duration = end_time - start_time
        
        total_products = sum(r["products_processed"] for r in worker_results)
        total_errors = sum(r["errors"] for r in worker_results)
        
        return {
            "test_name": "concurrent_processing_stress",
            "num_workers": num_workers,
            "products_per_worker": products_per_worker,
            "total_products_processed": total_products,
            "total_errors": total_errors,
            "total_duration": total_duration,
            "throughput": total_products / total_duration,
            "worker_results": worker_results
        }
    
    def run_memory_leak_test(self, engine, duration=300):
        """Test for memory leaks during extended operation."""
        print(f"🔥 Running memory leak test ({duration} seconds)")
        
        start_time = time.time()
        initial_memory = psutil.Process().memory_info().rss / 1024 / 1024  # MB
        memory_samples = [initial_memory]
        
        iteration = 0
        while time.time() - start_time < duration:
            products, temp_dir = self.create_test_products(5)
            
            try:
                for product in products:
                    engine.process_product(product)
                    iteration += 1
            except Exception:
                pass
            
            # Sample memory every 30 seconds
            if iteration % 50 == 0:
                current_memory = psutil.Process().memory_info().rss / 1024 / 1024
                memory_samples.append(current_memory)
                print(f"  Memory usage: {current_memory:.1f} MB (iteration {iteration})")
            
            # Cleanup
            shutil.rmtree(temp_dir)
        
        final_memory = psutil.Process().memory_info().rss / 1024 / 1024
        memory_increase = final_memory - initial_memory
        
        return {
            "test_name": "memory_leak_test",
            "duration": duration,
            "iterations": iteration,
            "initial_memory_mb": initial_memory,
            "final_memory_mb": final_memory,
            "memory_increase_mb": memory_increase,
            "memory_samples": memory_samples,
            "potential_leak": memory_increase > 100  # Flag if memory increased by >100MB
        }
    
    def run_all_stress_tests(self):
        """Run all stress tests."""
        print("🚀 Starting SEA-E Stress Test Suite")
        print("=" * 60)
        
        # Setup test engine
        engine, engine_temp_dir = self.setup_test_engine()
        if not engine:
            print("❌ Failed to setup test engine")
            return
        
        # Start system monitoring
        monitoring_thread = threading.Thread(
            target=lambda: self.results.update({"system_monitoring": self.monitor_system_resources(600)}),
            daemon=True
        )
        monitoring_thread.start()
        
        try:
            # Run stress tests
            self.results["single_product_stress"] = self.stress_test_single_product_processing(engine, 500)
            self.results["batch_processing_stress"] = self.stress_test_batch_processing(engine, 25, 5)
            self.results["concurrent_processing_stress"] = self.stress_test_concurrent_processing(engine, 3, 10)
            self.results["memory_leak_test"] = self.run_memory_leak_test(engine, 180)
            
        except Exception as e:
            print(f"❌ Stress test error: {e}")
        
        finally:
            # Cleanup
            if engine_temp_dir:
                shutil.rmtree(engine_temp_dir)
        
        # Wait for monitoring to complete
        monitoring_thread.join(timeout=10)
        
        # Generate report
        self.generate_stress_test_report()
    
    def generate_stress_test_report(self):
        """Generate comprehensive stress test report."""
        total_duration = time.time() - self.start_time
        
        report = {
            "timestamp": datetime.now().isoformat(),
            "total_duration": total_duration,
            "test_results": self.results
        }
        
        # Save JSON report
        json_file = self.output_dir / "stress_test_report.json"
        with open(json_file, 'w') as f:
            json.dump(report, f, indent=2)
        
        # Generate markdown report
        md_file = self.output_dir / "stress_test_report.md"
        with open(md_file, 'w') as f:
            f.write("# SEA-E Stress Test Report\n\n")
            f.write(f"**Generated:** {report['timestamp']}\n")
            f.write(f"**Total Duration:** {total_duration:.2f} seconds\n\n")
            
            for test_name, result in self.results.items():
                if test_name == "system_monitoring":
                    continue
                
                f.write(f"## {result.get('test_name', test_name).replace('_', ' ').title()}\n\n")
                
                if test_name == "single_product_stress":
                    f.write(f"- **Iterations:** {result['iterations']}\n")
                    f.write(f"- **Successful:** {result['successful_iterations']}\n")
                    f.write(f"- **Error Rate:** {result['error_rate']:.2%}\n")
                    f.write(f"- **Throughput:** {result['throughput']:.2f} products/second\n")
                    f.write(f"- **Avg Time per Product:** {result['avg_time_per_iteration']:.3f} seconds\n\n")
                
                elif test_name == "batch_processing_stress":
                    f.write(f"- **Batches:** {result['num_batches']}\n")
                    f.write(f"- **Batch Size:** {result['batch_size']}\n")
                    f.write(f"- **Total Products:** {result['total_products']}\n")
                    f.write(f"- **Successful Batches:** {result['successful_batches']}\n")
                    f.write(f"- **Throughput:** {result['throughput']:.2f} products/second\n\n")
                
                elif test_name == "concurrent_processing_stress":
                    f.write(f"- **Workers:** {result['num_workers']}\n")
                    f.write(f"- **Products per Worker:** {result['products_per_worker']}\n")
                    f.write(f"- **Total Products:** {result['total_products_processed']}\n")
                    f.write(f"- **Total Errors:** {result['total_errors']}\n")
                    f.write(f"- **Throughput:** {result['throughput']:.2f} products/second\n\n")
                
                elif test_name == "memory_leak_test":
                    f.write(f"- **Duration:** {result['duration']} seconds\n")
                    f.write(f"- **Iterations:** {result['iterations']}\n")
                    f.write(f"- **Initial Memory:** {result['initial_memory_mb']:.1f} MB\n")
                    f.write(f"- **Final Memory:** {result['final_memory_mb']:.1f} MB\n")
                    f.write(f"- **Memory Increase:** {result['memory_increase_mb']:.1f} MB\n")
                    f.write(f"- **Potential Leak:** {'⚠️ Yes' if result['potential_leak'] else '✅ No'}\n\n")
        
        print(f"\n📊 Stress test reports generated:")
        print(f"- JSON: {json_file}")
        print(f"- Markdown: {md_file}")


def main():
    """Main function."""
    if len(sys.argv) > 1:
        output_dir = sys.argv[1]
    else:
        output_dir = "reports"
    
    runner = StressTestRunner(output_dir)
    runner.run_all_stress_tests()


if __name__ == "__main__":
    main()
