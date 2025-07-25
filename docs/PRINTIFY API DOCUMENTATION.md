Blueprint properties
id
READ-ONLY
"id": 5
A unique int identifier for the blueprint. Each id is unique across the Printify system.
title
READ-ONLY
"title": "Blueprint's title"
The name of the blueprint.
brand
READ-ONLY
"brand": "Blueprint's brand"
The brand of the blueprint (i.e. the name of the blank product's manufacturer).
model
READ-ONLY
"model": "Blueprint's brand model"
The specific model of the blueprint's brand (i.e. the unique identifier of the blank product's model or style).
images
READ-ONLY
"images": [
      "https://images.example.com/869549a1a0894a4692371b1f9928e14a.png",
      "https://images.example.com/878331a2b0876c9801746d2e2454f14a.png"
]
Links to the title image wrappers displayed on the catalog.
Print provider properties
id
READ-ONLY
"id": 3
A unique int identifier for the print provider. Each id is unique across the Printify system.
title
READ-ONLY
"title": "Print provider's title"
The name of the print provider.
location
READ-ONLY
"location": {
      "address1": "89 Weirfield St",
      "address2": "",
      "city": "Brooklyn",
      "country": "US",
      "region": "NY",
      "zip": "11221-5120"
}
The return address of the print provider.
Variant properties
id
READ-ONLY
"id": 17390
A unique int identifier for the blueprint variant. Each id is unique across the Printify system.
title
READ-ONLY
"title": "Variant's title"
The name of the variant.
options
READ-ONLY
"options": {
    "color": "Heather Grey",
    "size": "XS"
}
Options are read only values and describes blueprint variant options. There can be up to 3 options for a blueprint.
placeholders
READ-ONLY
"placeholders": [{
    "position": "back",
    "height": 3995,
    "width": 3153
    },
    {
    "position": "front",
    "height": 3995,
    "width": 3153
}]
Placeholders describe the available printable areas for a blueprint. See placeholder properties for reference.
Placeholder properties
position
READ-ONLY
"position": "front"
Position states the available printable areas for a blueprint fulfilled by a specific print provider.
height
READ-ONLY
"height": 3995
Integer value for printable area height in pixels.
width
READ-ONLY
"width": 3153
Integer value for printable area width in pixels.
Shipping properties
handling_time
READ-ONLY
"handling_time": {
    "value":10,
    "unit": "day"
}
The standard shipping timeframe for a blueprint from a specific print provider.
profiles
READ-ONLY
"profiles": [
    {
        "variant_ids": [1,2],
        "first_item": {
             "currency": "USD",
             "cost": 1000
        },
        "additional_items": {
             "currency": "USD",
             "cost": 1000
        },
        "countries":["US"]
    },
    {
        "variant_ids": [1,2],
        "first_item": {
             "currency": "USD",
             "cost": 1000
        },
        "additional_items": {
             "currency": "USD",
             "cost": 1000
        },
        "countries":["REST_OF_THE_WORLD"]
    }
]
The list of shipping locations and flat shipping costs for all variants of a blueprint from a specific print provider. See profile properties for reference.
Profile properties
variant_ids
READ-ONLY
"variant_ids": [
    1,2,3,4,5,6,7
]
Lists the ids of all blueprint variants the specific profile is associated to in an array.
first_item
READ-ONLY
"first_item": {
    "currency": "USD",
    "cost": 1000
}
The currency and flat cost of shipping for a line item if identified as the first item in an order.
additional_items
READ-ONLY
"additional_items": {
    "currency": "USD",
    "cost": 1000
}
The currency and flat cost of shipping for all other line items of the specific blueprint and print provider in the same order.
countries
READ-ONLY
"countries": [
    US
]
Lists the countries or delivery locations the shipping profile applies to.
Print details properties
print_on_side
OPTIONAL

        "print_on_side": "regular"
    
States the type of side print. possible values are "regular" for extending print area to the sides of canvas and "mirror" to keep original print area and mirror it to the sides.
separator_type
OPTIONAL

        "separator_type": "Numbers"
    
Required with "separator_color" and specific to clock type blueprints, States the type clock separator. Possible string values are "Numbers" numeric separators, "Lines" for single bar separators, and "None" to specify that no separators be used.
separator_color
OPTIONAL

        "separator_color": "#f100ff"
    
Required with "separator_type" and specific to clock type blueprints, States the type clock separator. Value must be a valid string hexadecimal color code.
Endpoints
Retrieve a list of available blueprints
GET	/v1/catalog/blueprints.json
Retrieve a list of available blueprints
GET /v1/catalog/blueprints.json
View Response
Retrieve a specific blueprint
GET	/v1/catalog/blueprints/{blueprint_id}.json
Retrieve a specific blueprint
GET /v1/catalog/blueprints/{blueprint_id}.json
View Response
Retrieve a list of all print providers that fulfill orders for a specific blueprint
GET	/v1/catalog/blueprints/{blueprint_id}/print_providers.json
Retrieve a list of all print providers that fulfill orders for a specific blueprint
GET /v1/catalog/blueprints/{blueprint_id}/print_providers.json
View Response
Retrieve a list of variants of a blueprint from a specific print provider
GET	/v1/catalog/blueprints/{blueprint_id}/print_providers/{print_provider_id}/variants.json
show-out-of-stock
OPTIONAL
Depending on the value, it shows all variants or only those not out of stock. Without passing this query param, the list will contain only those variants in stock.
0 - show only variants that are in stock.
1 - also show variants out of stock (all variants).
Retrieve a list of variants of a blueprint from a specific print provider
GET /v1/catalog/blueprints/{blueprint_id}/print_providers/{print_provider_id}/variants.json
View Response
Retrieve shipping information
GET	/v1/catalog/blueprints/{blueprint_id}/print_providers/{print_provider_id}/shipping.json
Retrieve shipping information
GET /v1/catalog/blueprints/{blueprint_id}/print_providers/{print_provider_id}/shipping.json
View Response
Retrieve a list of available print providers
GET	/v1/catalog/print_providers.json
Retrieve a list of available print providers
GET /v1/catalog/print_providers.json
View Response
Retrieve a specific print provider
GET	/v1/catalog/print_providers/{print_provider_id}.json
Retrieve a specific print provider and a list of associated blueprint offerings
GET /v1/catalog/print_providers/{print_provider_id}.json
View Response
Structure
Structure of Catalog resource with possible transitions between endpoints.

catalog structure

Products
The Product resource lets you list, create, update, delete and publish products to a store.

On this page:

What you can do with the product resource
Product properties
Variant properties
Placeholder properties
Image properties
Image Pattern properties
Mock-up image properties
Publishing properties
Endpoints
Products Structure
Image positioning
Common error cases
What you can do with the product resource
The Printify Public API lets you do the following with the Product resource:

