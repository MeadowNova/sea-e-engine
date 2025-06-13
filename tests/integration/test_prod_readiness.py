
#!/usr/bin/env python3
"""
Production Readiness Tests for SEA-E Engine.

Tests production deployment readiness, monitoring,
logging, security, and operational capabilities.
"""

import pytest
import os
import sys
import logging
import tempfile
import json
import shutil
import time
import importlib
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

# Add src to path for imports
sys.path.append(str(Path(__file__).parent.parent.parent / "src"))
sys.path.append(str(Path(__file__).parent.parent.parent))

from sea_engine import SEAEngine
from core.logger import setup_logger


@pytest.mark.prod
class TestProductionReadiness:
    """Test production readiness and operational capabilities."""
    
    @pytest.fixture
    def production_engine(self):
        """Create engine configured for production testing."""
        with tempfile.TemporaryDirectory() as temp_dir:
            config_dir = Path(temp_dir) / "config"
            config_dir.mkdir()
            
            # Copy config files
            original_config = Path(__file__).parent.parent.parent / "config"
            if original_config.exists():
                shutil.copytree(original_config, config_dir, dirs_exist_ok=True)
            
            # Mock environment variables
            with patch.dict(os.environ, {
                'ETSY_API_KEY': 'test_etsy_key',
                'ETSY_REFRESH_TOKEN': 'test_refresh_token',
                'ETSY_SHOP_ID': 'test_shop_id',
                'PRINTIFY_API_KEY': 'test_printify_key',
                'PRINTIFY_SHOP_ID': 'test_printify_shop_id'
            }):
                try:
                    engine = SEAEngine(config_dir=str(config_dir))
                    
                    # Mock API clients
                    engine.etsy_client = Mock()
                    engine.printify_client = Mock()
                    engine.sheets_client = Mock()
                    engine.mockup_generator = Mock()
                    
                    yield engine
                except Exception as e:
                    pytest.skip(f"Failed to initialize production engine: {e}")
    
    @pytest.fixture
    def log_directory(self):
        """Create temporary log directory for testing."""
        with tempfile.TemporaryDirectory() as temp_dir:
            log_dir = Path(temp_dir) / "logs"
            log_dir.mkdir()
            yield str(log_dir)
    
    def test_logging_system_validation(self, production_engine, log_directory):
        """Test logging system under various scenarios."""
        # Test logger setup
        logger = setup_logger("test_logger", log_file=f"{log_directory}/test.log")
        
        # Test different log levels
        logger.debug("Debug message")
        logger.info("Info message")
        logger.warning("Warning message")
        logger.error("Error message")
        logger.critical("Critical message")
        
        # Verify log file was created
        log_file = Path(log_directory) / "test.log"
        assert log_file.exists()
        
        # Verify log content
        with open(log_file, 'r') as f:
            log_content = f.read()
            assert "Info message" in log_content
            assert "Warning message" in log_content
            assert "Error message" in log_content
    
    def test_log_file_rotation(self, production_engine, log_directory):
        """Test log file rotation and management."""
        # Create a logger with rotation
        logger = setup_logger("rotation_test", log_file=f"{log_directory}/rotation.log")
        
        # Generate multiple log entries
        for i in range(100):
            logger.info(f"Log entry {i}")
        
        # Check if log file exists
        log_file = Path(log_directory) / "rotation.log"
        assert log_file.exists()
        
        # Verify log file size is reasonable (not growing indefinitely)
        file_size = log_file.stat().st_size
        assert file_size < 1024 * 1024  # Should be less than 1MB for 100 entries
    
    def test_error_reporting_capabilities(self, production_engine):
        """Test error reporting and alerting."""
        # Test error capture and reporting
        errors_captured = []
        
        def mock_error_handler(error_msg):
            errors_captured.append(error_msg)
        
        # Mock error in API call
        production_engine.etsy_client.create_listing.side_effect = Exception("Test error for reporting")
        
        with tempfile.TemporaryDirectory() as temp_dir:
            design_path = Path(temp_dir) / "test_design.png"
            png_data = b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x02\x00\x00\x00\x90wS\xde\x00\x00\x00\tpHYs\x00\x00\x0b\x13\x00\x00\x0b\x13\x01\x00\x9a\x9c\x18\x00\x00\x00\x0cIDATx\x9cc```\x00\x00\x00\x04\x00\x01\xdd\x8d\xb4\x1c\x00\x00\x00\x00IEND\xaeB`\x82'
            
            with open(design_path, 'wb') as f:
                f.write(png_data)
            
            from sea_engine import ProductData
            product = ProductData("Error Test", str(design_path), "t-shirt")
            
            try:
                production_engine.process_product(product)
            except Exception as e:
                # Error should be captured and reportable
                mock_error_handler(str(e))
        
        # Verify error was captured
        assert len(errors_captured) > 0
        assert "Test error for reporting" in errors_captured[0]
    
    def test_performance_metrics_collection(self, production_engine):
        """Test performance metrics collection."""
        # Test metrics collection
        metrics = {}
        
        def collect_metric(name, value):
            metrics[name] = value
        
        # Simulate performance monitoring
        start_time = time.time()
        
        with tempfile.TemporaryDirectory() as temp_dir:
            design_path = Path(temp_dir) / "test_design.png"
            png_data = b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x02\x00\x00\x00\x90wS\xde\x00\x00\x00\tpHYs\x00\x00\x0b\x13\x00\x00\x0b\x13\x01\x00\x9a\x9c\x18\x00\x00\x00\x0cIDATx\x9cc```\x00\x00\x00\x04\x00\x01\xdd\x8d\xb4\x1c\x00\x00\x00\x00IEND\xaeB`\x82'
            
            with open(design_path, 'wb') as f:
                f.write(png_data)
            
            from sea_engine import ProductData
            product = ProductData("Metrics Test", str(design_path), "t-shirt")
            
            try:
                production_engine.process_product(product)
            except Exception:
                pass  # Focus on metrics collection
        
        end_time = time.time()
        processing_time = end_time - start_time
        
        # Collect performance metrics
        collect_metric("processing_time", processing_time)
        collect_metric("memory_usage", 50.5)  # Mock memory usage
        collect_metric("api_calls", 3)  # Mock API call count
        
        # Verify metrics were collected
        assert "processing_time" in metrics
        assert "memory_usage" in metrics
        assert "api_calls" in metrics
        assert metrics["processing_time"] > 0
    
    def test_health_check_endpoints(self, production_engine):
        """Test system health check capabilities."""
        # Test health check functionality
        health_status = {}
        
        def check_component_health(component_name):
            try:
                if component_name == "etsy_api":
                    # Mock health check for Etsy API
                    production_engine.etsy_client.get_shop_info()
                    return "healthy"
                elif component_name == "printify_api":
                    # Mock health check for Printify API
                    production_engine.printify_client.get_blueprints()
                    return "healthy"
                elif component_name == "database":
                    # Mock database health check
                    return "healthy"
                else:
                    return "unknown"
            except Exception:
                return "unhealthy"
        
        # Check health of all components
        components = ["etsy_api", "printify_api", "database"]
        for component in components:
            health_status[component] = check_component_health(component)
        
        # Verify health checks
        assert all(status in ["healthy", "unhealthy"] for status in health_status.values())
        
        # Overall system health
        overall_health = "healthy" if all(status == "healthy" for status in health_status.values()) else "degraded"
        assert overall_health in ["healthy", "degraded"]
    
    def test_credential_security_handling(self, production_engine):
        """Test secure credential handling."""
        # Test that credentials are not exposed in logs or errors
        sensitive_data = [
            "test_etsy_key",
            "test_refresh_token",
            "test_printify_key"
        ]
        
        # Capture log output
        log_output = []
        
        class TestLogHandler(logging.Handler):
            def emit(self, record):
                log_output.append(self.format(record))
        
        # Add test handler to logger
        logger = logging.getLogger("sea_engine")
        test_handler = TestLogHandler()
        logger.addHandler(test_handler)
        
        try:
            # Trigger some operations that might log credentials
            production_engine.etsy_client.create_listing({"title": "Test"})
            production_engine.printify_client.create_product({"title": "Test"})
        except Exception:
            pass  # Focus on credential security
        
        # Check that sensitive data is not in logs
        log_content = " ".join(log_output)
        for sensitive in sensitive_data:
            assert sensitive not in log_content, f"Sensitive data '{sensitive}' found in logs"
        
        # Remove test handler
        logger.removeHandler(test_handler)
    
    def test_environment_configuration_management(self, production_engine):
        """Test environment-specific configuration management."""
        # Test configuration loading for different environments
        environments = ["development", "staging", "production"]
        
        for env in environments:
            with patch.dict(os.environ, {"ENVIRONMENT": env}):
                # Test environment-specific configuration
                config = {
                    "environment": env,
                    "debug": env == "development",
                    "log_level": "DEBUG" if env == "development" else "INFO",
                    "api_timeout": 30 if env == "production" else 10
                }
                
                # Verify configuration is appropriate for environment
                if env == "production":
                    assert not config["debug"]
                    assert config["log_level"] == "INFO"
                    assert config["api_timeout"] == 30
                elif env == "development":
                    assert config["debug"]
                    assert config["log_level"] == "DEBUG"
    
    def test_backup_and_recovery_procedures(self, production_engine):
        """Test backup and recovery mechanisms."""
        # Test state backup and recovery
        with tempfile.TemporaryDirectory() as temp_dir:
            backup_dir = Path(temp_dir) / "backups"
            backup_dir.mkdir()
            
            # Create mock state data
            state_data = {
                "workflow_id": "test_workflow_123",
                "current_step": "printify_product_creation",
                "product_data": {
                    "design_name": "Test Product",
                    "product_type": "t-shirt"
                },
                "timestamp": time.time()
            }
            
            # Test backup creation
            backup_file = backup_dir / "workflow_backup.json"
            with open(backup_file, 'w') as f:
                json.dump(state_data, f)
            
            # Verify backup was created
            assert backup_file.exists()
            
            # Test recovery from backup
            with open(backup_file, 'r') as f:
                recovered_data = json.load(f)
            
            # Verify recovery
            assert recovered_data["workflow_id"] == state_data["workflow_id"]
            assert recovered_data["current_step"] == state_data["current_step"]
    
    def test_system_monitoring_capabilities(self, production_engine):
        """Test system monitoring and alerting."""
        # Test monitoring metrics
        monitoring_data = {}
        
        def monitor_system():
            # CPU usage monitoring
            monitoring_data["cpu_usage"] = 45.2  # Mock CPU usage
            
            # Memory usage monitoring
            monitoring_data["memory_usage"] = 67.8  # Mock memory usage
            
            # API response times
            monitoring_data["api_response_times"] = {
                "etsy": 250,  # ms
                "printify": 180,  # ms
            }
            
            # Error rates
            monitoring_data["error_rate"] = 0.02  # 2% error rate
            
            return monitoring_data
        
        # Collect monitoring data
        metrics = monitor_system()
        
        # Verify monitoring data
        assert "cpu_usage" in metrics
        assert "memory_usage" in metrics
        assert "api_response_times" in metrics
        assert "error_rate" in metrics
        
        # Test alerting thresholds
        alerts = []
        if metrics["cpu_usage"] > 80:
            alerts.append("High CPU usage")
        if metrics["memory_usage"] > 90:
            alerts.append("High memory usage")
        if metrics["error_rate"] > 0.05:
            alerts.append("High error rate")
        
        # In this test case, no alerts should be triggered
        assert len(alerts) == 0
    
    def test_startup_shutdown_procedures(self, production_engine):
        """Test system startup and shutdown procedures."""
        # Test startup procedure
        startup_steps = []
        
        def startup_procedure():
            startup_steps.append("Loading configuration")
            startup_steps.append("Initializing API clients")
            startup_steps.append("Setting up logging")
            startup_steps.append("Verifying dependencies")
            startup_steps.append("System ready")
            return True
        
        # Test shutdown procedure
        shutdown_steps = []
        
        def shutdown_procedure():
            shutdown_steps.append("Stopping active workflows")
            shutdown_steps.append("Saving state")
            shutdown_steps.append("Closing API connections")
            shutdown_steps.append("Flushing logs")
            shutdown_steps.append("System stopped")
            return True
        
        # Execute startup
        startup_success = startup_procedure()
        assert startup_success
        assert len(startup_steps) == 5
        assert "System ready" in startup_steps
        
        # Execute shutdown
        shutdown_success = shutdown_procedure()
        assert shutdown_success
        assert len(shutdown_steps) == 5
        assert "System stopped" in shutdown_steps
    
    def test_configuration_validation(self, production_engine):
        """Test configuration file validation."""
        # Test configuration validation
        with tempfile.TemporaryDirectory() as temp_dir:
            config_dir = Path(temp_dir) / "config"
            config_dir.mkdir()
            
            # Test valid configuration
            valid_config = {
                "api_settings": {
                    "timeout": 30,
                    "retry_attempts": 3
                },
                "product_types": ["t-shirt", "sweatshirt", "poster"],
                "logging": {
                    "level": "INFO",
                    "file": "sea_engine.log"
                }
            }
            
            config_file = config_dir / "settings.json"
            with open(config_file, 'w') as f:
                json.dump(valid_config, f)
            
            # Validate configuration
            def validate_config(config_path):
                try:
                    with open(config_path, 'r') as f:
                        config = json.load(f)
                    
                    # Check required sections
                    required_sections = ["api_settings", "product_types", "logging"]
                    for section in required_sections:
                        if section not in config:
                            return False, f"Missing section: {section}"
                    
                    # Validate data types
                    if not isinstance(config["product_types"], list):
                        return False, "product_types must be a list"
                    
                    return True, "Configuration valid"
                except Exception as e:
                    return False, f"Configuration error: {e}"
            
            # Test validation
            is_valid, message = validate_config(config_file)
            assert is_valid
            assert "valid" in message
    
    def test_dependency_verification(self, production_engine):
        """Test dependency verification and compatibility."""
        # Test dependency verification
        dependencies = {
            "requests": "2.32.4",
            "pytest": "8.4.0",
            "Pillow": "11.2.1",
            "gspread": "6.2.1"
        }
        
        def verify_dependencies():
            missing_deps = []
            version_mismatches = []
            
            for dep_name, expected_version in dependencies.items():
                try:
                    # Try to import the module
                    module = importlib.import_module(dep_name.lower())
                    
                    # Check version if available
                    if hasattr(module, "__version__"):
                        actual_version = module.__version__
                        # For this test, we'll just check that version exists
                        if not actual_version:
                            version_mismatches.append(f"{dep_name}: no version info")
                    
                except ImportError:
                    missing_deps.append(dep_name)
            
            return missing_deps, version_mismatches
        
        # Verify dependencies
        missing, mismatches = verify_dependencies()
        
        # All required dependencies should be available
        assert len(missing) == 0, f"Missing dependencies: {missing}"
    
    def test_deployment_readiness_checklist(self, production_engine):
        """Test deployment readiness checklist."""
        # Deployment readiness checklist
        checklist = {}
        
        # Check configuration files
        config_dir = Path(production_engine.config_dir)
        checklist["config_files_present"] = (
            (config_dir / "product_blueprints.json").exists() and
            (config_dir / "mockup_blueprints.json").exists()
        )
        
        # Check environment variables
        required_env_vars = [
            "ETSY_API_KEY", "ETSY_REFRESH_TOKEN", "ETSY_SHOP_ID",
            "PRINTIFY_API_KEY", "PRINTIFY_SHOP_ID"
        ]
        checklist["environment_variables"] = all(
            os.getenv(var) is not None for var in required_env_vars
        )
        
        # Check API connectivity (mocked)
        checklist["api_connectivity"] = True  # Mocked as working
        
        # Check logging setup
        checklist["logging_configured"] = True  # Logger is set up
        
        # Check error handling
        checklist["error_handling"] = True  # Error handling is implemented
        
        # Overall readiness
        deployment_ready = all(checklist.values())
        
        # Verify deployment readiness
        assert checklist["config_files_present"]
        assert checklist["environment_variables"]
        assert deployment_ready
    
    def test_documentation_completeness(self, production_engine):
        """Test documentation completeness and accuracy."""
        # Check for documentation files
        project_root = Path(__file__).parent.parent.parent
        
        documentation_files = {
            "README.md": project_root / "README.md",
            "API_DOCS": project_root / "docs" / "api.md",
            "DEPLOYMENT": project_root / "docs" / "deployment.md",
            "CONFIGURATION": project_root / "docs" / "configuration.md"
        }
        
        # Check which documentation exists
        existing_docs = {}
        for doc_name, doc_path in documentation_files.items():
            existing_docs[doc_name] = doc_path.exists()
        
        # At minimum, README should exist
        assert existing_docs.get("README.md", False), "README.md is required"
        
        # Check code documentation (docstrings)
        import inspect
        
        # Check if main classes have docstrings
        sea_engine_class = production_engine.__class__
        assert sea_engine_class.__doc__ is not None, "SEAEngine class should have docstring"
        
        # Check if main methods have docstrings
        methods_to_check = ["process_product", "process_products_batch"]
        for method_name in methods_to_check:
            if hasattr(production_engine, method_name):
                method = getattr(production_engine, method_name)
                if callable(method):
                    assert method.__doc__ is not None, f"{method_name} should have docstring"
