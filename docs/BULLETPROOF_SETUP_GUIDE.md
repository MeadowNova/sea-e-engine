# 🎯 SEA-E Engine Bulletproof Setup Guide

## Complete Quality Assurance & Precision Mapping Workflow

This guide ensures **perfect mockups**, **precise Printify placement**, and **bulletproof Airtable automation** for your 1000+ listing scale-up.

---

## 📋 Phase 1: Precision Coordinate Mapping

### Step 1: Install VGG Image Annotator (VIA)

**Option A: Online Tool (Recommended)**
1. Go to: https://www.robots.ox.ac.uk/~vgg/software/via/via_demo.html
2. No installation required - runs in browser

**Option B: Local Installation**
```bash
git clone https://gitlab.com/vgg/via.git
cd via
# Open via.html in your browser
```

### Step 2: Annotate Your Mockup Templates

1. **Load Template Images**:
   - Upload your t-shirt/sweatshirt/poster templates to VIA
   - Use high-resolution templates (2000x2000+ recommended)

2. **Create Design Area Annotations**:
   - Use **Polygon Tool** for precise design area mapping
   - Mark each design placement area (front, back, etc.)
   - Label each area: "front", "back", "sleeve", etc.

3. **Annotation Guidelines**:
   ```
   T-Shirts: Mark chest area precisely
   Sweatshirts: Mark chest + optional sleeve areas  
   Art Prints: Mark frame interior area
   ```

4. **Export Annotations**:
   - Click: Annotation → Export annotations
   - Choose: JSON format
   - Save as: `template_annotations.json`

### Step 3: Generate Coordinate Mappings

```bash
cd "/home/ajk/sea-e engine"

# Process VIA annotations to generate coordinate configs
python tools/coordinate_mapper.py \
  --via-json path/to/template_annotations.json \
  --templates-dir assets/mockups \
  --config-dir config/coordinate_maps
```

**Output**: Precise coordinate configurations in `config/coordinate_maps/`

---

## 🎨 Phase 2: Quality Assurance Testing

### Step 1: Run Complete QA Suite

```bash
# Run comprehensive quality tests
python tests/test_quality_assurance.py
```

**Expected Results**:
- ✅ T-Shirt Mockups: 8.0+/10 quality score
- ✅ Art Print Mockups: 8.0+/10 quality score  
- ✅ Coordinate Precision: 0% error rate
- ✅ Processing Time: <30 seconds per mockup

### Step 2: Test with Your Design

```bash
# Test with your actual design
python examples/google_sheets_integration_demo.py
```

**Validation Checklist**:
- [ ] Mockup resolution ≥ 1800x1800 pixels
- [ ] Design placement perfectly centered
- [ ] No distortion or quality loss
- [ ] Google Sheets URL generated
- [ ] Airtable record updated

---

## 🖨️ Phase 3: Printify Integration Testing

### Step 1: Test Precise Placement

```python
from src.api.printify import PrintifyAPIClient
from tools.coordinate_mapper import CoordinateMapper

# Load coordinate configuration
mapper = CoordinateMapper()
config = mapper.load_config("config/coordinate_maps/tshirt_template_coordinates.json")

# Create product with precise placement
printify = PrintifyAPIClient()
product_id = printify.create_product_with_precise_placement(
    title="QA Test Product",
    description="Quality assurance test",
    blueprint_id=5,  # Your blueprint ID
    print_provider_id=1,  # Your print provider ID
    design_file_path="path/to/your/design.png",
    coordinate_config=config,
    colors=["Black", "White"],
    variations=["S", "M", "L", "XL"]
)
```

### Step 2: Validate Printify Product

1. **Check Product in Printify Dashboard**:
   - Design placement is pixel-perfect
   - All color variations included
   - All size variations included
   - Product ready for publishing

2. **Verify Coordinates**:
   - Design centered exactly as intended
   - No cropping or distortion
   - Consistent across all variants

---

## 🗃️ Phase 4: Airtable Automation Validation

### Step 1: Test Complete Automation