GET /v1/shops/{shop_id}/products.json
Retrieve a list of all products
GET /v1/shops/{shop_id}/products/{product_id}.json
Retrieve a product
GET /v1/shops/{shop_id}/products/{product_id}/gpsr.json
Retrieve a product's GPSR information
POST /v1/shops/{shop_id}/products.json
Create a new product
PUT /v1/shops/{shop_id}/products/{product_id}.json
Update a product
DELETE /v1/shops/{shop_id}/products/{product_id}.json
Delete a product
POST /v1/shops/{shop_id}/products/{product_id}/publish.json
Publish a product
POST /v1/shops/{shop_id}/products/{product_id}/publishing_succeeded.json
Set product publish status to succeeded
POST /v1/shops/{shop_id}/products/{product_id}/publishing_failed.json
Set product publish status to failed
POST /v1/shops/{shop_id}/products/{product_id}/unpublish.json
Notify that a product has been unpublished
Product properties
id
READ-ONLY
"id": "5cb87a8cd490a2ccb256cec4"
A unique string identifier for the product. Each id is unique across the Printify system.
title
REQUIRED
"title": "Product's title"
The name of the product.
description
REQUIRED
"description": "Product's description"
A description of the product. Supports HTML formatting for compatible sales channels.
safety_information
OPTIONAL
"safety_information": "GPSR information: John Doe, test@example.com, 123 Main St, Apt 1, New York, NY, 10001, US
Product information: Gildan, 5000, 2 year warranty in EU and UK as per Directive 1999/44/EC
Warnings, Hazzard: No warranty, US
Care instructions: Machine wash: warm (max 40C or 105F), Non-chlorine: bleach as needed, Tumble dry: medium, Do not iron, Do not dryclean",
Safety information of the product. Can be retrieved using the GPSR endpoint. Supports HTML formatting for compatible sales channels.
tags
OPTIONAL
"tags": ["T-shirt", "Men's"]
Tags are also published to sales channel.
options
READ-ONLY
"options": [{
    "name": "Colors",
    "type": "color",
    "values": [{
        "id": 751,
        "title": "Solid White",
        "colors": [
            "#F9F9F9"
        ]
    }]
}]
Options are read only values and describes product options. There can be up to 3 options for a product.
variants
REQUIRED
"variants": [{
    "id": 123,
    "price": 1000,
    "title": "Solid Dark Gray / S",
    "sku": "PRY-123",
    "grams": 120,
    "is_enabled": true,
    "is_default": false,
    "is_printify_express_eligible": true,
    "options": [751, 2]
}]
A list of all product variants, each representing a different version of the product. But during product creation, only the variant id and price are necessary. See variant properties for reference.
images
READ-ONLY
"images": [{
    "src": "http://example.com/tee.jpg",
    "variant_ids": [123, 124],
    "position": "front",
    "is_default" : false,
}]
Mock-up images are read only values. The mock-up images are grouped by variants and position. See mock-up image properties for reference.
created_at
READ-ONLY
"created_at": "2017-04-18 13:24:28+00:00"
The date and time when a product was created.
update_at
READ-ONLY
"update_at": "2017-04-18 13:24:28+00:00"
The date and time when a product was last updated.
visible
READ-ONLY
"visible": true
Used for publishing. Visibility in sales channel. Can be true or false, defaults to true.
blueprint_id
REQUIRED
READ-ONLY
"blueprint_id": 5
Required when creating a product, but is read only after. See catalog for how to get blueprint_id.
print_provider_id
REQUIRED
READ-ONLY
"print_provider_id": 5
Required when creating a product, but is read only after. See catalog for how to get print_provider_id.
user_id
READ-ONLY
"user_id": 5
User id that a product belongs to.
shop_id
READ-ONLY
"shop_id": 1
Shop id that a product belongs to.
print_areas
REQUIRED
"print_areas": [{
    "variant_ids": [123, 124],
    "placeholders": [{
        "position": "front",
        "images": []
    }],
}]
All print area values are required. Each variant has a print area attached to it. Each print area has placeholders which represent printable areas on a product. For example the front of the t-shirt, back of the t-shirt etc. Each placeholder has images and their positions, where they need to be printed in the printable area. See placeholder properties for reference.
print_details
OPTIONAL

    "print_details": {
        "print_on_side": "regular"
    }
}]
"print_on_side" key is used to set the type of side printing for canvases. There are three possible values:
"regular" - to extend print area to the sides of canvas
"mirror" - to keep original print area and mirror it to the sides
"off" - stop printing on sides
external
CONDITIONAL
"external": [{
    "id": "A123abceASd",
    "handle": "/path/to/product",
    "shipping_template_id": "B123abceASd"
}]
Updated by sales channel with publishing succeeded endpoint. Id and handle are external references in the sales channel. See publishing succeeded endpoint for more reference.
Shipping Template ID is optional and can be passed during product creation or update.
is_locked
READ-ONLY
"is_locked": true
A product is locked during publishing. Locked products can't be updated until unlocked.
is_printify_express_eligible
READ-ONLY
"is_printify_express_eligible": true
Flag to indicate if product could be eligible for Printify Express Delivery, depending on selection of its variant.
is_economy_shipping_eligible
READ-ONLY
"is_economy_shipping_eligible": true
Flag to indicate if product could be eligible for Economy Shipping, depending on selection of its variant.
is_printify_express_enabled
OPTIONAL
"is_printify_express_enabled": true
Flag to indicate if Printify Express Delivery is enabled for the product. Printify Express Delivery can be enabled only for eligible products (see is_printify_express_eligible flag). Defaults to false.
is_economy_shipping_enabled
READ-ONLY
"is_economy_shipping_enabled": true
Flag to indicate if Economy Shipping is enabled for the product. Economy Shipping can be enabled only for eligible products (see is_economy_shipping_eligible flag). Defaults to false.
sales_channel_properties
OPTIONAL
Lists product properties specific to the sales channel associated with the product, if the sales channel has such custom properties, the attributes are listed in the object and may be actionable, but for all custom integrations, it will either be null or an empty array.
Amazon
"sales_channel_properties": {
      "free_shipping": false,
      "bullet_points": [
          "Machine-washable",
          "100% cotton"
      ],
      "no_variation_parent": false
}
Etsy
"sales_channel_properties": {
      "free_shipping": false,
      "personalisation": [
          {
              "instructions": "Please provide the name you would like to be printed on the mug",
              "buyer_response_limit": 30
          }
      ]
}
Big Commerce
"sales_channel_properties": {
      "categories": [1, 2, 3],
      "free_shipping": false
}
eBay
"sales_channel_properties": {
      "free_shipping": false
}
Shopify
"sales_channel_properties": {
      "collections": ["T-shirts", "Red Clothing"],
      "free_shipping": false
}
Squarespace
"sales_channel_properties": {
      "store_page": "https://some-store.squarespace.com"
}
TikTok
"sales_channel_properties": {
      "delivery_service_id": "123",
      "warehouse_id": "456",
      "free_shipping": false
}
views
READ-ONLY
"views": [
      {
          "id": 34395,
          "label": "Front side",
          "position": "front",
          "files": [
              {
                  "src": "https://images.printify.com/api/catalog/618e1792f80e2001a840687b.svg",
                  "variant_ids": [
                      76255
                  ]
              },
          ]
      }
    ]
Lists blank blueprint images with dedicated print areas. Each view has a label, position, and files source url for a list of variants.
Variant properties
id
REQUIRED
READ-ONLY
"id": 123
A unique int identifier for the product variant from the blueprint. Each id is unique across the Printify system. See catalog for instructions on how to get variant ids.
sku
OPTIONAL
"sku": "SKU-123"
Optional unique string identifier for the product variant. If one is not provided, one will be generated by Printify.
price
REQUIRED
"price": 1000
Price in cents, integer value.
cost
READ-ONLY
"cost": 400
Product variant's fulfillment cost in cents, integer value.
title
READ-ONLY
"title": "Solid Dark Gray / S"
Variant title.
grams
READ-ONLY
"grams": 120
Weight in grams for a product variant
is_enabled
OPTIONAL
"is_enabled": true
Used for publishing, the value is true if one has the variant in question selected as an offering and wants it published.
is_default
OPTIONAL
"is_default": true
Only one variant can be default. Used when publishing to sales channel. Default variant's image will be the title image of the product.
is_available
READ-ONLY
"is_available": true
Actual stock status of the variant, if false, the variant is out of stock and vice versa.
is_printify_express_eligible
READ-ONLY
"is_printify_express_eligible": true
Flag to indicate if product's variant is eligible for Printify Express delivery.
options
READ-ONLY
"options": [751, 2]
Reference to options by id.
Placeholder properties
position
REQUIRED
"position": "front"
See blueprint placeholder properties from the catalog endpoint for reference on how to get positions.
images
REQUIRED
"images": []
Array of images. See image properties for reference.
Image properties
id
REQUIRED
"id": 123
See upload images for reference on how to upload images and get all needed properties.
src
READ-ONLY
"src": https://example.com/5c7665205342af161e1cb26e
Full image source url.
name
READ-ONLY
"name": "image.jpg"
Name of an image file.
type
READ-ONLY
"type": "image/png"
Type of an image. Valid image types are image/png, image/jpg, image/jpeg.
height
READ-ONLY
"height": 100
Float value for image height in pixels. See upload images for reference on how to upload images and get all needed properties.
width
READ-ONLY
"width": 100
Float value for image width in pixels. See upload images for reference on how to upload images and get all needed properties.
x
REQUIRED
"x": 100
Float value to position an image on the x axis. See image positioning for reference on how to position images.
y
REQUIRED
"y": 100
Float value to position an image on the y axis. See image positioning for reference on how to position images.
scale
REQUIRED
"scale": 1
Float value to scale image up or down. See image positioning for reference on how to position images.
angle
REQUIRED
"angle": 180
Integer value used to rotate image. See image positioning for reference on how to position images.
pattern
OPTIONAL
Object value used to field defines a repeating graphical design applied to a product image. It includes properties to adjust spacing, rotation, and positioning of the pattern. See image pattern properties
font_family
READ-ONLY
"font_family": "Arial"
Font family used for text layer.
font_size
READ-ONLY
"font_size": 12
Font size used for text layer.
font_weight
READ-ONLY
"font_weight": "bold"
Font weight used for text layer.
font_color
READ-ONLY
"font_color": "#000000"
Font color used for text layer.
font_style
READ-ONLY
"font_style": "italic"
Font style used for text layer.
input_text
READ-ONLY
"input_text": "Hello World"
Text value used for text layer.
text_align
READ-ONLY
"text_align": "left"
Text alignment used for text layer.
Image pattern properties
spacing_x
REQUIRED
"spacing_x": 0.5
Float value. Horizontal Spacing expressed relative to width, where 0.5 would mean the item should repeat each half-width of image, and 1 means no spacing, 1.5 would mean 50% spacing etc.
spacing_y
REQUIRED
"spacing_y": 0.5
Float value. Vertical Spacing expressed relative to height, where 0.5 would mean the item should repeat each half-height of image, and 1 means no spacing, 1.5 would mean 50% spacing etc.
angle
REQUIRED
"angle": 0
Float value. Allows changing the axis along which items repeat. 0 means horizontal. Accepts values from -45 to +45 (Because the result of all other angles can already be achieved by staying within this range).
offset
REQUIRED
"offset": 0.5
Float value. Allows specifying offset between 2 lines. Setting this to 0.5 will produce a "brick" pattern. Accepts values between -1 and 1.
Mock-up image properties
src
READ-ONLY
"src": "https://images.printify.com/mockup/5d39b159e7c48c000728c89f/33719/145/mug-11oz.jpg"
Url of a mock-up image.
variant_ids
READ-ONLY
"variant_ids": [
    61618,
    61619,
    61620,
    61621,
    61622
]
Array of integer ids for variants illustrated by the mock-up image.
position
READ-ONLY
"position": "front"
Camera position of a mockup (i.e. what part of the product is being displayed).
is_default
READ-ONLY
"is_default": true
Used by the sales channel. If set to true, The specific mockup is the title image. Can be used to decide the first image displayed when a product's page is accessed.
Publishing properties
The "publish" button in the Printify app only locks the product on the Printify app and triggers the product:publish:started event if you are subscribed to it, see See Product events for reference. To publish a product, you need to create it manually on your store from the data you can obtain from the product resource or develop a system to automate that. Once done, you can use the Publish succeeded endpoint or Publish failed endpoint to unlock the product.

