# 🤖 Airtable Automation Setup Guide

## Step-by-Step Manual Configuration for Bulletproof SEA-E Automations

Since Airtable automations cannot be created via API, follow this guide to manually configure all 5 critical automations in your Airtable base.

---

## 🚀 **Automation 1: New Product Setup - Bulletproof**

### Setup Steps:
1. **Open Airtable Base**: https://airtable.com/appF5TYNhZ71SCjco
2. **Click "Automations" tab** at the top
3. **Click "Create automation"**
4. **Name**: `🚀 New Product Setup - Bulletproof`

### Trigger Configuration:
- **Trigger Type**: "When a record is created"
- **Table**: Products
- **Conditions**: 
  - Product Type is not empty
  - Blueprint ID is not empty
  - Print Provider ID is not empty

### Actions:
#### Action 1: Update Product Record
- **Action Type**: "Update record"
- **Table**: Products
- **Record**: Use record from trigger
- **Fields to Update**:
  ```
  Status → "Design"
  Automation Status → "Initialized"
  Created Date → NOW()
  Last Updated → NOW()
  Automation Log → "Product initialized: " + NOW()
  ```

#### Action 2: Create Variations (Script)
- **Action Type**: "Run script"
- **Script**:
```javascript
// Get product details
let productRecord = input.config().productRecord;
let productType = productRecord.getCellValue("Product Type");
let productId = productRecord.id;

// Define variations by product type
let colors, sizes;
switch(productType) {
  case 'T-Shirt':
    colors = ['Black', 'White', 'Navy', 'Gray', 'baby blue', 'heather navy', 'natural', 'soft pink', 'solid black blend'];
    sizes = ['S', 'M', 'L', 'XL', 'XXL', '3XL'];
    break;
  case 'Sweatshirt':
    colors = ['Black', 'White', 'Navy', 'Gray', 'ash', 'dark heather', 'light blue', 'light pink', 'sand',];
    sizes = ['S', 'M', 'L', 'XL', 'XXL'];
    break;
  case 'Poster':
    colors = ['Default'];
    sizes = ['12x16', '16x20', '18x24', '8x10', '9x11', '11x14', '12x18', '20x30', '24x36'];
    break;
  default:
    colors = ['Black', 'White'];
    sizes = ['M', 'L'];
}

// Create variations
let variationsTable = base.getTable('Variations');
let variations = [];

for (let color of colors) {
  for (let size of sizes) {
    variations.push({
      'Product': [{id: productId}],
      'Variation Name': `${color}-${size}`,
      'Color': color,
      'Size': size,
      'Status': 'Active',
      'Mockup Status': 'Pending'
    });
  }
}

// Create all variation records
await variationsTable.createRecordsAsync(variations);
```

---

## 📊 **Automation 2: Printify Product Created - Auto-Populate**

### Setup Steps:
1. **Click "Create automation"**
2. **Name**: `📊 Printify Product Created - Auto-Populate`

### Trigger Configuration:
- **Trigger Type**: "When a record is updated"
- **Table**: Products
- **Fields**: Printify Product ID
- **Conditions**:
  - Printify Product ID is not empty
  - Automation Status is "Initialized"

### Actions:
#### Action 1: Update Product Status
- **Action Type**: "Update record"
- **Table**: Products
- **Record**: Use record from trigger
- **Fields to Update**:
  ```
  Automation Status → "Printify Created"
  Last Updated → NOW()
  Automation Log → CONCATENATE(Automation Log, "\n", NOW(), ": Printify product created")
  ```

---

## 🎨 **Automation 3: Google Sheets Upload Complete**

### Setup Steps:
1. **Click "Create automation"**
2. **Name**: `🎨 Google Sheets Upload Complete`

### Trigger Configuration:
- **Trigger Type**: "When a record is updated"
- **Table**: Mockups
- **Fields**: Google Sheets URL, Sheets Upload Status
- **Conditions**:
  - Google Sheets URL is not empty
  - Sheets Upload Status is "Uploaded"

### Actions:
#### Action 1: Update Mockup Record
- **Action Type**: "Update record"
- **Table**: Mockups
- **Record**: Use record from trigger
- **Fields to Update**:
  ```
  Generation Status → "Complete"
  Approved → ✓ (checked)
  ```

#### Action 2: Update Linked Variation
- **Action Type**: "Update record"
- **Table**: Variations
- **Record**: Use linked record from Variation field
- **Fields to Update**:
  ```
  Mockup Status → "Complete"
  ```

---

## ✅ **Automation 4: All Mockups Complete - Ready for Listing**

### Setup Steps:
1. **Click "Create automation"**
2. **Name**: `✅ All Mockups Complete - Ready for Listing`