```python
from src.automation.airtable_automations import AirtableAutomationEngine

# Initialize automation engine
automation = AirtableAutomationEngine()

# Create complete product record
product_data = {
    'product_name': 'QA Test Product',
    'blueprint_id': 5,
    'print_provider_id': 1,
    'description': 'Quality assurance test product',
    'category': 'Apparel',
    'target_price': 25.99,
    'variations': [
        {'name': 'Black-M', 'color': 'Black', 'size': 'M'},
        {'name': 'White-L', 'color': 'White', 'size': 'L'}
    ]
}

# This should auto-populate ALL fields
product_record_id = automation.create_complete_product_record(product_data)
```

### Step 2: Verify Airtable Population

**Check these fields are auto-populated**:
- [ ] Blueprint ID ✅
- [ ] Blueprint Title ✅  
- [ ] Blueprint Brand ✅
- [ ] Print Provider ID ✅
- [ ] Print Provider Name ✅
- [ ] Print Provider Location ✅
- [ ] Variant SKUs ✅
- [ ] Available Colors ✅
- [ ] Available Sizes ✅
- [ ] Creation Timestamps ✅
- [ ] Automation Status ✅

---

## 🔗 Phase 5: End-to-End Workflow Test

### Complete Workflow Test

```python
# Complete workflow test
from src.core.engine import SEAEngine

engine = SEAEngine()

# Test complete pipeline
result = engine.process_single_product(
    design_path="path/to/your/design.png",
    product_name="Complete QA Test",
    product_type="tshirts",
    blueprint_id=5,
    print_provider_id=1,
    colors=["Black", "White", "Navy"],
    sizes=["S", "M", "L", "XL"],
    enable_sheets_upload=True,
    create_etsy_listing=True
)
```

**Expected Complete Result**:
1. ✅ High-quality mockup generated (8.0+/10)
2. ✅ Mockup uploaded to Google Sheets
3. ✅ Shareable URL generated
4. ✅ Airtable record created with ALL fields
5. ✅ Printify product created with precise placement
6. ✅ Etsy listing created (optional)

---

## 📊 Quality Thresholds

### Mockup Quality Standards
- **Resolution**: Minimum 1800x1800 pixels
- **Quality Score**: Minimum 8.0/10
- **Processing Time**: Maximum 30 seconds
- **File Size**: 2-10MB (optimized)

### Coordinate Precision Standards  
- **Placement Error**: Maximum 2% deviation
- **Center Accuracy**: ±0.02 coordinate units
- **Scale Consistency**: ±5% across templates

### Automation Completeness
- **Field Population**: 100% required fields
- **Error Rate**: <1% automation failures
- **Processing Speed**: <5 seconds per record

---

## 🚨 Troubleshooting

### Common Issues & Solutions

**Issue**: Mockup quality score <8.0
- **Solution**: Check template resolution, adjust blend modes
- **Command**: `python tests/test_quality_assurance.py --debug`

**Issue**: Coordinate placement off-center
- **Solution**: Re-annotate templates with VIA, regenerate configs
- **Command**: `python tools/coordinate_mapper.py --validate config_file.json`

**Issue**: Airtable fields not populating
- **Solution**: Check API connections, validate field mappings
- **Command**: `python src/automation/airtable_automations.py --test`

**Issue**: Google Sheets upload failing
- **Solution**: Check credentials, test connection
- **Command**: `python auth/test_gsheets_auth.py`

---

## ✅ Production Readiness Checklist

### Before Scaling to 1000+ Listings:

- [ ] All QA tests passing (8.0+/10 scores)
- [ ] Coordinate precision validated (<2% error)
- [ ] Airtable automation 100% complete
- [ ] Google Sheets integration working
- [ ] Printify placement pixel-perfect
- [ ] Processing time <30 seconds per product
- [ ] Error handling robust
- [ ] Monitoring/logging in place

### Scale-Up Preparation:

- [ ] Batch processing tested (10+ products)
- [ ] Rate limiting configured
- [ ] Storage management optimized
- [ ] Backup systems in place
- [ ] Quality monitoring automated

---

## 🎯 Success Metrics

**Target Performance**:
- **Quality**: 8.5+/10 average mockup score
- **Speed**: 20 products/hour processing rate
- **Accuracy**: 99%+ coordinate precision
- **Automation**: 100% field population
- **Reliability**: 99%+ uptime

**Your 1000 Listing Goal**:
- **Timeline**: 30 days = 33 listings/day
- **Processing**: 2 hours/day at 20 products/hour
- **Quality**: Bulletproof automation ensures consistency

---

🎉 **You're now ready for bulletproof, high-volume listing creation!**