images
REQUIRED
"images": true
Used by the sales channel. If set to false, Images will not be published, and existing images will be used instead.
variants
REQUIRED
"variants": true
Used by the sales channel. If set to false, product variations will not be published.
title
REQUIRED
"title": true
Used by sales channel. If set to false, product title will not be updated.
description
REQUIRED
"description": true
Used by sales channel. If set to false, product description will not be updated.
tags
REQUIRED
"tags": true
Used by sales channel. If set to false, product tags will not be updated.
shipping_template
OPTIONAL
"shipping_template": true
Used by Etsy and Amazon sales channels only. If set to false, product shipping template will not be updated.
Endpoints
Retrieve a list of products
GET	/v1/shops/{shop_id}/products.json
limit
OPTIONAL
Results per page
(default: 10, maximum: 50)
page
OPTIONAL
Paginate through list of results
Retrieve all products
GET /v1/shops/{shop_id}/products.json
View Response
Retrieve specific page from results
GET /v1/shops/{shop_id}/products.json?page=2
View Response
Retrieve limited results
GET /v1/shops/{shop_id}/products.json?limit=1
View Response
Retrieve a product
GET	/v1/shops/{shop_id}/products/{product_id}.json
Retrieve a product
GET /v1/shops/{shop_id}/products/{product_id}.json
View Response
Retrieve product GPSR information
GET	/v1/shops/{shop_id}/products/{product_id}/gpsr.json
Retrieve a product's GPSR information
GET /v1/shops/{shop_id}/products/{product_id}/gpsr.json
View Response
Create a new product
POST	/v1/shops/{shop_id}/products.json
Create a new product
POST /v1/shops/{shop_id}/products.json
{
    "title": "Product",
    "description": "Good product",
    "safety_information": "GPSR information: John Doe, test@example.com, 123 Main St, Apt 1, New York, NY, 10001, US
    Product information: Gildan, 5000, 2 year warranty in EU and UK as per Directive 1999/44/EC
    Warnings, Hazzard: No warranty, US
    Care instructions: Machine wash: warm (max 40C or 105F), Non-chlorine: bleach as needed, Tumble dry: medium, Do not iron, Do not dryclean",
    "blueprint_id": 384,
    "print_provider_id": 1,
    "variants": [
          {
              "id": 45740,
              "price": 400,
              "is_enabled": true
          },
          {
              "id": 45742,
              "price": 400,
              "is_enabled": true
          },
          {
              "id": 45744,
              "price": 400,
              "is_enabled": false
          },
          {
              "id": 45746,
              "price": 400,
              "is_enabled": false
          }
      ],
      "print_areas": [
        {
          "variant_ids": [45740,45742,45744,45746],
          "placeholders": [
            {
              "position": "front",
              "images": [
                  {
                    "id": "5d15ca551163cde90d7b2203", 
                    "x": 0.5, 
                    "y": 0.5, 
                    "scale": 1,
                    "angle": 0,
                    "pattern": {
                      "spacing_x": 1,
                      "spacing_y": 2,
                      "scale": 3,
                      "offset": 4
                    }
                  }
              ]
            }
          ]
        }
      ]
  }
View Response
Update a product
A product can be updated partially or as a whole document. When updating variants, all variants must be present in the request.

PUT	/v1/shops/{shop_id}/products/{product_id}.json
Update a product
PUT /v1/shops/{shop_id}/products/{product_id}.json
{
    "title": "Product"
}
View Response
Delete a product
DELETE	/v1/shops/{shop_id}/products/{product_id}.json
Delete a product
DELETE /v1/shops/{shop_id}/products/{product_id}.json
View Response
Publish a product
This does not implement any publishing action unless the Printify store is connected to one of our other supported sales channel integrations, if your store is custom and is subscribed to the product::pubish::started event, that event will be triggered and the properties that are set in the request body will be set in the event payload for your store to react to if implemented. The case is the same for attempting to publish a product from the Printify app. See product events for reference.

POST	/v1/shops/{shop_id}/products/{product_id}/publish.json
Publish a product
POST /v1/shops/{shop_id}/products/{product_id}/publish.json
{
    "title": true,
    "description": true,
    "images": true,
    "variants": true,
    "tags": true,
    "keyFeatures": true,
    "shipping_template": true
}
View Response
Set product publish status to succeeded
Using this endpoint removes the product from the locked status on the Printify app and sets the the it's external property with the handle you provide in the request body.

POST	/v1/shops/{shop_id}/products/{product_id}/publishing_succeeded.json
Set product publish status to succeeded
POST /v1/shops/{shop_id}/products/{product_id}/publishing_succeeded.json
{
    "external": {
        "id": "5941187eb8e7e37b3f0e62e5",
        "handle": "https://example.com/path/to/product"
    }
}
View Response
Set product publish status to failed
Using this endpoint removes the product from the locked status on the Printify app.

POST	/v1/shops/{shop_id}/products/{product_id}/publishing_failed.json
Set product publish status to failed
POST /v1/shops/{shop_id}/products/{product_id}/publishing_failed.json
{
    "reason": "Request timed out"
}
View Response
Notify that a product has been unpublished
POST	/v1/shops/{shop_id}/products/{product_id}/unpublish.json
Notify that a product has been unpublished
POST /v1/shops/{shop_id}/products/{product_id}/unpublish.json
View Response
Structure
Structure of Product resource with possible transitions between endpoints.

products structure

Image positioning
Coordinate system
coordinate system
Printify uses the [0,00; 0,00] .. [1,00; 1,00] cartesian coordinate system, with the placeholder center being x=0,5, y=0,5.
Artwork scale
scale 1,00 scale 0,5

The scale of the image (width) relative to the print area placeholder (width). Scale can be anything from 0,00 to infinity.

1,00 - scale image to fill the print area fully
0,5 - scale image to fill 1/2 of the the print area

Artwork angle - 360° angle
Rule of thumb: if you use artwork with width equal to print area placeholder width, set scale to 1,00 and position it at x=0,5 y=0,5 - your design will be horizontally and vertically aligned and fill all the print area fully.

Creating Products
Flow of transitions between resources for making the product - with two possible paths of coming from Blueprint or Print Provider.

creating product by blueprint
creating product by blueprint

Common error cases
You may receive errors when trying to create or update a product. A common error is due failing dpi validation because the image is low quality. If this happens, you will receive a detailed error message similar to the one shown here.

POST	/v1/shops/{shop_id}/products.json
Common error cases
POST /v1/shops/{shop_id}/products.json
400 Image has low quality error example (See HTTP Status Codes below)
View Response
PUT	/v1/shops/{shop_id}/products/{product_id}.json
Common error cases
PUT /v1/shops/{shop_id}/products/{product_id}.json
400 Image has low quality error example (See HTTP Status Codes below)
View Response
Orders
Printify API lets your application manage orders in a Merchants shop. You can submit orders for existing products in a merchant's shop or you can create new products with every order as in the case with merchandise created with customizable user-generated content.

Ordering existing products or creating products with orders will require different line item entries so that should be kept in mind.

On this page:

What you can do with the order resource
Order properties
Line item properties
Line item metadata properties
Metadata properties
Shipment properties
Order submission properties
Print area properties
Print details properties
Endpoints
Structure
Making Order
Common error cases
What you can do with the order resource
The Printify Public API lets you do the following with the Order resource:

