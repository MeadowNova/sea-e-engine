
# SEA-E: Scalable E-commerce Automation Engine

[![Python 3.8+](https://i.ytimg.com/vi/7ZUt4S7blGU/hqdefault.jpg)
[![License: MIT](https://blogger.googleusercontent.com/img/b/R29vZ2xl/AVvXsEjcFTvVoyHXTT89PUxo5h-J5QYf2jb49mq9hDaMtjMzA9SX62qhK7HmiGm7O8XfpWA_MLwpqFYWIHmyNw_Xp89gHcQowcJloLQLxSbgNdMK15kLWUS_arqjiZNwy2iYj5wHx4wrjijG3P65/s1600/MIT.PNG)
[![Production Ready](https://i.pinimg.com/originals/28/a1/a5/28a1a51729b0127332ce83948be2bce6.png)

## 🚀 Overview

SEA-E (Scalable E-commerce Automation Engine) is a production-ready automation system that streamlines the entire e-commerce product lifecycle from design concept to marketplace publication. Built with enterprise-grade reliability, SEA-E integrates with Airtable, Etsy, and Printify to automate product creation, mockup generation, and listing management.

### Key Features

- **Complete Workflow Automation**: Automate the entire product lifecycle from design to publication
- **Airtable Integration**: Relational database backend with 6 interconnected tables
- **Multi-Platform Support**: Seamless integration with Etsy and Printify APIs
- **Batch Processing**: Handle multiple products efficiently with parallel processing
- **Enterprise Reliability**: Comprehensive error handling, retry mechanisms, and logging
- **State Management**: Track and recover from any point in the workflow
- **Configuration-Driven**: Flexible manifest system for different product campaigns

### System Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Airtable      │    │   SEA-E Engine  │    │   Marketplaces  │
│   Database      │◄──►│   Orchestrator  │◄──►│   (Etsy, etc.)  │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Collections   │    │   Workflow      │    │   Print-on-     │
│   Products      │    │   Management    │    │   Demand        │
│   Variations    │    │   State Engine  │    │   (Printify)    │
│   Mockups       │    │                 │    │                 │
│   Listings      │    │                 │    │                 │
│   Dashboard     │    │                 │    │                 │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

### Workflow Stages

SEA-E manages products through a 5-stage workflow:

1. **Design** → Initial product concept and design assets
2. **Mockup** → Generate product mockups and previews
3. **Product** → Create print-on-demand products
4. **Listed** → Generate marketplace listings
5. **Published** → Publish to live marketplaces

## 📋 System Requirements

### Software Requirements

- **Python**: 3.8 or higher
- **Operating System**: Linux, macOS, or Windows
- **Memory**: Minimum 2GB RAM (4GB recommended)
- **Storage**: 1GB free space for logs and temporary files

### API Account Requirements

You'll need active accounts and API access for:

- **Airtable**: Personal Access Token and Base ID
- **Etsy**: API Key, Secret, Access Token, and Shop ID
- **Printify**: API Key and Shop ID

### Python Dependencies

All dependencies are managed through `requirements.txt`:

```bash
# Core dependencies
requests>=2.31.0
python-dotenv>=1.0.0
Pillow>=10.0.0
pandas>=2.1.0
colorlog>=6.7.0
httpx>=0.25.0
pyyaml>=6.0.1

# Development and testing
pytest>=7.4.0
pytest-cov>=4.1.0
black>=23.9.0
flake8>=6.1.0
```

## 🛠️ Installation Guide

### 1. Clone the Repository

```bash
git clone https://github.com/your-repo/sea-engine.git
cd sea-engine
```

### 2. Set Up Python Virtual Environment

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Linux/macOS:
source venv/bin/activate
# On Windows:
venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables

```bash
# Copy the example environment file
cp .env.example .env

# Edit the .env file with your API credentials
nano .env  # or use your preferred editor
```

### 5. Verify Installation

```bash
# Test the installation
python run_engine.py --help

# List available manifests
python run_engine.py --list-manifests
```

## ⚙️ Configuration Setup

### Environment Variables

Edit your `.env` file with the following configuration:

```bash
# Printify API Configuration
PRINTIFY_API_KEY=your_printify_api_key_here
PRINTIFY_SHOP_ID=your_printify_shop_id_here

# Etsy API Configuration
ETSY_API_KEY=your_etsy_api_key_here
ETSY_API_SECRET=your_etsy_api_secret_here
ETSY_ACCESS_TOKEN=your_etsy_access_token_here
ETSY_REFRESH_TOKEN=your_etsy_refresh_token_here
ETSY_SHOP_ID=your_etsy_shop_id_here

# Airtable Configuration
AIRTABLE_API_KEY=your_airtable_api_key_here
AIRTABLE_BASE_ID=your_airtable_base_id_here

# Application Configuration
LOG_LEVEL=INFO
ENVIRONMENT=production
```

### API Credential Setup

#### Airtable Setup

1. **Create Airtable Account**: Sign up at [airtable.com](https://airtable.com)
2. **Generate Personal Access Token**:
   - Go to [airtable.com/create/tokens](https://airtable.com/create/tokens)
   - Create a new token with `data.records:read` and `data.records:write` scopes
   - Copy the token to `AIRTABLE_API_KEY`
3. **Get Base ID**:
   - Open your Airtable base
   - Go to Help → API documentation
   - Copy the Base ID from the URL or documentation

#### Etsy API Setup

1. **Create Etsy Developer Account**: Register at [developers.etsy.com](https://developers.etsy.com)
2. **Create New App**:
   - Go to "Your Apps" and click "Create a New App"
   - Fill in app details and get API Key and Secret
3. **Generate Access Tokens**:
   - Use Etsy's OAuth flow to generate access and refresh tokens
   - Store all credentials in your `.env` file

#### Printify API Setup

1. **Create Printify Account**: Sign up at [printify.com](https://printify.com)
2. **Generate API Token**:
   - Go to My Profile → Connections → API
   - Generate a new Personal Access Token
3. **Get Shop ID**:
   - Use the API or check your shop settings for the Shop ID

### Airtable Base Setup

SEA-E requires a specific Airtable base structure with 6 interconnected tables:

#### Table Structure

| Table Name | Purpose | Key Fields |
|------------|---------|------------|
| **Collections** | Product groupings and campaigns | Name, Status, Description, Target Date |
| **Products** | Individual product definitions | Title, Collection, Status, Priority, SKU |
| **Variations** | Product variants (colors, sizes) | Product, Color, Size, Price, Status |
| **Mockups** | Generated product previews | Product, Variation, Image URL, Status |
| **Listings** | Marketplace listing data | Product, Platform, Listing ID, Status |
| **Status Dashboard** | Workflow monitoring | Product, Current Stage, Progress, Issues |

#### Relationships

- Collections → Products (One-to-Many)
- Products → Variations (One-to-Many)
- Products → Mockups (One-to-Many)
- Products → Listings (One-to-Many)
- Products → Status Dashboard (One-to-One)

### Authentication Testing

Verify your API connections:

```bash
# Test with dry-run mode
python run_engine.py --manifest test_manifest --dry-run

# Check logs for authentication status
tail -f logs/sea-engine.log
```

## 🎯 Usage Instructions

### Command-Line Interface

SEA-E provides a comprehensive CLI for all operations:

```bash
# Basic usage
python run_engine.py --manifest <manifest_name>

# Available options
python run_engine.py [options]

Options:
  -h, --help            Show help message and exit
  --manifest MANIFEST   Manifest key to process (from config/manifests.json)
  --dry-run             Run in dry-run mode (no actual API calls)
  --list-manifests      List available manifests and exit
  --log-level LEVEL     Set logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
```

### Common Commands

```bash
# List all available manifests
python run_engine.py --list-manifests

# Run a specific manifest
python run_engine.py --manifest tshirts_q3_launch

# Test run without making API calls
python run_engine.py --manifest posters_q3_launch --dry-run

# Run with debug logging
python run_engine.py --manifest holiday_collection --log-level DEBUG
```

### Workflow Execution Examples

#### Single Product Processing

```bash
# Process a single product collection
python run_engine.py --manifest single_product_test
```

#### Batch Processing

```bash
# Process multiple products in a collection
python run_engine.py --manifest bulk_tshirt_collection

# Large batch with detailed logging
python run_engine.py --manifest seasonal_collection --log-level DEBUG
```

#### Development and Testing

```bash
# Safe testing without API calls
python run_engine.py --manifest development_test --dry-run

# Test specific workflow stages
python run_engine.py --manifest stage_test --log-level DEBUG
```

## 🗄️ Airtable Integration

### Database Schema

SEA-E uses a relational database structure in Airtable with the following tables:

#### Collections Table
- **Purpose**: Group related products into campaigns or collections
- **Key Fields**: Name, Status, Description, Target Launch Date, Product Count
- **Relationships**: Links to multiple Products

#### Products Table
- **Purpose**: Define individual products with metadata
- **Key Fields**: Title, Collection (linked), Status, Priority, SKU, Description
- **Relationships**: Links to Collection, has multiple Variations, Mockups, Listings

#### Variations Table
- **Purpose**: Define product variants (colors, sizes, styles)
- **Key Fields**: Product (linked), Color, Size, Price, Printify Product ID, Status
- **Relationships**: Links to Product, has multiple Mockups

#### Mockups Table
- **Purpose**: Store generated product preview images
- **Key Fields**: Product (linked), Variation (linked), Image URL, Generation Date, Status
- **Relationships**: Links to Product and Variation

#### Listings Table
- **Purpose**: Track marketplace listings and their status
- **Key Fields**: Product (linked), Platform, Listing ID, URL, Status, Publication Date
- **Relationships**: Links to Product

#### Status Dashboard Table
- **Purpose**: Monitor workflow progress and issues
- **Key Fields**: Product (linked), Current Stage, Progress %, Last Updated, Issues
- **Relationships**: Links to Product

### Data Entry Guidelines

#### Creating Collections

1. **Name**: Use descriptive, unique names (e.g., "Summer 2024 T-Shirts")
2. **Status**: Set to "Planning", "Active", or "Inactive"
3. **Description**: Provide clear campaign description
4. **Target Date**: Set realistic launch timeline

#### Adding Products

1. **Title**: Use SEO-friendly product titles
2. **Collection**: Link to appropriate collection
3. **Status**: Start with "Design" status
4. **Priority**: Set based on business importance
5. **SKU**: Use consistent SKU format

#### Managing Variations

1. **Color**: Use standard color names
2. **Size**: Follow platform size standards
3. **Price**: Set competitive pricing
4. **Status**: Mark as "Active" when ready

### Workflow Status Management

Products move through stages automatically:

```
Design → Mockup → Product → Listed → Published
```

Monitor progress in the Status Dashboard table:

- **Current Stage**: Shows workflow position
- **Progress %**: Completion percentage
- **Last Updated**: Timestamp of last activity
- **Issues**: Any errors or warnings

## 🔌 API Integrations

### Etsy API Integration

#### Features
- **Product Creation**: Automatically create Etsy listings
- **Image Upload**: Upload mockup images to listings
- **Inventory Management**: Sync stock levels
- **Order Processing**: Handle order notifications

#### Configuration
```python
# Etsy API settings in .env
ETSY_API_KEY=your_api_key
ETSY_API_SECRET=your_api_secret
ETSY_ACCESS_TOKEN=your_access_token
ETSY_REFRESH_TOKEN=your_refresh_token
ETSY_SHOP_ID=your_shop_id
```

#### Usage Examples
```bash
# Create Etsy listings for a collection
python run_engine.py --manifest etsy_summer_collection

# Update existing listings
python run_engine.py --manifest etsy_inventory_update
```

### Printify API Integration

#### Features
- **Product Creation**: Create print-on-demand products
- **Mockup Generation**: Generate product preview images
- **Variant Management**: Handle colors, sizes, and styles
- **Order Fulfillment**: Automatic order processing

#### Configuration
```python
# Printify API settings in .env
PRINTIFY_API_KEY=your_api_key
PRINTIFY_SHOP_ID=your_shop_id
```

#### Mockup Generation Process

1. **Design Upload**: Upload design files to Printify
2. **Product Creation**: Create products with variants
3. **Mockup Generation**: Generate preview images
4. **Quality Check**: Validate mockup quality
5. **Storage**: Save mockup URLs to Airtable

### Error Handling and Troubleshooting

#### Common API Issues

**Rate Limiting**
- SEA-E includes automatic retry mechanisms
- Exponential backoff prevents API overload
- Monitor logs for rate limit warnings

**Authentication Errors**
```bash
# Test API connections
python run_engine.py --manifest auth_test --dry-run

# Check authentication logs
grep "AUTH" logs/sea-engine.log
```

**Network Issues**
- Automatic retry for transient failures
- Configurable timeout settings
- Detailed error logging

#### Debug Mode

Enable detailed logging for troubleshooting:

```bash
# Run with debug logging
python run_engine.py --manifest problem_collection --log-level DEBUG

# Monitor real-time logs
tail -f logs/sea-engine.log
```

## 🚀 Advanced Features

### Batch Processing Capabilities

#### Parallel Processing
- Process multiple products simultaneously
- Configurable concurrency limits
- Resource-aware processing

#### Bulk Operations
```bash
# Process entire collections
python run_engine.py --manifest bulk_holiday_collection

# Update multiple listings
python run_engine.py --manifest bulk_price_update
```

### Custom Configuration Options

#### Manifest System
Create custom workflows in `config/manifests.json`:

```json
{
  "custom_collection": {
    "name": "Custom Product Collection",
    "description": "Custom workflow configuration",
    "filters": {
      "collection": "Custom Collection",
      "status": "Design"
    },
    "settings": {
      "batch_size": 10,
      "parallel_processing": true,
      "auto_publish": false
    }
  }
}
```

#### Workflow Customization
- Configure stage transitions
- Set custom validation rules
- Define approval workflows

### Performance Optimization Tips

#### Database Optimization
- Use Airtable views for filtering
- Index frequently queried fields
- Limit record sets for large collections

#### API Optimization
- Enable request caching
- Use batch API calls where possible
- Monitor API usage quotas

#### System Resources
```bash
# Monitor system performance
python run_engine.py --manifest large_collection --log-level INFO

# Check memory usage
ps aux | grep python
```

### Monitoring and Logging

#### Log Levels
- **DEBUG**: Detailed execution information
- **INFO**: General operational messages
- **WARNING**: Important notices
- **ERROR**: Error conditions
- **CRITICAL**: Serious failures

#### Log Files
```bash
# Main application log
tail -f logs/sea-engine.log

# Error-specific logs
grep "ERROR" logs/sea-engine.log

# Performance monitoring
grep "PERFORMANCE" logs/sea-engine.log
```

#### Monitoring Dashboard
Access workflow status through Airtable's Status Dashboard table:
- Real-time progress tracking
- Error identification
- Performance metrics

## 🔧 Troubleshooting

### Common Issues and Solutions

#### Installation Issues

**Python Version Compatibility**
```bash
# Check Python version
python --version

# Should be 3.8 or higher
# If not, install correct version
```

**Dependency Conflicts**
```bash
# Clean install dependencies
pip uninstall -r requirements.txt -y
pip install -r requirements.txt
```

**Virtual Environment Issues**
```bash
# Recreate virtual environment
rm -rf venv
python -m venv venv
source venv/bin/activate  # Linux/macOS
pip install -r requirements.txt
```

#### Configuration Issues

**Environment Variables Not Loading**
```bash
# Check .env file exists
ls -la .env

# Verify file format (no spaces around =)
cat .env | grep "="
```

**API Authentication Failures**
```bash
# Test individual API connections
python -c "from src.api.airtable_client import AirtableClient; print('Airtable OK')"
python -c "from src.api.etsy import EtsyAPIClient; print('Etsy OK')"
python -c "from src.api.printify import PrintifyAPIClient; print('Printify OK')"
```

#### Runtime Issues

**Memory Issues**
```bash
# Reduce batch size in manifest
# Monitor memory usage
free -h  # Linux
top -l 1 | grep PhysMem  # macOS
```

**Network Timeouts**
```bash
# Check internet connectivity
ping google.com

# Test API endpoints
curl -I https://api.airtable.com/v0/meta/bases
```

### Error Message Explanations

#### Common Error Patterns

**"Authentication failed"**
- Check API credentials in .env file
- Verify token expiration dates
- Test API access in browser/Postman

**"Rate limit exceeded"**
- Wait for rate limit reset
- Reduce batch processing size
- Check API usage quotas

**"Record not found"**
- Verify Airtable base structure
- Check record IDs and relationships
- Ensure proper table permissions

**"Network connection error"**
- Check internet connectivity
- Verify firewall settings
- Test with --dry-run mode

### Debug Mode Instructions

#### Enable Debug Logging
```bash
# Run with maximum verbosity
python run_engine.py --manifest debug_test --log-level DEBUG

# Save debug output to file
python run_engine.py --manifest debug_test --log-level DEBUG > debug.log 2>&1
```

#### Debug Specific Components
```bash
# Test Airtable connection only
python -c "
from src.api.airtable_client import AirtableClient
client = AirtableClient()
print(client.test_connection())
"

# Test workflow state management
python -c "
from src.workflow.state import WorkflowStateManager
manager = WorkflowStateManager()
print(manager.get_status())
"
```

### Support Resources

#### Documentation
- [Complete Tutorial](TUTORIAL.md) - Step-by-step usage guide
- [Quick Start Guide](QUICKSTART.md) - 5-minute setup
- [API Documentation](docs/) - Detailed API reference

#### Community Support
- GitHub Issues: Report bugs and request features
- Discussions: Community Q&A and best practices
- Wiki: Additional documentation and examples

#### Professional Support
- Enterprise support available
- Custom integration services
- Training and consultation

## 🤝 Contributing and Development

### Development Setup

#### Clone for Development
```bash
git clone https://github.com/your-repo/sea-engine.git
cd sea-engine
git checkout develop
```

#### Install Development Dependencies
```bash
pip install -r requirements-dev.txt
```

#### Pre-commit Hooks
```bash
# Install pre-commit hooks
pre-commit install

# Run code formatting
black .
flake8 .
```

### Testing Procedures

#### Run Test Suite
```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src --cov-report=html

# Run specific test categories
pytest tests/unit/
pytest tests/integration/
pytest tests/performance/
```

#### Test Categories

**Unit Tests**
- Individual component testing
- Mock API responses
- Fast execution

**Integration Tests**
- End-to-end workflow testing
- Real API connections
- Comprehensive validation

**Performance Tests**
- Load testing
- Memory usage validation
- Scalability testing

### Code Structure Explanation

#### Directory Structure
```
sea-engine/
├── src/                    # Source code
│   ├── api/               # API client modules
│   ├── core/              # Core functionality
│   ├── data/              # Data models
│   ├── modules/           # Feature modules
│   ├── services/          # Service integrations
│   └── workflow/          # Workflow management
├── tests/                 # Test suite
├── config/                # Configuration files
├── docs/                  # Documentation
├── logs/                  # Log files
└── scripts/               # Utility scripts
```

#### Key Components

**Core Engine** (`sea_engine.py`)
- Main orchestration logic
- Workflow management
- Error handling

**API Clients** (`src/api/`)
- Airtable integration
- Etsy API wrapper
- Printify API wrapper

**Data Models** (`src/data/`)
- Airtable record models
- Type definitions
- Validation logic

**Workflow Management** (`src/workflow/`)
- State management
- Stage transitions
- Progress tracking

### Contribution Guidelines

#### Code Standards
- Follow PEP 8 style guidelines
- Use type hints for all functions
- Write comprehensive docstrings
- Maintain test coverage above 90%

#### Pull Request Process
1. Fork the repository
2. Create feature branch
3. Write tests for new functionality
4. Ensure all tests pass
5. Submit pull request with description

#### Issue Reporting
- Use issue templates
- Provide reproduction steps
- Include system information
- Add relevant logs

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Airtable team for excellent API documentation
- Etsy developer community for integration examples
- Printify for robust print-on-demand services
- Python community for amazing libraries

---

**SEA-E v2.1** - Built with ❤️ for e-commerce automation

For more information, see our [Complete Tutorial](TUTORIAL.md) and [Quick Start Guide](QUICKSTART.md).
