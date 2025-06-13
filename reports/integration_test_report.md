# SEA-E Integration Test Report

**Generated:** 2025-06-11T23:57:57.550902

## Summary

- **Total Test Suites:** 5
- **Successful:** 5
- **Failed:** 0
- **Total Duration:** 7.04 seconds
- **Success Rate:** 100.0%

## Test Suite Results

### test_real_apis.py ✅ PASSED

- **Duration:** 1.40 seconds
- **Return Code:** 0
- **Markers:** integration and not slow

**Output:**
```
============================= test session starts ==============================
platform linux -- Python 3.11.6, pytest-8.4.0, pluggy-1.6.0 -- /home/ubuntu/sea-engine/venv_integration/bin/python
cachedir: .pytest_cache
benchmark: 5.1.0 (defaults: timer=time.perf_counter disable_gc=False min_rounds=5 min_time=0.000005 max_time=1.0 calibration_precision=10 warmup=False warmup_iterations=100000)
rootdir: /home/ubuntu/sea-engine
configfile: pytest.ini
plugins: requests-mock-1.12.1, benchmark-5.1.0, asyncio-1.0.0, mock-3.14.1
asyncio: mode=Mode.STRICT, asyncio_default_fixture_loop_scope=None, asyncio_default_test_loop_scope=function
collecting ... collected 14 items / 2 deselected / 12 selected

tests/integration/test_real_apis.py::TestRealAPIIntegration::test_etsy_authentication_renewal SKIPPED [  8%]
tests/integration/test_real_apis.py::TestRealAPIIntegration::test_etsy_rate_limiting_compliance SKIPPED [ 16%]
tests/integration/test_real_apis.py::TestRealAPIIntegration::test_etsy_error_ha
... (truncated)
```

### test_e2e_workflow.py ✅ PASSED

- **Duration:** 1.35 seconds
- **Return Code:** 0
- **Markers:** e2e and not slow

**Output:**
```
============================= test session starts ==============================
platform linux -- Python 3.11.6, pytest-8.4.0, pluggy-1.6.0 -- /home/ubuntu/sea-engine/venv_integration/bin/python
cachedir: .pytest_cache
benchmark: 5.1.0 (defaults: timer=time.perf_counter disable_gc=False min_rounds=5 min_time=0.000005 max_time=1.0 calibration_precision=10 warmup=False warmup_iterations=100000)
rootdir: /home/ubuntu/sea-engine
configfile: pytest.ini
plugins: requests-mock-1.12.1, benchmark-5.1.0, asyncio-1.0.0, mock-3.14.1
asyncio: mode=Mode.STRICT, asyncio_default_fixture_loop_scope=None, asyncio_default_test_loop_scope=function
collecting ... collected 10 items / 2 deselected / 8 selected

tests/integration/test_e2e_workflow.py::TestEndToEndWorkflow::test_tshirt_complete_workflow SKIPPED [ 12%]
tests/integration/test_e2e_workflow.py::TestEndToEndWorkflow::test_sweatshirt_complete_workflow SKIPPED [ 25%]
tests/integration/test_e2e_workflow.py::TestEndToEndWorkflow::test_poster_complete
... (truncated)
```

### test_edge_cases.py ✅ PASSED

- **Duration:** 1.47 seconds
- **Return Code:** 0
- **Markers:** edge

**Output:**
```
============================= test session starts ==============================
platform linux -- Python 3.11.6, pytest-8.4.0, pluggy-1.6.0 -- /home/ubuntu/sea-engine/venv_integration/bin/python
cachedir: .pytest_cache
benchmark: 5.1.0 (defaults: timer=time.perf_counter disable_gc=False min_rounds=5 min_time=0.000005 max_time=1.0 calibration_precision=10 warmup=False warmup_iterations=100000)
rootdir: /home/ubuntu/sea-engine
configfile: pytest.ini
plugins: requests-mock-1.12.1, benchmark-5.1.0, asyncio-1.0.0, mock-3.14.1
asyncio: mode=Mode.STRICT, asyncio_default_fixture_loop_scope=None, asyncio_default_test_loop_scope=function
collecting ... collected 14 items

tests/integration/test_edge_cases.py::TestEdgeCasesAndFailures::test_invalid_product_configuration SKIPPED [  7%]
tests/integration/test_edge_cases.py::TestEdgeCasesAndFailures::test_malformed_input_data SKIPPED [ 14%]
tests/integration/test_edge_cases.py::TestEdgeCasesAndFailures::test_missing_required_fields SKIPPED [ 21%]
t
... (truncated)
```

### test_prod_readiness.py ✅ PASSED

- **Duration:** 1.51 seconds
- **Return Code:** 0
- **Markers:** prod

**Output:**
```
============================= test session starts ==============================
platform linux -- Python 3.11.6, pytest-8.4.0, pluggy-1.6.0 -- /home/ubuntu/sea-engine/venv_integration/bin/python
cachedir: .pytest_cache
benchmark: 5.1.0 (defaults: timer=time.perf_counter disable_gc=False min_rounds=5 min_time=0.000005 max_time=1.0 calibration_precision=10 warmup=False warmup_iterations=100000)
rootdir: /home/ubuntu/sea-engine
configfile: pytest.ini
plugins: requests-mock-1.12.1, benchmark-5.1.0, asyncio-1.0.0, mock-3.14.1
asyncio: mode=Mode.STRICT, asyncio_default_fixture_loop_scope=None, asyncio_default_test_loop_scope=function
collecting ... collected 14 items

tests/integration/test_prod_readiness.py::TestProductionReadiness::test_logging_system_validation SKIPPED [  7%]
tests/integration/test_prod_readiness.py::TestProductionReadiness::test_log_file_rotation SKIPPED [ 14%]
tests/integration/test_prod_readiness.py::TestProductionReadiness::test_error_reporting_capabilities SKIPPED [
... (truncated)
```

### test_stress.py ✅ PASSED

- **Duration:** 1.31 seconds
- **Return Code:** 0
- **Markers:** stress and not slow and not benchmark

**Output:**
```
============================= test session starts ==============================
platform linux -- Python 3.11.6, pytest-8.4.0, pluggy-1.6.0 -- /home/ubuntu/sea-engine/venv_integration/bin/python
cachedir: .pytest_cache
benchmark: 5.1.0 (defaults: timer=time.perf_counter disable_gc=False min_rounds=5 min_time=0.000005 max_time=1.0 calibration_precision=10 warmup=False warmup_iterations=100000)
rootdir: /home/ubuntu/sea-engine
configfile: pytest.ini
plugins: requests-mock-1.12.1, benchmark-5.1.0, asyncio-1.0.0, mock-3.14.1
asyncio: mode=Mode.STRICT, asyncio_default_fixture_loop_scope=None, asyncio_default_test_loop_scope=function
collecting ... collected 10 items / 5 deselected / 5 selected

tests/integration/test_stress.py::TestStressAndPerformance::test_memory_usage_under_load SKIPPED [ 20%]
tests/integration/test_stress.py::TestStressAndPerformance::test_concurrent_api_calls SKIPPED [ 40%]
tests/integration/test_stress.py::TestStressAndPerformance::test_rate_limiting_compliance_stres
... (truncated)
```