GET /v1/shops/{shop_id}/orders.json
Retrieve a list of orders
GET /v1/shops/{shop_id}/orders/{order_id}.json
Get order details by id
POST /v1/shops/{shop_id}/orders.json
Submit an order
POST /v1/shops/{shop_id}/express.json
Submit a Printify Express order
POST /v1/shops/{shop_id}/orders/{order_id}/send_to_production.json
Send an existing order to production
POST /v1/shops/{shop_id}/orders/shipping.json
Calculate the shipping cost of an order
POST /v1/shops/{shop_id}/orders/{order_id}/cancel.json
Cancel an unpaid order
Order properties
id
READ-ONLY
"id": "5a96f649b2439217d070f507"
A unique string identifier for the order. Each id is unique across the Printify system.
app_order_id
READ-ONLY
"app_order_id": "215014.44"
The Web app Printify order ID for the order. Present only in responses (read-only), and cannot be used for searching or filtering.
address_to
REQUIRED
READ-ONLY
"address_to": {
    "first_name": "John",
    "last_name": "Smith",
    "region": "",
    "address1": "ExampleBaan 121",
    "city": "Retie",
    "zip": "2470",
    "email": "example@msn.com",
    "phone": "0574 69 21 90",
    "country": "BE",
    "company": "MSN"
}
The delivery details of the order's recipient.
line_items
REQUIRED
READ-ONLY
"line_items": [{
      "product_id": "5b05842f3921c9547531758d",
      "quantity": 1,
      "variant_id": 17887,
      "print_provider_id": 5,
      "cost": 1050,
      "shipping_cost": 400,
      "status": "pending",
      "metadata": {
        "title": "18K gold plated Necklace",
        "price": 2200,
        "variant_label": "Golden indigocoin",
        "sku": "168699843",
        "country": "United States"
      },
      "sent_to_production_at": "2017-04-18 13:24:28+00:00",
      "fulfilled_at": "2017-04-18 13:24:28+00:00"
}]
A list of all line items in the order. See line item properties for reference.
metadata
READ-ONLY
"metadata": {
    "order_type": "external",
    "shop_order_id": 1370762297,
    "shop_order_label": "1370762297",
    "shop_fulfilled_at": "2017-04-18 13:24:28+00:00"
}
Other data about the order. See metadata properties for reference.
total_price
READ-ONLY
"total_price": 2200
Retail price in cents, integer value.
total_shipping
READ-ONLY
"total_shipping": 400
Shipping price in cents, integer value.
total_tax
READ-ONLY
"total_tax": 0
Tax cost in cents, integer value.
status
READ-ONLY
"status": "pending"
Production status of the entire order in string format, it can be any of the following:

Status	Definition
pending	An order is created in the pending status. Orders should not stay in this status for a long time.
on-hold	
The order is ready to handle user actions. Users can edit orders in this status. The order gets this status at later stages for various reasons:

Line items are discontinued during the order processing
Line items go out of stock during the order processing
The order contain items with shipping restricted line items
User needs to take actions upon orders that got the status during the submission.

sending-to-production	Order is picked for sending to production. The status should be changed when the system receives updates from print providers.
in-production	Order has been received by the print providers successfully. Print providers start the fulfillment process on their side.
canceled	The order is canceled. No actions can be taken towards the order by the user.
fulfilled	All line items are fulfilled by all print providers. The last status for successful order fulfillment.
partially-fulfilled	At least one of the line items is fulfilled, but not all of them.
payment-not-received	The order could not be charged during the submission in our system. It can be retried by the merchant. The order waits for merchant actions.
had-issues	If an order encounters any issue during its lifecycle it will get this status. For instance, the shipping address is invalid.
shipping_method
REQUIRED
"shipping_method": 1
Method of shipping selected for the order, "1" is for standard shipping and "2" is for express priority shipping, "3" is for Printify Express shipping and "4" is for Economy shipping. Please note, that express order can only contain products eligible for express delivery. Similarly, economy order can only contain products eligible for economy delivery. More about shipping methods can be read here: Printify's shipping options

⚠	Please be aware that Printify Express Delivery is using carriers that might not be supported by all sales channels (e.g. Amazon, Tik Tok).
⚠	Please be aware that only the Product's and the Variant's eligibility (is_printify_express_eligible flag) is taken into account. Eligible but disabled products (is_printify_express_enabled flag) can still be ordered with Printify Express Delivery.
⚠	Please be aware that shipping method 4 (economy) will not be usable when creating a product with an order. Therefore, for this shipping method the product must already exist before placing an order on it.
Property value should be decoded based on the following table:

Code	Old version	Transitional version [active]	Final version
1	standard	standard	standard
2	express	express
priority	priority
3		printify_express	express
4	economy	economy	economy
The printify_express is a new shipping option that will later in the future change its name to the express. Current express option will be renamed to the priority name.

is_printify_express
READ-ONLY
"is_printify_express": true
Boolean value that indicates if the order is using Printify Express shipping.

is_economy_shipping
READ-ONLY
"is_economy_shipping": true
Boolean value that indicates if the order is using Economy shipping.

shipments
READ-ONLY
"shipments": [{
      "carrier": "usps",
      "number": "94001116990045395649372",
      "url": "http://example.com/94001116990045395649372",
      "delivered_at": "2017-04-18 13:24:28+00:00"
}]
Tracking details of the order after fulfillment. See shipment properties for reference.
created_at
READ-ONLY
"created_at": "2017-04-18 13:24:28+00:00"
The date and time the order was created. It is stored in ISO date format.
sent_to_production_at
READ-ONLY
"sent_to_production_at": "2017-04-18 13:24:28+00:00"
The date and time the order was sent to production. It is stored in ISO date format.
fulfilled_at
READ-ONLY
"fulfilled_at": "2017-04-18 13:24:28+00:00"
The date and time the order was fulfilled. It is stored in ISO date format.
printify_connect
READ-ONLY
"printify_connect": {
      "url": "https://example.com/printify_connect_hash", 
      "id": "printify_connect_hash"
}
Printify Connect data containing link to the order in the Printify Connect page and the unique hash for the order.
More about Printify Connect can be read in our Help Center or Blog.
Line item properties
product_id
READ-ONLY
"product_id": "5b05842f3921c9547531758d"
A unique string identifier for the product. Each id is unique across the Printify system.
variant_id
REQUIRED
READ-ONLY
"variant_id": 17887
A unique int identifier for the product variant from the blueprint. Each id is unique across the Printify system.
quantity
REQUIRED
"quantity": 1
Describes the number of said product ordered as an integer.
print_provider_id
REQUIRED
READ-ONLY
"print_provider_id": 5
A unique int identifier for the print provider. Each id is unique across the Printify system.
cost
READ-ONLY
"cost": 1050
Product variant's fulfillment cost in cents, integer value.
shipping_cost
READ-ONLY
"shipping_cost": 400
Product variant's shipment cost in cents, integer value.
status
READ-ONLY
"status": "in-production"
Specific line item fulfillment status:

Status	Definition
on-hold	
The item waits for user actions. Items get this status when:

