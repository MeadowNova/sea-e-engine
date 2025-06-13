#!/usr/bin/env python3
"""
SEA-E Integration Test Runner

Comprehensive test runner for all integration test suites with reporting.
"""

import os
import sys
import subprocess
import json
import time
from pathlib import Path
from datetime import datetime


def run_test_suite(test_file, markers=None, output_file=None):
    """Run a specific test suite and capture results."""
    cmd = [
        sys.executable, "-m", "pytest",
        test_file,
        "-v",
        "--tb=short",
        "--durations=10"
    ]
    
    if markers:
        cmd.extend(["-m", markers])
    
    if output_file:
        cmd.extend(["--junitxml", output_file])
    
    print(f"\n{'='*60}")
    print(f"Running: {test_file}")
    if markers:
        print(f"Markers: {markers}")
    print(f"{'='*60}")
    
    start_time = time.time()
    result = subprocess.run(cmd, capture_output=True, text=True)
    end_time = time.time()
    
    return {
        "test_file": test_file,
        "markers": markers,
        "duration": end_time - start_time,
        "return_code": result.returncode,
        "stdout": result.stdout,
        "stderr": result.stderr,
        "success": result.returncode == 0
    }


def generate_report(results, output_dir):
    """Generate comprehensive test report."""
    report_data = {
        "timestamp": datetime.now().isoformat(),
        "total_suites": len(results),
        "successful_suites": sum(1 for r in results if r["success"]),
        "failed_suites": sum(1 for r in results if not r["success"]),
        "total_duration": sum(r["duration"] for r in results),
        "results": results
    }
    
    # Generate JSON report
    json_report = output_dir / "integration_test_report.json"
    with open(json_report, 'w') as f:
        json.dump(report_data, f, indent=2)
    
    # Generate Markdown report
    md_report = output_dir / "integration_test_report.md"
    with open(md_report, 'w') as f:
        f.write("# SEA-E Integration Test Report\n\n")
        f.write(f"**Generated:** {report_data['timestamp']}\n\n")
        
        f.write("## Summary\n\n")
        f.write(f"- **Total Test Suites:** {report_data['total_suites']}\n")
        f.write(f"- **Successful:** {report_data['successful_suites']}\n")
        f.write(f"- **Failed:** {report_data['failed_suites']}\n")
        f.write(f"- **Total Duration:** {report_data['total_duration']:.2f} seconds\n")
        f.write(f"- **Success Rate:** {(report_data['successful_suites']/report_data['total_suites']*100):.1f}%\n\n")
        
        f.write("## Test Suite Results\n\n")
        for result in results:
            status = "✅ PASSED" if result["success"] else "❌ FAILED"
            f.write(f"### {Path(result['test_file']).name} {status}\n\n")
            f.write(f"- **Duration:** {result['duration']:.2f} seconds\n")
            f.write(f"- **Return Code:** {result['return_code']}\n")
            if result["markers"]:
                f.write(f"- **Markers:** {result['markers']}\n")
            f.write("\n")
            
            if result["stdout"]:
                f.write("**Output:**\n```\n")
                f.write(result["stdout"][:1000])  # Limit output length
                if len(result["stdout"]) > 1000:
                    f.write("\n... (truncated)")
                f.write("\n```\n\n")
            
            if result["stderr"] and not result["success"]:
                f.write("**Errors:**\n```\n")
                f.write(result["stderr"][:1000])  # Limit error length
                if len(result["stderr"]) > 1000:
                    f.write("\n... (truncated)")
                f.write("\n```\n\n")
    
    return json_report, md_report


def main():
    """Main test runner function."""
    # Change to project directory
    project_dir = Path(__file__).parent.parent
    os.chdir(project_dir)
    
    # Activate virtual environment
    venv_activate = project_dir / "venv_integration" / "bin" / "activate"
    if venv_activate.exists():
        # Source the virtual environment
        activate_cmd = f"source {venv_activate} && "
    else:
        activate_cmd = ""
    
    # Create reports directory
    reports_dir = project_dir / "reports"
    reports_dir.mkdir(exist_ok=True)
    
    # Define test suites
    test_suites = [
        {
            "file": "tests/integration/test_real_apis.py",
            "markers": "integration and not slow",
            "description": "Real API Integration Tests (Fast)"
        },
        {
            "file": "tests/integration/test_e2e_workflow.py", 
            "markers": "e2e and not slow",
            "description": "End-to-End Workflow Tests (Fast)"
        },
        {
            "file": "tests/integration/test_edge_cases.py",
            "markers": "edge",
            "description": "Edge Cases and Failure Scenarios"
        },
        {
            "file": "tests/integration/test_prod_readiness.py",
            "markers": "prod",
            "description": "Production Readiness Tests"
        },
        {
            "file": "tests/integration/test_stress.py",
            "markers": "stress and not slow and not benchmark",
            "description": "Stress Tests (Fast)"
        }
    ]
    
    print("SEA-E Integration Test Runner")
    print("=" * 60)
    print(f"Project Directory: {project_dir}")
    print(f"Reports Directory: {reports_dir}")
    print(f"Test Suites: {len(test_suites)}")
    
    results = []
    
    for suite in test_suites:
        print(f"\n🧪 {suite['description']}")
        
        # Create output file for this suite
        output_file = reports_dir / f"{Path(suite['file']).stem}_results.xml"
        
        result = run_test_suite(
            suite["file"],
            suite["markers"],
            str(output_file)
        )
        
        results.append(result)
        
        # Print immediate result
        status = "✅ PASSED" if result["success"] else "❌ FAILED"
        print(f"Result: {status} ({result['duration']:.2f}s)")
    
    # Generate comprehensive report
    print(f"\n📊 Generating reports...")
    json_report, md_report = generate_report(results, reports_dir)
    
    print(f"\n📋 Test Summary:")
    print(f"Total Suites: {len(results)}")
    print(f"Passed: {sum(1 for r in results if r['success'])}")
    print(f"Failed: {sum(1 for r in results if not r['success'])}")
    print(f"Total Duration: {sum(r['duration'] for r in results):.2f}s")
    
    print(f"\n📄 Reports Generated:")
    print(f"- JSON: {json_report}")
    print(f"- Markdown: {md_report}")
    
    # Return appropriate exit code
    all_passed = all(r["success"] for r in results)
    if all_passed:
        print(f"\n🎉 All integration tests passed!")
        return 0
    else:
        print(f"\n⚠️  Some integration tests failed!")
        return 1


if __name__ == "__main__":
    sys.exit(main())