### Trigger Configuration:
- **Trigger Type**: "When a record is updated"
- **Table**: Variations
- **Fields**: Mockup Status
- **Conditions**:
  - Mockup Status is "Complete"

### Actions:
#### Action 1: Check All Variations Complete (Script)
- **Action Type**: "Run script"
- **Script**:
```javascript
// Get the variation record and its linked product
let variationRecord = input.config().variationRecord;
let productRecords = variationRecord.getCellValue("Product");

if (productRecords && productRecords.length > 0) {
  let productId = productRecords[0].id;
  
  // Get all variations for this product
  let variationsTable = base.getTable('Variations');
  let queryResult = await variationsTable.selectRecordsAsync({
    filterByFormula: `{Product} = "${productId}"`
  });
  
  // Check if all variations have complete mockups
  let allComplete = queryResult.records.every(variation => 
    variation.getCellValue('Mockup Status') === 'Complete'
  );
  
  if (allComplete) {
    // Update product status
    let productsTable = base.getTable('Products');
    let productRecord = await productsTable.selectRecordAsync(productId);
    let currentLog = productRecord.getCellValue('Automation Log') || '';
    
    await productsTable.updateRecordAsync(productId, {
      'Status': 'Ready for Listing',
      'Automation Status': 'Mockups Generated',
      'Last Updated': new Date().toISOString(),
      'Automation Log': currentLog + '\n' + new Date().toLocaleString() + ': All mockups completed'
    });
  }
}
```

---

## 🛒 **Automation 5: Etsy Listing Created - Auto-Populate**

### Setup Steps:
1. **Click "Create automation"**
2. **Name**: `🛒 Etsy Listing Created - Auto-Populate`

### Trigger Configuration:
- **Trigger Type**: "When a record is updated"
- **Table**: Listings
- **Fields**: Etsy Listing ID
- **Conditions**:
  - Etsy Listing ID is not empty

### Actions:
#### Action 1: Update Listing Record
- **Action Type**: "Update record"
- **Table**: Listings
- **Record**: Use record from trigger
- **Fields to Update**:
  ```
  Etsy URL → CONCATENATE("https://www.etsy.com/listing/", Etsy Listing ID)
  Etsy Status → "Active"
  Etsy Created Date → NOW()
  Publication Status → "Published"
  ```

#### Action 2: Update Linked Product
- **Action Type**: "Update record"
- **Table**: Products
- **Record**: Use linked record from Product field
- **Fields to Update**:
  ```
  Status → "Listed"
  Automation Status → "Etsy Listed"
  Last Updated → NOW()
  Automation Log → CONCATENATE(Automation Log, "\n", NOW(), ": Etsy listing created")
  ```

---

## 🧪 **Testing Your Automations**

### Test Sequence:
1. **Create Test Product**:
   ```
   Product Name: "🧪 Automation Test"
   Product Type: "T-Shirt"
   Blueprint ID: 5
   Print Provider ID: 1
   ```

2. **Verify Automation 1**: Check that variations were created automatically

3. **Test Printify Integration**:
   ```
   Add: Printify Product ID: "test123"
   ```

4. **Test Google Sheets Integration**:
   ```
   In a Mockup record:
   Google Sheets URL: "https://drive.google.com/file/d/test/view"
   Sheets Upload Status: "Uploaded"
   ```

5. **Test Etsy Integration**:
   ```
   In a Listing record:
   Etsy Listing ID: "123456789"
   ```

### Expected Results:
- ✅ Variations created automatically (5 colors × 5 sizes = 25 variations)
- ✅ Automation Status progresses: Initialized → Printify Created → Mockups Generated → Etsy Listed
- ✅ All timestamps and logs populated automatically
- ✅ Status fields updated at each stage

---

## 🚨 **Troubleshooting**

### Common Issues:
1. **Script Errors**: Check field names match exactly
2. **Missing Triggers**: Ensure all conditions are met
3. **Permission Issues**: Verify automation permissions in base settings

### Validation Commands:
```bash
# Test field mappings
python src/api/airtable_client.py --test-fields

# Validate automation logic
python src/automation/airtable_automations.py --validate
```

---

## ✅ **Completion Checklist**

- [ ] Automation 1: New Product Setup configured
- [ ] Automation 2: Printify Auto-Populate configured  
- [ ] Automation 3: Google Sheets Upload configured
- [ ] Automation 4: All Mockups Complete configured
- [ ] Automation 5: Etsy Listing configured
- [ ] All automations tested with sample data
- [ ] Field mappings validated
- [ ] Error handling verified

**Once complete, your Airtable will be BULLETPROOF for 1000+ listing automation!** 🎊