The order is created.
The order fails at one of the checks in the submission process.
The order fails with payments.
in-production	Print provider received the item for production.
sending-to-production	Says that the order is picked for sending to production. The status is changed once the system receives updates from print providers.
has-issues	Line item encountered an issue during its lifecycle.
fulfilled	The item is fulfilled by the print provider.
canceled	The item is canceled.
metadata
READ-ONLY
"metadata": {
        "title": "18K gold plated Necklace",
        "price": 2200,
        "variant_label": "Golden indigocoin",
        "sku": "168699843",
        "country": "United States"
}
Other details about the specific product variant. See line item metadata properties for reference.
sent_to_production_at
READ-ONLY
"sent_to_production_at": "2017-04-18 13:24:28+00:00"
The date and time the product variant was sent to production. It is stored in ISO date format.
fulfilled_at
READ-ONLY
"fulfilled_at": "2017-04-18 13:24:28+00:00"
The date and time the product variant was fulfilled. It is stored in ISO date format.
Line item metadata properties
title
READ-ONLY
"title": "Product's title"
The name of the product.
price
READ-ONLY
"price": 1000
Retail price in cents, integer value.
variant_label
READ-ONLY
"variant_label": "Golden indigocoin"
Name of the product variant.
sku
READ-ONLY
"sku": "168699843"
A unique string identifier for the product variant.
country
READ-ONLY
"country": "United States"
Location of print provider handling fulfillment.
Metadata properties
order_type
READ-ONLY
"order_type": "external"
Describes the order type, can be external, manual, or sample.
shop_order_id
READ-ONLY
"shop_order_id": 1370762297
A unique integer identifier for the order in the external sales channel.
shop_order_label
READ-ONLY
"shop_order_id": "1370762297"
A unique string identifier for the order in the external sales channel.
shop_fulfilled_at
READ-ONLY
"shop_fulfilled_at": "2017-04-18 13:24:28+00:00"
The date and time the order was fulfilled. It is stored in ISO date format.
Shipment properties
carrier
READ-ONLY
"carrier": "usps"
Name of the shipping courier used to deliver the order to its recipient.
number
READ-ONLY
"number": "123"
A unique string tracking number from the shipping courier used to track the status of the shipment.
url
READ-ONLY
"url": "http://example.com/94001116990045395649372"
A unique string tracking link from the shipping courier used to track the status of the shipment.
delivered_at
READ-ONLY
"delivered_at": "2017-04-18 13:24:28+00:00"
The date and time the order was delivered. It is stored in ISO date format.
Order submission properties
external_id
REQUIRED
"external_id": "2750e210-39bb-11e9-a503-452618153e4a"
A unique string identifier from the sales channel specifying the order name or id.
label
OPTIONAL
"label": "000012"
Optional value to specify order label instead of using "external_id"
line_items
REQUIRED
"line_items": [{
      "product_id": "5bfd0b66a342bcc9b5563216",
      "variant_id": 17887,
      "quantity": 1
}]
Required for ordering existing products. Provide the product_id (Printify Product ID), variant_id (selected variant, e.g. 'White / XXL') and desired item quantity. If creating a product from the order is required, then additional attributes will need to be provided, specifically the blueprint_id and print_areas.
"line_items": [{
      "print_provider_id": 5,
      "blueprint_id": 9,
      "variant_id": 17887,
      "print_areas": {
        "front": "https://images.example.com/image.png"
      },
      "quantity": 1
}]
See product properties and variant properties for reference. Also, see print area properties for reference on print_areas for product creation during order submission. It is also possible to order existing products by providing the product variant's SKU alone.
"line_items": [{
      "sku": "MY-SKU",
      "quantity": 1
}]
See variant properties for reference.
shipping_method
REQUIRED
"shipping_method": 1
Required to specify what method of shipping is desired, "1" means standard shipping, "2" means priority shipping, "3" means printify express shipping and "4" means economy shipping. It is stored as an integer.
send_shipping_notification
BOOLEAN
"send_shipping_notification": false
A boolean for choosing whether or not to receive email notifications after an order is shipped.
address_to
REQUIRED
"address_to": {
    "first_name": "John",
    "last_name": "Smith",
    "email": "example@msn.com",
    "phone": "0574 69 21 90",
    "country": "BE",
    "region": "",
    "address1": "ExampleBaan 121",
    "address2": "45",
    "city": "Retie",
    "zip": "2470"
}
The delivery details of the order's recipient.
Print area properties
placeholder position and image url
REQUIRED
"print_areas": {
        "front": "https://images.example.com/image.png",
        "back": "https://images.example.com/image.png"
}
Required for creating products during order submission, See placeholder properties for reference. Instead of specifing the url, it is also possible to provide an array with image objects that have additional keys for the advanced positioning:

        "print_areas": {
          "front": [
            {
                "src": "https://images.example.com/image.png",
                "scale": 0.15,
                "x": 0.80,
                "y": 0.34,
                "angle": 215
            },
            {
                "src": "https://images.example.com/image2.png",
                "scale": 1,
                "x": 0.5,
                "y": 0.5,
                "angle": 0
            }
          ],
          "back": [
            {
                "src": "https://images.example.com/image3.png",
                "scale": 1,
                "x": 0.5,
                "y": 0.5,
                "angle": 0
            }
          ]
        }
      
Print details properties
Special print options
OPTIONAL

        "print_details": {
            "print_on_side": "mirror"
        }
    
Used to store properties for special cases like printing on canvas sides or clock separators, See print details properties for reference.
Endpoints
Retrieve a list of orders
GET	/v1/shops/{shop_id}/orders.json
limit
OPTIONAL
Results per page
(default: 10, maximum: 10)
page
OPTIONAL
Paginate through list of results
status
OPTIONAL
Filter results by order status
sku
OPTIONAL
Filter results by product SKU - response will contain only those orders that have at least one product with passed SKU
Retrieve all orders
GET /v1/shops/{shop_id}/orders.json
View Response
Retrieve limited results
GET /v1/shops/{shop_id}/orders.json?limit=1
View Response
Retrieve specific page from results.
GET /v1/shops/{shop_id}/orders.json?page=2
View Response
Filter results by order status.
GET /v1/shops/{shop_id}/orders.json?status=fulfilled
View Response
Filter results by product SKU.
GET /v1/shops/{shop_id}/orders.json?sku=168699843
View Response
Get order details by ID
GET	/v1/shops/{shop_id}/orders/{order_id}.json
Get order details by ID
GET /v1/shops/{shop_id}/orders/{order_id}.json
View Response
Submit an order
POST	/v1/shops/{shop_id}/orders.json
Order an existing product
POST /v1/shops/{shop_id}/orders.json
{
    "external_id": "2750e210-39bb-11e9-a503-452618153e4a",
    "label": "00012",
    "line_items": [
      {
        "product_id": "5bfd0b66a342bcc9b5563216",
        "variant_id": 17887,
        "quantity": 1
      }
    ],
    "shipping_method": 1,
    "is_printify_express": false,
    "is_economy_shipping": false,
    "send_shipping_notification": false,
    "address_to": {
      "first_name": "John",
      "last_name": "Smith",
      "email": "example@msn.com",
      "phone": "0574 69 21 90",
      "country": "BE",
      "region": "",
      "address1": "ExampleBaan 121",
      "address2": "45",
      "city": "Retie",
      "zip": "2470"
    }
  }
View Response
Create a product with an order (simple image positioning)
POST /v1/shops/{shop_id}/orders.json
{
    "external_id": "2750e210-39bb-11e9-a503-452618153e5a",
    "label": "00012",
    "line_items": [
      {
        "print_provider_id": 5,
        "blueprint_id": 9,
        "variant_id": 17887,
        "print_areas": {
          "front": "https://images.example.com/image.png"
        },
        "quantity": 1
      }
    ],
    "shipping_method": 1,
    "is_printify_express": false,
    "is_economy_shipping": false,
    "send_shipping_notification": false,
    "address_to": {
      "first_name": "John",
      "last_name": "Smith",
      "email": "example@msn.com",
      "phone": "0574 69 21 90",
      "country": "BE",
      "region": "",
      "address1": "ExampleBaan 121",
      "address2": "45",
      "city": "Retie",
      "zip": "2470"
    }
  }
View Response
Create a product with an order (advanced image positioning)
POST /v1/shops/{shop_id}/orders.json
{
    "external_id": "2750e210-39bb-11e9-a503-452618153e5a",
    "label": "00012",
    "line_items": [
      {
        "print_provider_id": 5,
        "blueprint_id": 9,
        "variant_id": 17887,
        "print_areas": {
          "front": [
            {
                "src": "https://images.example.com/image.png",
                "scale": 0.15,
                "x": 0.80,
                "y": 0.34,
                "angle": 0.34
            },
            {
                "src": "https://images.example.com/image.png",
                "scale": 1,
                "x": 0.5,
                "y": 0.5,
                "angle": 1
            }
          ]
        },
        "quantity": 1
      }
    ],
    "shipping_method": 1,
    "is_printify_express": false,
    "is_economy_shipping": false,
    "send_shipping_notification": false,
    "address_to": {
      "first_name": "John",
      "last_name": "Smith",
      "email": "example@msn.com",
      "phone": "0574 69 21 90",
      "country": "BE",
      "region": "",
      "address1": "ExampleBaan 121",
      "address2": "45",
      "city": "Retie",
      "zip": "2470"
    }
  }
View Response
Create a product with an order (with specifying print details for printing on sides)
POST /v1/shops/{shop_id}/orders.json

    {
        "external_id": "2750e210-39bb-11e9-a503-452618153e5a",
        "label": "00012",
        "line_items": [
          {
            "print_provider_id": 5,
            "blueprint_id": 9,
            "variant_id": 17887,
            "print_areas": {
              "front": "https://images.example.com/image.png"
            },
            "print_details": {
                "print_on_side": "mirror"
            },
            "quantity": 1
          }
        ],
        "shipping_method": 1,
        "is_printify_express": false,
        "is_economy_shipping": false,
        "send_shipping_notification": false,
        "address_to": {
          "first_name": "John",
          "last_name": "Smith",
          "email": "example@msn.com",
          "phone": "0574 69 21 90",
          "country": "BE",
          "region": "",
          "address1": "ExampleBaan 121",
          "address2": "45",
          "city": "Retie",
          "zip": "2470"
    }
  }
View Response
Order an existing product using only an SKU
POST /v1/shops/{shop_id}/orders.json
"external_id": "2750e210-39bb-11e9-a503-452618153e6a",
    "label": "00012",
    "line_items": [
      {
        "sku": "MY-SKU",
        "quantity": 1
      }
    ],
    "shipping_method": 1,
    "is_printify_express": false,
    "is_economy_shipping": false,
    "send_shipping_notification": false,
    "address_to": {
      "first_name": "John",
      "last_name": "Smith",
      "email": "example@msn.com",
      "phone": "0574 69 21 90",
      "country": "BE",
      "region": "",
      "address1": "ExampleBaan 121",
      "address2": "45",
      "city": "Retie",
      "zip": "2470"
    }
}
View Response
Submit a Printify Express order
POST	/v1/shops/{shop_id}/orders/express.json
Order an existing product with Printify Express Delivery
This API method creates one or two separate orders using the following logic:

If none of the line items are Printify Express eligible: one order with "fulfilment_type": "ordinary"
If all of the line items are Printify Express eligible: one order with "fulfilment_type": "express"
If at least one line item is Printify Express eligible, and at least one isn't: two separate orders, one express, and one ordinary
Read more about Printify Express Delivery in a dedicated Help center section.

⚠	address_to.email and address_to.phone fields are required for Printify Express eligibility.
⚠	
The endpoint works only with already existing products.

Please be aware that Printify Express Delivery is using carriers that might not be supported by all sales channels (e.g. Amazon, Tik Tok).

⚠	
Please be aware that only the Product's and the Variant's eligibility (is_printify_express_eligible flag) is taken into account. Eligible but disabled products (is_printify_express_enabled flag) can still be ordered with Printify Express Delivery.

POST /v1/shops/{shop_id}/orders/express.json
{
  "external_id": "2750e210-39bb-11e9-a503-452618153e4a",
  "label": "00012",
  "line_items": [
    {
      "product_id": "5b05842f3921c9547531758d",
      "variant_id": 12359,
      "quantity": 1
    },
    {
      "product_id": "5b05842f3921c34764fa478bc",
      "variant_id": 17887,
      "quantity": 1
    }
  ],
  "shipping_method": 3,
  "send_shipping_notification": false,
  "address_to": {
    "first_name": "John",
    "last_name": "Smith",
    "email": "example@example.com",
    "phone": "0574 69 21 90",
    "country": "BE",
    "region": "",
    "address1": "ExampleBaan 121",
    "address2": "45",
    "city": "Retie",
    "zip": "2470"
  }
}
View Response
Send an existing order to production
POST	/v1/shops/{shop_id}/orders/{order_id}/send_to_production.json
Send an existing order to production
POST /v1/shops/{shop_id}/orders/{order_id}/send_to_production.json
View Response
Calculate the shipping cost of an order
POST	/v1/shops/{shop_id}/orders/shipping.json
Calculate the shipping cost of an order
POST /v1/shops/{shop_id}/orders/shipping.json
{
    "line_items": [{
        "product_id": "5bfd0b66a342bcc9b5563216",
        "variant_id": 17887,
        "quantity": 1
    },{
        "print_provider_id": 5,
        "blueprint_id": 9,
        "variant_id": 17887,
        "quantity": 1
    },{
        "sku": "MY-SKU",
        "quantity": 1
    }],
    "address_to": {
        "first_name": "John",
        "last_name": "Smith",
        "email": "example@msn.com",
        "phone": "0574 69 21 90",
        "country": "BE",
        "region": "",
        "address1": "ExampleBaan 121",
        "address2": "45",
        "city": "Retie",
        "zip": "2470"
    }
}
Response


{
    "standard": 1000,
    "express": 5000,
    "priority": 5000,
    "printify_express": 799,
    "economy": 399
}
    
Response contains the shipping options that are defined in the following table:

Code	Old version	Transitional version [active]	Final version
1	standard	standard	standard
2	express	express
priority	priority
3		printify_express	express
4	economy	economy	economy
The printify_express is a new shipping option that will later in the future change its name to the express. Current express option will be renamed to the priority name.

Cancel an order
This request will only be accepted if the order to be canceled has the status "on-hold" or "payment-not-received".

POST	/v1/shops/{shop_id}/orders/{order_id}/cancel.json
Cancel an order
POST /v1/shops/{shop_id}/orders/{order_id}/cancel.json
View Response
Structure
Structure of Orders resource with possible transitions between endpoints.

orders structure

Making Order
Flow of transitions between resources for making an order.

making order

Common error cases
POST	/v1/shops/{shop_id}/orders.json
Common error cases
POST /v1/shops/{shop_id}/orders.json
400 Invalid address validation error example (See HTTP Status Codes below)
View Response
Uploads
Artwork added to a Printify Product can be saved in the Media library to be reused on additional products.

You can use this API to directly add files to the media library, and later use image IDs when creating or modifying products.

On this page:

What you can do with the uploads resource
Image properties
Endpoints
Structure
Common Error cases
What you can do with the uploads resource
The Printify Public API lets you do the following with the Uploads resource:

GET /v1/uploads.json
Retrieve a list of uploaded images
GET /v1/uploads/{image_id}.json
Retrieve an uploaded image by id
POST /v1/uploads/images.json
Upload an image
POST /v1/uploads/{image_id}/archive.json
Archive an uploaded image
Image properties
id
READ-ONLY
"id": "5e16d66791287a0006e522b2"
A unique string identifier for the image. Each id is unique across the Printify system.
file_name
READ-ONLY
"file_name": "Image's file name"
The file name of the image.
height
READ-ONLY
"height": 5979
The height of the image in pixels.
width
READ-ONLY
"width": 17045
The width of the image in pixels.
size
READ-ONLY
"size": 1138575
The file size of the image in bytes.
mime_type
READ-ONLY
"mime_type": "image/png"
The media type of the image file.
preview_url
READ-ONLY
"preview_url": "https://example.com/artwork"
A url to preview the image.
upload_time
READ-ONLY
"upload_time": "2020-01-09 07:29:43"
The date and time the image was uploaded in ISO date format.
Endpoints
Retrieve a list of uploaded images
GET	/v1/uploads.json
limit
OPTIONAL
Results per page
(default: 10, maximum: 100)
page
OPTIONAL
Paginate through list of results
Retrieve all uploaded images
GET /v1/uploads.json
View Response
Retrieve specific page from results
GET /v1/uploads.json?page=2
View Response
Retrieve limited results
GET /v1/uploads.json?limit=1
View Response
Retrieve an uploaded image by id
GET	/v1/uploads/{image_id}.json
Retrieve an uploaded image by id
GET /v1/uploads/{image_id}.json
View Response
Upload an image
Upload image files either via image URL or image file base64-encoded contents. The file will be stored in the Merchant's account Media Library.

⚠	We highly recommend using upload via image URL for files larger than 5MB.
Upload via image URL is the future-proof solution, as we plan to drop support for base64-encoded content uploads larger than 5MB in the future.
POST	/v1/uploads/images.json
Upload image to a Printify account's media library
POST /v1/uploads/images.json
Body parameter (upload image by URL)
{
    "file_name": "1x1-ff00007f.png",
    "url": "http://png-pixel.com/1x1-ff00007f.png"
}
Body parameter (upload image by base64-encoded contents)
{
    "file_name": "image.png",
    "contents": "base-64-encoded-content"
}
View Response
Archive an uploaded image
POST	/v1/uploads/{image_id}/archive.json
Archive an uploaded image
POST /v1/uploads/{image_id}/archive.json
View Response
Structure
Structure of Image Uploads resource with possible transitions between endpoints.

uploads structure

Common Error cases
When uploading images to the library, you may encounter errors. These are commonly due to download errors, incorrect file formats, or your image being too large. If these are the case, you will receive messages similar to these outlined here.

POST	/v1/uploads/images.json
Common error cases
POST /v1/uploads/images.json
400 Image download error example (See HTTP Status Codes below)
View Response

400 Image too large error example (See HTTP Status Codes below)
View Response

400 Unsupported file format error example (See HTTP Status Codes below)
View Response
Events
Events are generated by some resources when certain actions are completed, such as the creation of a product, the fulfillment of an order. By requesting events, your app can know when certain actions have occurred in the shop.

On this page:

Shop events
Product events
Order events
Event properties
Resource properties
Resource data examples
Shop resource data examples
Product resource data examples
Order resource data examples
Payload examples
Shop events
Event	Description
shop:disconnected	The shop was disconnected.
Product events
Event	Description
product:deleted	The product was deleted.
product:publish:started	The product publishing was started.
Order events
Event	Description
order:created	The order was created.
order:updated	The order's status was updated.
order:sent-to-production	The order was sent to production.
order:shipment:created	Some/all items have been fulfilled.
order:shipment:delivered	Some/all items have been delivered.
Event properties
id	
"id": "653b6be8-2ff7-4ab5-a7a6-6889a8b3bbf5"
A unique string identifier for the event. Each id is unique across the Printify system.
type	
"type": "order:created"
The type of event that occurred. Different resources generate different types of event.
created_at	
"created_at": "2017-04-18 13:24:28+00:00"
The date and time when the event was triggered.
resource	
"resource": {
     "id": "653b6be8-2ff7-4ab5-a7a6-6889a8b3bbf5",
     "type": "product",
     "data":  {
        "shop_id": 1234567,
        "reason": "Request timed out"
    }
}
Information about the resource that triggered the event. Check Resource properties for reference.
Resource properties
id	
"id": "5cb87a8cd490a2ccb256cec4"
A unique string identifier for the resource. Each id is unique across the Printify system.
type	
"type": "product"
Resource type, currently valid types are shop, product and order.
data	
"data": {
    "shop_id": 1234567,
    "reason": "Request timed out"
}
For more information see Resource data examples.
Resource data examples
Shop events
shop:disconnected	No resource data is sent.
Product events
product:deleted	No resource data is sent.
product:publish:started	The values for the action property determine the resource data payload, the values can be "create", "update", or "delete". For "create" and "update" actions, the payload is as follows:
"data": {
    "shop_id": 1234567,
    "publish_details": {
        "title": true,
        "description": true,
        "images": true,
        "variants": true,
        "tags": true,
        "key_features": true,
        "shipping_template": true
    },
    "action": "create",
}
For the "delete" action, the payload is as follows:
"data": {
    "action": "delete"
}
For reference on what other properties mean, check Publishing properties.
Order events
order:created	No resource data is sent with this event.
order:updated	
"data": {
    "shop_id": 815256,
    "status": "in-production"
}
For information on what production statuses can be expected, check Order properties for reference.
order:shipment:created	
"data": {
    "shop_id": 815256,
    "shipped_at": "2017-04-18 13:24:28+00:00",
    "carrier": {
      "code": "USPS",
      "tracking_number": "9400110200828911663274"
    },
    "skus": [
      "6220"
  ]
}
order:shipment:delivered	
"data": {
    "shop_id": 815256,
    "delivered_at": "2017-04-18 13:24:28+00:00",
    "carrier": {
      "code": "USPS",
      "tracking_number": "9400110200828911663274"
    },
    "skus": [
      "6220"
  ]
}
order:sent-to-production	No resource data is sent with this event.
Payload examples
shop:disconnected	

{
  "id": "653b6be8-2ff7-4ab5-a7a6-6889a8b3bbf5",
  "type": "shop:disconnected",
  "created_at": "2022-05-17 15:00:00+00:00",
  "resource": {
    "id": 815256,
    "type": "shop",
    "data": null
  }
}
      
product:deleted	

{
  "id": "653b6be8-2ff7-4ab5-a7a6-6889a8b3bbf5",
  "type": "product:deleted",
  "created_at": "2022-05-17 15:00:00+00:00",
  "resource": {
    "id": "5cb87a8cd490a2ccb256cec4",
    "type": "product",
    "data": {
      "shop_id": 815256
    }
  }
}
      
product:publish:started	

{
  "id": "653b6be8-2ff7-4ab5-a7a6-6889a8b3bbf5",
  "type": "product:publish:started",
  "created_at": "2022-05-17 15:00:00+00:00",
  "resource": {
    "id": "5cb87a8cd490a2ccb256cec4",
    "type": "product",
    "data": {
      "shop_id": 815256,
      "publish_details": {
        "title": true,
        "variants": false,
        "description": true,
        "tags": true,
        "images": false,
        "key_features": false,
        "shipping_template": true
      },
      "action": "create",
      "out_of_stock_publishing": 0
    }
  }
}
      
order:created	

{
  "id": "653b6be8-2ff7-4ab5-a7a6-6889a8b3bbf5",
  "type": "order:created",
  "created_at": "2022-05-17 15:00:00+00:00",
  "resource": {
    "id": "5a96f649b2439217d070f507",
    "type": "order",
    "data": {
      "shop_id": 815256
    }
  }
}
      
order:updated	

{
  "id": "653b6be8-2ff7-4ab5-a7a6-6889a8b3bbf5",
  "type": "order:updated",
  "created_at": "2022-05-17 15:00:00+00:00",
  "resource": {
    "id": "5a96f649b2439217d070f507",
    "type": "order",
    "data": {
      "shop_id": 815256,
      "status": "in-production"
    }
  }
}
      
order:shipment:created	

{
  "id": "653b6be8-2ff7-4ab5-a7a6-6889a8b3bbf5",
  "type": "order:shipment:created",
  "created_at": "2022-05-17 15:00:00+00:00",
  "resource": {
    "id": "5a96f649b2439217d070f507",
    "type": "order",
    "data": {
      "shop_id": 815256,
      "shipped_at": "2022-05-17 15:00:00+00:00",
      "carrier": {
        "code": "USPS",
        "tracking_number": "9400110200828911663274",
        "tracking_url": "https://example.com/track/9400110200828911663274"
      },
      "skus": [
        "6202"
      ]
    }
  }
}
      
order:shipment:delivered	

{
  "id": "653b6be8-2ff7-4ab5-a7a6-6889a8b3bbf5",
  "type": "order:shipment:delivered",
  "created_at": "2022-05-17 15:00:00+00:00",
  "resource": {
    "id": "5a96f649b2439217d070f507",
    "type": "order",
    "data": {
      "shop_id": 815256,
      "delivered_at": "2022-05-17 15:00:00+00:00",
      "carrier": {
        "code": "USPS",
        "tracking_number": "9400110200828911663274",
        "tracking_url": "https://example.com/track/9400110200828911663274"
      },
      "skus": [
        "6202"
      ]
    }
  }
}
      
order:sent-to-production	

{
  "id": "653b6be8-2ff7-4ab5-a7a6-6889a8b3bbf5",
  "type": "order:sent-to-production",
  "created_at": "2022-05-17 15:00:00+00:00",
  "resource": {
    "id": "5a96f649b2439217d070f507",
    "type": "order",
    "data": {
      "shop_id": 815256
    }
  }
}
      
Webhooks
You can use webhook subscriptions to receive notifications about particular events in a shop. After you've subscribed to a webhook, you can let your app execute code immediately after specific events occur in shops that have your app connected, instead of having to make API calls periodically to check their status. For example, you can rely on webhooks to trigger an action in your app when a merchant creates a new product in a store. By using webhooks subscriptions you can make fewer API calls overall, which makes sure that your apps are more efficient and update quickly. For more information what actually gets sent by a webhook check Event properties and Resource data examples.

On this page:

Webhook rules to follow
What you can do with the webhooks resource
Webhook properties
Webhook endpoints
Securing your Webhooks
Webhook rules to follow
To ensure that your webhook works correctly, follow these good practices:

Printify will send a POST request to the URL you specify when the event occurs.
This POST request will contain a JSON payload with information about the event.
The expected response is a 200 OK.
In case of a 4xx or 5xx response, Printify will retry the request up to 3 times, after which the webhook will be blocked for 1 hour.
If the webhook is blocked, no new requests will be sent to the URL until the block is lifted.
What you can do with the Webhooks resource
The Printify Public API lets you do the following with the Webhook resource:

GET /v1/shops/{shop_id}/webhooks.json
Retrieve a list of webhooks
POST /v1/shops/{shop_id}/webhooks.json
Create a new webhook
PUT /v1/shops/{shop_id}/webhooks/{webhook_id}.json
Modify a webhook
DELETE /v1/shops/{shop_id}/webhooks/{webhook_id}.json
Delete a webhook
Webhook properties
id
READ-ONLY
"id": "5cb87a8cd490a2ccb256cec4"
A unique string identifier for the webhook. Each id is unique across the Printify system.
topic
REQUIRED
READ-ONLY
"topic": "product:publish:started"
Event that triggers the webhook. See Events for reference. Can't be changed.
url
REQUIRED
"url": "https://example.com/webhooks"
URI where the webhook subscription should send the POST request when the event occurs.
shop_id
READ-ONLY
"shop_id": 1
Id of merchant's store.
secret
OPTIONAL
"secret": "optional-secret-value"
Secret that will be used to sign requests for webhook. See Securing your webhooks for more information.
Webhook endpoints
Retrieve a list of webhooks
GET	/v1/shops/{shop_id}/webhooks.json
Retrieve a list of webhooks
GET /v1/shops/{shop_id}/webhooks.json
View Response
Create a new webhook
POST	/v1/shops/{shop_id}/webhooks.json
Create a new webhook
POST /v1/shops/{shop_id}/webhooks.json
{
    "topic": "order:created",
    "url": "https://example.com/webhooks/order/created"
}
View Response
Modify a webhook
PUT	/v1/shops/{shop_id}/webhooks/{webhook_id}.json
Modify a webhook
PUT /v1/shops/{shop_id}/webhooks/{webhook_id}.json
{
    "url": "https://example.com/callback/order/created"
}
View Response
Delete a webhook
DELETE	/v1/shops/{shop_id}/webhooks/{webhook_id}.json
Delete a webhook
DELETE /v1/shops/{shop_id}/webhooks/{webhook_id}.json
View Response
Securing your Webhooks
Once your server is configured to receive payloads, it'll listen for any payload sent to the endpoint you configured. For security reasons, you probably want to limit requests to those coming from Printify.

There are a few ways to go about this - for example, you could opt to whitelist requests from Printify's IP address - but a far easier method is to set up a secret token and validate the information.

Summary:

Setting your shared secret with Printify
Accessing the Secret from your backend
Validating payloads from Printify
Setting your shared secret with Printify
You can generate the secret by running 'openssl rand -hex 20'.

When your secret token is set, Printify will use it to create a hash signature with each payload body. Printify uses an HMAC hexdigest to compute the hash sha256 signature with your provided secret.

Secret example

    7afa37fd47d7a52ea644382e04962a83c16aef62
This payload body signature is passed along with each request in the headers as X-Pfy-Signature. The signature format is: sha256={digest}.

Signature example

    x-pfy-signature: sha256=4260d30ec4ee2a17181ae5072c846d8dfcb5ceb195e24de055fd9a21d8c6648f
Accessing the Secret from your backend
Next, set up a SECRET_TOKEN environment variable on your server that stores this token. Never hardcode the secret into your app!

Setting the SECRET_TOKEN environment variable example

    $ export SECRET_TOKEN=your_token
Validating payloads from Printify
Next, compute a request body hash using your SECRET_TOKEN, and ensure that the hash from Printify matches. Printify uses an HMAC hexdigest to compute the hash. Always use "constant time" string comparisons, which renders it safe from certain timing attacks against regular equality operators.

Validation sample (python)

    import os
    import hmac
    
    def sha256hash(request):
        hash = hmac.new(os.environ['SECRET_TOKEN'].encode('utf-8'),
                        request.data.encode('utf-8'), 
                        'sha256')
        return 'sha256=' + hash.hexdigest()
    
    
    def secure_compare(a, b):
        return hmac.compare_digest(a, b)
    
    
    print('%r' % secure_compare(request.headers['x-pfy-signature'],
                                sha256hash(request)))
V2 API Reference
The second version of the API is organized around the JSON:API specification. This version of the API is designed to be more consistent and predictable, and to provide a better foundation for future improvements. It follows JSON API standard on pagination, linking and can support the filtering if it is mentioned in the endpoint documentation.

New features and improvements are being added to the V2 API, and we encourage you to use it for new integrations. The V1 API will continue to be supported, but new features will only be added to the V2 API.

The V2 API is available at the following base URL: https://api.printify.com/v2/.

The Economy Shipping costs listing is available only in the V2 API.

Catalog V2
Through the Catalog resource you can see all of the products, product variants, variant options and print providers available in the Printify catalog.

Products in the Printify catalog are referred to as blueprints (only after user artwork has been added, they are referred to as products).

Every blueprint in the Printify catalog has multiple Print Providers that offer that blueprint. In addition to general differences between Print Providers including location and print technology employed, each Print Provider also offers different colors, sizes, print areas and prices.

Each Print Provider's blueprint has specific option (e.g. color, size) combinations known as variants. Variants also contain information on a products' available print areas and sizes.

On this page:

What you can do with the catalog resource
Shipping properties
Endpoints
What you can do with the catalog resource
The Printify Public API lets you do the following with the Catalog resource:

GET /v2/catalog/blueprints/{blueprint_id}/print_providers/{print_provider_id}/shipping.json
Retrieve the list of available shipping for all variants of a blueprint from a specific print provider
GET /v2/catalog/blueprints/{blueprint_id}/print_providers/{print_provider_id}/shipping/standard.json
Retrieve the standard shipping handling time and shipping costs for all variants of a blueprint from a specific print provider.
GET /v2/catalog/blueprints/{blueprint_id}/print_providers/{print_provider_id}/shipping/priority.json
Retrieve the priority shipping handling time and shipping costs for all variants of a blueprint from a specific print provider.
GET /v2/catalog/blueprints/{blueprint_id}/print_providers/{print_provider_id}/shipping/express.jsonRetrieve the express shipping handling time and shipping costs for all variants of a blueprint from a specific print provider.
GET /v2/catalog/blueprints/{blueprint_id}/print_providers/{print_provider_id}/shipping/economy.json
Retrieve the economy shipping handling time and shipping costs for all variants of a blueprint from a specific print provider.
Shipping list attributes
Attribute	Description
name
READ-ONLY
"name": "standard"
The shipping type (method) name
Specific Shipping attributes
Attribute	Description
shippingType
READ-ONLY
"shippingType": "economy"
The shipping type (method) name
country
READ-ONLY
"country": {
  "code": "US"
}
The code of the country the shipping costs apply to. Can be also REST_OF_THE_WORLD which means it applies to all the countries that don't have the costs specified.
variantId
READ-ONLY
"variantId": 1
Variant ID for which this shipping is available
shippingPlanId
READ-ONLY
"shippingPlanId": "65a7c0825b50fcd56a018e02"
Internal Shipping Plan ID that is used to calculate shipping costs
handlingTime
READ-ONLY
"handlingTime": {
  "from": 4,
  "to": 8
}
Delivery time in days
shippingCost
READ-ONLY
"shippingCost": {
  "firstItem": {
      "amount": 399,
      "currency": "USD"
  },
  "additionalItems": {
      "amount": 219,
      "currency": "USD"
  }
Shipping cost for first, and potentially additional items. Returned in cents (1/100), for example: 399 = $3.99.
Endpoints
Retrieve available shipping list information
GET	/v2/catalog/blueprints/{blueprint_id}/print_providers/{print_provider_id}/shipping.json
Retrieve available shipping list information
GET /v2/catalog/blueprints/{blueprint_id}/print_providers/{print_provider_id}/shipping.json
View Response
Retrieve specific shipping method information
GET	/v2/catalog/blueprints/{blueprint_id}/print_providers/{print_provider_id}/shipping/standard.json
Retrieve standard shipping method information
GET /v2/catalog/blueprints/{blueprint_id}/print_providers/{print_provider_id}/shipping/standard.json
View Response
GET	/v2/catalog/blueprints/{blueprint_id}/print_providers/{print_provider_id}/shipping/priority.json
Retrieve priority shipping method information
GET /v2/catalog/blueprints/{blueprint_id}/print_providers/{print_provider_id}/shipping/priority.json
View Response
GET	/v2/catalog/blueprints/{blueprint_id}/print_providers/{print_provider_id}/shipping/express.json
Retrieve express shipping method information
GET /v2/catalog/blueprints/{blueprint_id}/print_providers/{print_provider_id}/shipping/express.json
View Response
GET	/v2/catalog/blueprints/{blueprint_id}/print_providers/{print_provider_id}/shipping/economy.json
Retrieve economy shipping method information
GET /v2/catalog/blueprints/{blueprint_id}/print_providers/{print_provider_id}/shipping/economy.json
View Response
HTTP Status Codes
Printify API relies heavily on standard HTTP response codes codes. Please find the brief summary of status codes used below.

Success
Code	Name	Description
200	OK	Request completed successfully.
201	Created	The request has been fulfilled and has resulted in one or more new resources being created.
202	Accepted	The request has been accepted for processing, but the processing has not been completed.
204	No Content	Indicates that the server has successfully fulfilled the request and that there is no content to send in the response payload body.
User error codes
These errors generally indicate a problem on the client side. If you are getting one of these, check your code and the request details.

Code	Name	Description
400	Bad Request	The request encoding is invalid; the request can't be parsed as a valid JSON.
401	Unauthorized	Accessing a protected resource without authorization or with invalid credentials.
402	Payment Required	The account associated with the API key making requests hits a quota that can be increased by upgrading the Printify API account plan.
403	Forbidden	Accessing a protected resource with API credentials that don't have access to that resource.
404	Not Found	Route or resource is not found. This error is returned when the request hits an undefined route, or if the resource doesn't exist (e.g. has been deleted).
413	Request Entity Too Large	The request exceeded the maximum allowed payload size. You shouldn't encounter this under normal use.
422	Invalid Request	The request data is invalid. This includes most of the base-specific validations. You will receive a detailed error message and code pointing to the exact issue.
429	Too Many Requests	Too Many Requests response status code indicates you have sent too many requests in a given amount of time ("rate limiting").
Server error codes
These errors generally represent an error on our side. In the event of a 5xx error code, detailed information about the error will be automatically recorded, and Printify's developers will be notified.

Code	Name	Description
500	Internal Server Error	The server encountered an unexpected condition.
502	Bad Gateway	Printify's servers are restarting or an unexpected outage is in progress. You should generally not receive this error, and requests are safe to retry.
503	Service Unavailable	The server could not process your request in time. The server could be temporarily unavailable, or it could have timed out processing your request. You should retry the request with backoffs.
History