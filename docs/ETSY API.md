SellerTaxonomy
getSellerTaxonomyNodes
General Release
Report bug
This endpoint is ready for production use.

Retrieves the full hierarchy tree of seller taxonomy nodes.

Authorizations:
api_key
Responses
200 List the full hierarchy tree of seller taxonomy nodes.
500 The server encountered an internal error. See the error message for details.
503 The service is unavailable

get
/v3/application/seller-taxonomy/nodes

Response samples
200500503
Content type
application/json

Copy
Expand allCollapse all
{
"count": 0,
"results": [
{}
]
}
getPropertiesByTaxonomyId
General Release
Report bug
This endpoint is ready for production use.

Retrieves a list of product properties, with applicable scales and values, supported for a specific seller taxonomy ID.

Authorizations:
api_key
path Parameters
taxonomy_id
required
integer <int64> >= 1
The unique numeric ID of an Etsy taxonomy node, which is a metadata category for listings organized into the seller taxonomy hierarchy tree. For example, the "shoes" taxonomy node (ID: 1429, level: 1) is higher in the hierarchy than "girls' shoes" (ID: 1440, level: 2). The taxonomy nodes assigned to a listing support access to specific standardized product scales and properties. For example, listings assigned the taxonomy nodes "shoes" or "girls' shoes" support access to the "EU" shoe size scale with its associated property names and IDs for EU shoe sizes, such as property value_id:"1394", and name:"38".

Responses
200 A list of product properties, with applicable scales and values.
400 There was a problem with the request data. See the error message for details.
404 A resource could not be found. See the error message for details.
500 The server encountered an internal error. See the error message for details.

get
/v3/application/seller-taxonomy/nodes/{taxonomy_id}/properties

Response samples
200400404500
Content type
application/json

Copy
Expand allCollapse all
{
"count": 0,
"results": [
{}
]
}
ShopListing
createDraftListing
General Release
Report bug
This endpoint is ready for production use.

Creates a physical draft listing product in a shop on the Etsy channel.

Authorizations:
api_keyoauth2 (listings_w)
path Parameters
shop_id
required
integer <int64> >= 1
The unique positive non-zero numeric ID for an Etsy Shop.

Request Body schema: application/x-www-form-urlencoded
quantity
required
integer
The positive non-zero number of products available for purchase in the listing. Note: The listing quantity is the sum of available offering quantities. You can request the quantities for individual offerings from the ListingInventory resource using the getListingInventory endpoint.

title
required
string
The listing's title string. When creating or updating a listing, valid title strings contain only letters, numbers, punctuation marks, mathematical symbols, whitespace characters, ™, ©, and ®. (regex: /[^\p{L}\p{Nd}\p{P}\p{Sm}\p{Zs}™©®]/u) You can only use the %, :, & and + characters once each.

description
required
string
A description string of the product for sale in the listing.

price
required
number <float>
The positive non-zero price of the product. (Sold product listings are private) Note: The price is the minimum possible price. The getListingInventory method requests exact prices for available offerings.

who_made
required
string
Enum: "i_did" "someone_else" "collective"
An enumerated string indicating who made the product. Helps buyers locate the listing under the Handmade heading. Requires 'is_supply' and 'when_made'.

when_made
required
string
Enum: "made_to_order" "2020_2025" "2010_2019" "2006_2009" "before_2006" "2000_2005" "1990s" "1980s" "1970s" "1960s" "1950s" "1940s" "1930s" "1920s" "1910s" "1900s" "1800s" "1700s" "before_1700"
An enumerated string for the era in which the maker made the product in this listing. Helps buyers locate the listing under the Vintage heading. Requires 'is_supply' and 'who_made'.

taxonomy_id
required
integer <int64> >= 1
The numerical taxonomy ID of the listing. See SellerTaxonomy and BuyerTaxonomy for more information.

shipping_profile_id	
integer <int64> >= 1 Nullable
The numeric ID of the shipping profile associated with the listing. Required when listing type is physical.

return_policy_id	
integer <int64> >= 1 Nullable
The numeric ID of the Return Policy.

materials	
Array of strings Nullable
A list of material strings for materials used in the product. Valid materials strings contain only letters, numbers, and whitespace characters. (regex: /[^\p{L}\p{Nd}\p{Zs}]/u) Default value is null.

shop_section_id	
integer <int64> >= 1 Nullable
The numeric ID of the shop section for this listing. Default value is null.

processing_min	
integer Nullable
The minimum number of days required to process this listing. Default value is null.

processing_max	
integer Nullable
The maximum number of days required to process this listing. Default value is null.

readiness_state_id	
integer <int64> >= 1 Nullable
The numeric ID of the processing profile associated with the listing. Required when listing type is physical.

tags	
Array of strings Nullable
A comma-separated list of tag strings for the listing. When creating or updating a listing, valid tag strings contain only letters, numbers, whitespace characters, -, ', ™, ©, and ®. (regex: /[^\p{L}\p{Nd}\p{Zs}-'™©®]/u) Default value is null.

styles	
Array of strings Nullable
An array of style strings for this listing, each of which is free-form text string such as "Formal", or "Steampunk". When creating or updating a listing, the listing may have up to two styles. Valid style strings contain only letters, numbers, and whitespace characters. (regex: /[^\p{L}\p{Nd}\p{Zs}]/u) Default value is null.

item_weight	
number <float> [ 0 .. 1.79769313486e+308 ] Nullable
The numeric weight of the product measured in units set in 'item_weight_unit'. Default value is null. If set, the value must be greater than 0.

item_length	
number <float> [ 0 .. 1.79769313486e+308 ] Nullable
The numeric length of the product measured in units set in 'item_dimensions_unit'. Default value is null. If set, the value must be greater than 0.

item_width	
number <float> [ 0 .. 1.79769313486e+308 ] Nullable
The numeric width of the product measured in units set in 'item_dimensions_unit'. Default value is null. If set, the value must be greater than 0.

item_height	
number <float> [ 0 .. 1.79769313486e+308 ] Nullable
The numeric height of the product measured in units set in 'item_dimensions_unit'. Default value is null. If set, the value must be greater than 0.

item_weight_unit	
string Nullable
Enum: "oz" "lb" "g" "kg"
A string defining the units used to measure the weight of the product. Default value is null.

item_dimensions_unit	
string Nullable
Enum: "in" "ft" "mm" "cm" "m" "yd" "inches"
A string defining the units used to measure the dimensions of the product. Default value is null.

is_personalizable	
boolean
When true, this listing is personalizable. The default value is null.

personalization_is_required	
boolean
When true, this listing requires personalization. The default value is null. Will only change if is_personalizable is 'true'.

personalization_char_count_max	
integer
This is an integer value representing the maximum length for the personalization message entered by the buyer. Will only change if is_personalizable is 'true'.

personalization_instructions	
string
A string representing instructions for the buyer to enter the personalization. Will only change if is_personalizable is 'true'.

production_partner_ids	
Array of integers <int64> Nullable
An array of unique IDs of production partner ids.

image_ids	
Array of integers <int64> Nullable
An array of numeric image IDs of the images in a listing, which can include up to 10 images.

is_supply	
boolean
When true, tags the listing as a supply product, else indicates that it's a finished product. Helps buyers locate the listing under the Supplies heading. Requires 'who_made' and 'when_made'.

is_customizable	
boolean
When true, a buyer may contact the seller for a customized order. The default value is true when a shop accepts custom orders. Does not apply to shops that do not accept custom orders.

should_auto_renew	
boolean
When true, renews a listing for four months upon expiration.

is_taxable	
boolean
When true, applicable shop tax rates apply to this listing at checkout.

type	
string
Enum: "physical" "download" "both"
An enumerated type string that indicates whether the listing is physical or a digital download.

legacy	
boolean
This parameter needed to enable new parameters and response values related to processing profiles.

Responses
201 A single ShopListing
400 There was a problem with the request data. See the error message for details.
401 The request lacks valid authentication credentials. See the error message for details.
403 The request attempted to perform an operation it is not allowed to. See the error message for details.
404 A resource could not be found. See the error message for details.
500 The server encountered an internal error. See the error message for details.

post
/v3/application/shops/{shop_id}/listings

Response samples
201400401403404500
Content type
application/json

Copy
Expand allCollapse all
{
"listing_id": 1,
"user_id": 1,
"shop_id": 1,
"title": "string",
"description": "string",
"state": "active",
"creation_timestamp": 946684800,
"created_timestamp": 946684800,
"ending_timestamp": 946684800,
"original_creation_timestamp": 946684800,
"last_modified_timestamp": 946684800,
"updated_timestamp": 946684800,
"state_timestamp": 946684800,
"quantity": 0,
"shop_section_id": 1,
"featured_rank": 0,
"url": "string",
"num_favorers": 0,
"non_taxable": true,
"is_taxable": true,
"is_customizable": true,
"is_personalizable": true,
"personalization_is_required": true,
"personalization_char_count_max": 0,
"personalization_instructions": "string",
"listing_type": "physical",
"tags": [
"string"
],
"materials": [
"string"
],
"shipping_profile_id": 1,
"return_policy_id": 1,
"processing_min": 0,
"processing_max": 0,
"who_made": "i_did",
"when_made": "made_to_order",
"is_supply": true,
"item_weight": 0,
"item_weight_unit": "oz",
"item_length": 0,
"item_width": 0,
"item_height": 0,
"item_dimensions_unit": "in",
"is_private": true,
"style": [
"string"
],
"file_data": "string",
"has_variations": true,
"should_auto_renew": true,
"language": "string",
"price": {
"amount": 0,
"divisor": 0,
"currency_code": "string"
},
"taxonomy_id": 0,
"readiness_state_id": 1
}
getListingsByShop
General Release
Report bug
This endpoint is ready for production use.

Endpoint to list Listings that belong to a Shop. Listings can be filtered using the 'state' param.

Authorizations:
api_keyoauth2 (listings_r)
path Parameters
shop_id
required
integer <int64> >= 1
The unique positive non-zero numeric ID for an Etsy Shop.

query Parameters
state	
string
Default: "active"
Enum: "active" "inactive" "sold_out" "draft" "expired"
When updating a listing, this value can be either active or inactive. Note: Setting a draft listing to active will also publish the listing on etsy.com and requires that the listing have an image set. Setting a sold_out listing to active will update the quantity to 1 and renew the listing on etsy.com.

limit	
integer [ 1 .. 100 ]
Default: 25
The maximum number of results to return.

offset	
integer >= 0
Default: 0
The number of records to skip before selecting the first result.

sort_on	
string
Default: "created"
Enum: "created" "price" "updated" "score"
The value to sort a search result of listings on. NOTES: a) sort_on only works when combined with one of the search options (keywords, region, etc.). b) when using score the returned results will always be in descending order, regardless of the sort_order parameter.

sort_order	
string
Default: "desc"
Enum: "asc" "ascending" "desc" "descending" "up" "down"
The ascending(up) or descending(down) order to sort listings by. NOTE: sort_order only works when combined with one of the search options (keywords, region, etc.).

includes	
Array of strings
Default: null
Items Enum: "Shipping" "Images" "Shop" "User" "Translations" "Inventory" "Videos"
An enumerated string that attaches a valid association. Acceptable inputs are 'Shipping', 'Shop', 'Images', 'User', 'Translations' and 'Inventory'.

Responses
200 A list of Listings
400 There was a problem with the request data. See the error message for details.
401 The request lacks valid authentication credentials. See the error message for details.
403 The request attempted to perform an operation it is not allowed to. See the error message for details.
500 The server encountered an internal error. See the error message for details.

get
/v3/application/shops/{shop_id}/listings

Response samples
200400401403500
Content type
application/json

Copy
Expand allCollapse all
{
"count": 0,
"results": [
{}
]
}
deleteListing
General Release
Report bug
This endpoint is ready for production use.

Open API V3 endpoint to delete a ShopListing. A ShopListing can be deleted only if the state is one of the following: SOLD_OUT, DRAFT, EXPIRED, INACTIVE, ACTIVE and is_available or ACTIVE and has seller flags: SUPRESSED (frozen), VACATION, CUSTOM_SHOPS (pattern), SELL_ON_FACEBOOK

Authorizations:
api_keyoauth2 (listings_d)
path Parameters
listing_id
required
integer <int64> >= 1
The numeric ID for the listing associated to this transaction.

Responses
204 The Listing resource was correctly deleted
400 There was a problem with the request data. See the error message for details.
401 The request lacks valid authentication credentials. See the error message for details.
403 The request attempted to perform an operation it is not allowed to. See the error message for details.
404 A resource could not be found. See the error message for details.
409 There was a request conflict with the current state of the target resource. See the error message for details.
500 The server encountered an internal error. See the error message for details.

delete
/v3/application/listings/{listing_id}

Response samples
400401403404409500
Content type
application/json

Copy
Expand allCollapse all
{
"error": "string"
}
getListing
General Release
Report bug
This endpoint is ready for production use.

Retrieves a listing record by listing ID.

Authorizations:
api_key
path Parameters
listing_id
required
integer <int64> >= 1
The numeric ID for the listing associated to this transaction.

query Parameters
includes	
Array of strings
Default: null
Items Enum: "Shipping" "Images" "Shop" "User" "Translations" "Inventory" "Videos"
An enumerated string that attaches a valid association. Acceptable inputs are 'Shipping', 'Shop', 'Images', 'User', 'Translations' and 'Inventory'.

language	
string
Default: null
The IETF language tag for the language of this translation. Ex: de, en, es, fr, it, ja, nl, pl, pt.

Responses
200 A single Listing.
400 There was a problem with the request data. See the error message for details.
404 A resource could not be found. See the error message for details.
500 The server encountered an internal error. See the error message for details.

get
/v3/application/listings/{listing_id}

Response samples
200400404500
Content type
application/json

Copy
Expand allCollapse all
{
"listing_id": 1,
"user_id": 1,
"shop_id": 1,
"title": "string",
"description": "string",
"state": "active",
"creation_timestamp": 946684800,
"created_timestamp": 946684800,
"ending_timestamp": 946684800,
"original_creation_timestamp": 946684800,
"last_modified_timestamp": 946684800,
"updated_timestamp": 946684800,
"state_timestamp": 946684800,
"quantity": 0,
"shop_section_id": 1,
"featured_rank": 0,
"url": "string",
"num_favorers": 0,
"non_taxable": true,
"is_taxable": true,
"is_customizable": true,
"is_personalizable": true,
"personalization_is_required": true,
"personalization_char_count_max": 0,
"personalization_instructions": "string",
"listing_type": "physical",
"tags": [
"string"
],
"materials": [
"string"
],
"shipping_profile_id": 1,
"return_policy_id": 1,
"processing_min": 0,
"processing_max": 0,
"who_made": "i_did",
"when_made": "made_to_order",
"is_supply": true,
"item_weight": 0,
"item_weight_unit": "oz",
"item_length": 0,
"item_width": 0,
"item_height": 0,
"item_dimensions_unit": "in",
"is_private": true,
"style": [
"string"
],
"file_data": "string",
"has_variations": true,
"should_auto_renew": true,
"language": "string",
"price": {
"amount": 0,
"divisor": 0,
"currency_code": "string"
},
"taxonomy_id": 0,
"readiness_state_id": 1,
"shipping_profile": {
"shipping_profile_id": 1,
"title": "string",
"user_id": 1,
"min_processing_days": 0,
"max_processing_days": 0,
"processing_days_display_label": "string",
"origin_country_iso": "string",
"is_deleted": true,
"shipping_profile_destinations": [],
"shipping_profile_upgrades": [],
"origin_postal_code": "string",
"profile_type": "manual",
"domestic_handling_fee": 0,
"international_handling_fee": 0
},
"user": {
"user_id": 1,
"primary_email": "user@example.com",
"first_name": "string",
"last_name": "string",
"image_url_75x75": "string"
},
"shop": {
"shop_id": 1,
"user_id": 1,
"shop_name": "string",
"create_date": 0,
"created_timestamp": 0,
"title": "string",
"announcement": "string",
"currency_code": "string",
"is_vacation": true,
"vacation_message": "string",
"sale_message": "string",
"digital_sale_message": "string",
"update_date": 0,
"updated_timestamp": 0,
"listing_active_count": 0,
"digital_listing_count": 0,
"login_name": "string",
"accepts_custom_requests": true,
"policy_welcome": "string",
"policy_payment": "string",
"policy_shipping": "string",
"policy_refunds": "string",
"policy_additional": "string",
"policy_seller_info": "string",
"policy_update_date": 0,
"policy_has_private_receipt_info": true,
"has_unstructured_policies": true,
"policy_privacy": "string",
"vacation_autoreply": "string",
"url": "string",
"image_url_760x100": "string",
"num_favorers": 0,
"languages": [],
"icon_url_fullxfull": "string",
"is_using_structured_policies": true,
"has_onboarded_structured_policies": true,
"include_dispute_form_link": true,
"is_direct_checkout_onboarded": true,
"is_etsy_payments_onboarded": true,
"is_calculated_eligible": true,
"is_opted_in_to_buyer_promise": true,
"is_shop_us_based": true,
"transaction_sold_count": 0,
"shipping_from_country_iso": "string",
"shop_location_country_iso": "string",
"review_count": 0,
"review_average": 0
},
"images": [
{}
],
"videos": [
{}
],
"inventory": {
"products": [],
"price_on_property": [],
"quantity_on_property": [],
"sku_on_property": []
},
"production_partners": [
{}
],
"skus": [
"string"
],
"translations": {
"de": {},
"en-GB": {},
"en-IN": {},
"en-US": {},
"es": {},
"fr": {},
"it": {},
"ja": {},
"nl": {},
"pl": {},
"pt": {},
"ru": {}
},
"views": 0
}
findAllListingsActive
General Release
Report bug
This endpoint is ready for production use.

A list of all active listings on Etsy paginated by their creation date. Without sort_order listings will be returned newest-first by default.

Authorizations:
api_key
query Parameters
limit	
integer [ 1 .. 100 ]
Default: 25
The maximum number of results to return.

offset	
integer >= 0
Default: 0
The number of records to skip before selecting the first result.

keywords	
string
Default: null
Search term or phrase that must appear in all results.

sort_on	
string
Default: "created"
Enum: "created" "price" "updated" "score"
The value to sort a search result of listings on. NOTES: a) sort_on only works when combined with one of the search options (keywords, region, etc.). b) when using score the returned results will always be in descending order, regardless of the sort_order parameter.

sort_order	
string
Default: "desc"
Enum: "asc" "ascending" "desc" "descending" "up" "down"
The ascending(up) or descending(down) order to sort listings by. NOTE: sort_order only works when combined with one of the search options (keywords, region, etc.).

min_price	
number <float>
Default: null
The minimum price of listings to be returned by a search result.

max_price	
number <float>
Default: null
The maximum price of listings to be returned by a search result.

taxonomy_id	
integer <int64> >= 1
Default: null
The numerical taxonomy ID of the listing. See SellerTaxonomy and BuyerTaxonomy for more information.

shop_location	
string
Default: null
Filters by shop location. If location cannot be parsed, Etsy responds with an error.

Responses
200 A list of all active listings on Etsy paginated by their creation date. Without sort_order listings will be returned newest-first by default.
404 A resource could not be found. See the error message for details.
500 The server encountered an internal error. See the error message for details.

get
/v3/application/listings/active

Response samples
200404500
Content type
application/json

Copy
Expand allCollapse all
{
"count": 0,
"results": [
{}
]
}
findAllActiveListingsByShop
General Release
Report bug
This endpoint is ready for production use.

Retrieves a list of all active listings on Etsy in a specific shop, paginated by listing creation date.

Authorizations:
api_key
path Parameters
shop_id
required
integer <int64> >= 1
The unique positive non-zero numeric ID for an Etsy Shop.

query Parameters
limit	
integer [ 1 .. 100 ]
Default: 25
The maximum number of results to return.

sort_on	
string
Default: "created"
Enum: "created" "price" "updated" "score"
The value to sort a search result of listings on. NOTES: a) sort_on only works when combined with one of the search options (keywords, region, etc.). b) when using score the returned results will always be in descending order, regardless of the sort_order parameter.

sort_order	
string
Default: "desc"
Enum: "asc" "ascending" "desc" "descending" "up" "down"
The ascending(up) or descending(down) order to sort listings by. NOTE: sort_order only works when combined with one of the search options (keywords, region, etc.).

offset	
integer >= 0
Default: 0
The number of records to skip before selecting the first result.

keywords	
string
Default: null
Search term or phrase that must appear in all results.

Responses
200 Retrieves a list of all active listings on Etsy in a specific shop, paginated by listing creation date.
400 There was a problem with the request data. See the error message for details.
404 A resource could not be found. See the error message for details.
500 The server encountered an internal error. See the error message for details.

get
/v3/application/shops/{shop_id}/listings/active

Response samples
200400404500
Content type
application/json

Copy
Expand allCollapse all
{
"count": 0,
"results": [
{}
]
}
getListingsByListingIds
General Release
Report bug
This endpoint is ready for production use.

Allows to query multiple listing ids at once. Limit 100 ids maximum per query.

Authorizations:
api_key
query Parameters
listing_ids
required
Array of integers <int64>
The list of numeric IDS for the listings in a specific Etsy shop.

includes	
Array of strings
Default: null
Items Enum: "Shipping" "Images" "Shop" "User" "Translations" "Inventory" "Videos"
An enumerated string that attaches a valid association. Acceptable inputs are 'Shipping', 'Shop', 'Images', 'User', 'Translations' and 'Inventory'.

Responses
200 A list of Listings
400 There was a problem with the request data. See the error message for details.
404 A resource could not be found. See the error message for details.
500 The server encountered an internal error. See the error message for details.

get
/v3/application/listings/batch

Response samples
200400404500
Content type
application/json

Copy
Expand allCollapse all
{
"count": 0,
"results": [
{}
]
}
getFeaturedListingsByShop
General Release
Report bug
This endpoint is ready for production use.

Retrieves Listings associated to a Shop that are featured.

Authorizations:
api_key
path Parameters
shop_id
required
integer <int64> >= 1
The unique positive non-zero numeric ID for an Etsy Shop.

query Parameters
limit	
integer [ 1 .. 100 ]
Default: 25
The maximum number of results to return.

offset	
integer >= 0
Default: 0
The number of records to skip before selecting the first result.

Responses
200 A list of Listings
400 There was a problem with the request data. See the error message for details.
403 The request attempted to perform an operation it is not allowed to. See the error message for details.
500 The server encountered an internal error. See the error message for details.

get
/v3/application/shops/{shop_id}/listings/featured

Response samples
200400403500
Content type
application/json

Copy
Expand allCollapse all
{
"count": 0,
"results": [
{}
]
}
deleteListingProperty
General Release
Report bug
This endpoint is ready for production use.

Deletes a property for a Listing.

Authorizations:
api_keyoauth2 (listings_w)
path Parameters
shop_id
required
integer <int64> >= 1
The unique positive non-zero numeric ID for an Etsy Shop.

listing_id
required
integer <int64> >= 1
The numeric ID for the listing associated to this transaction.

property_id
required
integer <int64> >= 1
The unique ID of an Etsy listing property.

Responses
204 The ListingProperty resource was correctly deleted
400 There was a problem with the request data. See the error message for details.
401 The request lacks valid authentication credentials. See the error message for details.
403 The request attempted to perform an operation it is not allowed to. See the error message for details.
404 A resource could not be found. See the error message for details.
500 The server encountered an internal error. See the error message for details.

delete
/v3/application/shops/{shop_id}/listings/{listing_id}/properties/{property_id}

Response samples
400401403404500
Content type
application/json

Copy
Expand allCollapse all
{
"error": "string"
}
updateListingProperty
General Release
Report bug
This endpoint is ready for production use.

Updates or populates the properties list defining product offerings for a listing. Each offering requires both a value and a value_id that are valid for a scale_id assigned to the listing or that you assign to the listing with this request.

Authorizations:
api_keyoauth2 (listings_w)
path Parameters
shop_id
required
integer <int64> >= 1
The unique positive non-zero numeric ID for an Etsy Shop.

listing_id
required
integer <int64> >= 1
The numeric ID for the listing associated to this transaction.

property_id
required
integer <int64> >= 1
The unique ID of an Etsy listing property.

Request Body schema: application/x-www-form-urlencoded
value_ids
required
Array of integers <int64>
An array of unique IDs of multiple Etsy listing property values. For example, if your listing offers different sizes of a product, then the value ID list contains value IDs for each size.

values
required
Array of strings
An array of value strings for multiple Etsy listing property values. For example, if your listing offers different colored products, then the values array contains the color strings for each color. Note: parenthesis characters (( and )) are not allowed.

scale_id	
integer <int64> >= 1
The numeric ID of a single Etsy.com measurement scale. For example, for shoe size, there are three scale_ids available - UK, US/Canada, and EU, where US/Canada has scale_id 19.

Responses
200 A single listing property.
400 There was a problem with the request data. See the error message for details.
401 The request lacks valid authentication credentials. See the error message for details.
403 The request attempted to perform an operation it is not allowed to. See the error message for details.
404 A resource could not be found. See the error message for details.
500 The server encountered an internal error. See the error message for details.

put
/v3/application/shops/{shop_id}/listings/{listing_id}/properties/{property_id}

Response samples
200400401403404500
Content type
application/json

Copy
Expand allCollapse all
{
"property_id": 1,
"property_name": "string",
"scale_id": 1,
"scale_name": "string",
"value_ids": [
1
],
"values": [
"string"
]
}
getListingProperty
Feedback only
Give feedback
Development for this endpoint is in progress. It will only return a 501 response.

Retrieves a listing's property

Authorizations:
api_key
path Parameters
listing_id
required
integer <int64> >= 1
The numeric ID for the listing associated to this transaction.

property_id
required
integer <int64> >= 1
The unique ID of an Etsy listing property.

Responses
200 A single ListingProperty.
400 There was a problem with the request data. See the error message for details.
404 A resource could not be found. See the error message for details.
500 The server encountered an internal error. See the error message for details.
501 This endpoint is not functional at this time.

get
/v3/application/listings/{listing_id}/properties/{property_id}

Response samples
200400404500501
Content type
application/json

Copy
Expand allCollapse all
{
"property_id": 1,
"property_name": "string",
"scale_id": 1,
"scale_name": "string",
"value_ids": [
1
],
"values": [
"string"
]
}
getListingProperties
General Release
Report bug
This endpoint is ready for production use.

Get a listing's properties

Authorizations:
api_key
path Parameters
shop_id
required
integer <int64> >= 1
The unique positive non-zero numeric ID for an Etsy Shop.

listing_id
required
integer <int64> >= 1
The numeric ID for the listing associated to this transaction.

Responses
200 A Listing's Properties
400 There was a problem with the request data. See the error message for details.
404 A resource could not be found. See the error message for details.
500 The server encountered an internal error. See the error message for details.

get
/v3/application/shops/{shop_id}/listings/{listing_id}/properties

Response samples
200400404500
Content type
application/json

Copy
Expand allCollapse all
{
"count": 0,
"results": [
{}
]
}
updateListing
General Release
Report bug
This endpoint is ready for production use.

Updates a listing, identified by a listing ID, for a specific shop identified by a shop ID. Note that this is a PATCH method type. When activating, or manually renewing a physical listing, the shipping profile referenced by the shipping_profile_id, and all of its fields, along with its entries and upgrades must be complete and valid. If the shipping profile is not complete and valid, we will throw an exception with an error message that guides the request sender to update whatever data is bad. Draft digital listings that are not made to order must have a file upload associated with it to be activated. If the listing is made to order, the file upload is not required.

Authorizations:
api_keyoauth2 (listings_w)
path Parameters
shop_id
required
integer <int64> >= 1
The unique positive non-zero numeric ID for an Etsy Shop.

listing_id
required
integer <int64> >= 1
The numeric ID for the listing associated to this transaction.

Request Body schema: application/x-www-form-urlencoded
image_ids	
Array of integers <int64>
An array of numeric image IDs of the images in a listing, which can include up to 10 images.

title	
string
The listing's title string. When creating or updating a listing, valid title strings contain only letters, numbers, punctuation marks, mathematical symbols, whitespace characters, ™, ©, and ®. (regex: /[^\p{L}\p{Nd}\p{P}\p{Sm}\p{Zs}™©®]/u) You can only use the %, :, & and + characters once each.

description	
string
A description string of the product for sale in the listing.

materials	
Array of strings Nullable
A list of material strings for materials used in the product. Valid materials strings contain only letters, numbers, and whitespace characters. (regex: /[^\p{L}\p{Nd}\p{Zs}]/u) Default value is null.

should_auto_renew	
boolean
When true, renews a listing for four months upon expiration.

shipping_profile_id	
integer <int64> >= 1 Nullable
The numeric ID of the shipping profile associated with the listing. Required when listing type is physical.

return_policy_id	
integer <int64> >= 1 Nullable
The numeric ID of the Return Policy. Required for active physical listings. This requirement does not apply to listings of EU-based shops.

shop_section_id	
integer Nullable
The numeric ID of the shop section for this listing. Default value is null.

item_weight	
number <float> [ 0 .. 1.79769313486e+308 ] Nullable
The numeric weight of the product measured in units set in 'item_weight_unit'. Default value is null. If set, the value must be greater than 0.

item_length	
number <float> [ 0 .. 1.79769313486e+308 ] Nullable
The numeric length of the product measured in units set in 'item_dimensions_unit'. Default value is null. If set, the value must be greater than 0.

item_width	
number <float> [ 0 .. 1.79769313486e+308 ] Nullable
The numeric width of the product measured in units set in 'item_dimensions_unit'. Default value is null. If set, the value must be greater than 0.

item_height	
number <float> [ 0 .. 1.79769313486e+308 ] Nullable
The numeric height of the product measured in units set in 'item_dimensions_unit'. Default value is null. If set, the value must be greater than 0.

item_weight_unit	
string Nullable
Enum: "" "oz" "lb" "g" "kg"
A string defining the units used to measure the weight of the product. Default value is null.

item_dimensions_unit	
string Nullable
Enum: "" "in" "ft" "mm" "cm" "m" "yd" "inches"
A string defining the units used to measure the dimensions of the product. Default value is null.

is_taxable	
boolean
When true, applicable shop tax rates apply to this listing at checkout.

taxonomy_id	
integer <int64> >= 1
The numerical taxonomy ID of the listing. See SellerTaxonomy and BuyerTaxonomy for more information.

tags	
Array of strings Nullable
A comma-separated list of tag strings for the listing. When creating or updating a listing, valid tag strings contain only letters, numbers, whitespace characters, -, ', ™, ©, and ®. (regex: /[^\p{L}\p{Nd}\p{Zs}-'™©®]/u) Default value is null.

who_made	
string
Enum: "i_did" "someone_else" "collective"
An enumerated string indicating who made the product. Helps buyers locate the listing under the Handmade heading. Requires 'is_supply' and 'when_made'.

when_made	
string
Enum: "made_to_order" "2020_2025" "2010_2019" "2006_2009" "before_2006" "2000_2005" "1990s" "1980s" "1970s" "1960s" "1950s" "1940s" "1930s" "1920s" "1910s" "1900s" "1800s" "1700s" "before_1700"
An enumerated string for the era in which the maker made the product in this listing. Helps buyers locate the listing under the Vintage heading. Requires 'is_supply' and 'who_made'.

featured_rank	
integer Nullable
The positive non-zero numeric position in the featured listings of the shop, with rank 1 listings appearing in the left-most position in featured listing on a shop's home page.

is_personalizable	
boolean
When true, this listing is personalizable. The default value is null.

personalization_is_required	
boolean
When true, this listing requires personalization. The default value is null. Will only change if is_personalizable is 'true'.

personalization_char_count_max	
integer
This is an integer value representing the maximum length for the personalization message entered by the buyer. Will only change if is_personalizable is 'true'.

personalization_instructions	
string
A string representing instructions for the buyer to enter the personalization. Will only change if is_personalizable is 'true'.

state	
string
Enum: "active" "inactive"
When updating a listing, this value can be either active or inactive. Note: Setting a draft listing to active will also publish the listing on etsy.com and requires that the listing have an image set. Setting a sold_out listing to active will update the quantity to 1 and renew the listing on etsy.com.

is_supply	
boolean
When true, tags the listing as a supply product, else indicates that it's a finished product. Helps buyers locate the listing under the Supplies heading. Requires 'who_made' and 'when_made'.

production_partner_ids	
Array of integers <int64> Nullable
An array of unique IDs of production partner ids.

type	
string Nullable
Enum: "physical" "download" "both"
An enumerated type string that indicates whether the listing is physical or a digital download.

legacy	
boolean
This parameter needed to enable new parameters and response values related to processing profiles.

Responses
200 A single ShopListing
400 There was a problem with the request data. See the error message for details.
401 The request lacks valid authentication credentials. See the error message for details.
403 The request attempted to perform an operation it is not allowed to. See the error message for details.
404 A resource could not be found. See the error message for details.
409 There was a request conflict with the current state of the target resource. See the error message for details.
500 The server encountered an internal error. See the error message for details.

patch
/v3/application/shops/{shop_id}/listings/{listing_id}

Response samples
200400401403404409500
Content type
application/json

Copy
Expand allCollapse all
{
"listing_id": 1,
"user_id": 1,
"shop_id": 1,
"title": "string",
"description": "string",
"state": "active",
"creation_timestamp": 946684800,
"created_timestamp": 946684800,
"ending_timestamp": 946684800,
"original_creation_timestamp": 946684800,
"last_modified_timestamp": 946684800,
"updated_timestamp": 946684800,
"state_timestamp": 946684800,
"quantity": 0,
"shop_section_id": 1,
"featured_rank": 0,
"url": "string",
"num_favorers": 0,
"non_taxable": true,
"is_taxable": true,
"is_customizable": true,
"is_personalizable": true,
"personalization_is_required": true,
"personalization_char_count_max": 0,
"personalization_instructions": "string",
"listing_type": "physical",
"tags": [
"string"
],
"materials": [
"string"
],
"shipping_profile_id": 1,
"return_policy_id": 1,
"processing_min": 0,
"processing_max": 0,
"who_made": "i_did",
"when_made": "made_to_order",
"is_supply": true,
"item_weight": 0,
"item_weight_unit": "oz",
"item_length": 0,
"item_width": 0,
"item_height": 0,
"item_dimensions_unit": "in",
"is_private": true,
"style": [
"string"
],
"file_data": "string",
"has_variations": true,
"should_auto_renew": true,
"language": "string",
"price": {
"amount": 0,
"divisor": 0,
"currency_code": "string"
},
"taxonomy_id": 0,
"readiness_state_id": 1
}
updateListingDeprecated
General Release
Report bug
This endpoint is ready for production use.

Updates a listing, identified by a listing ID, for a specific shop identified by a shop ID. This endpoint will be removed in the near future in favor of updateListing PATCH version.

Authorizations:
api_keyoauth2 (listings_w)
path Parameters
shop_id
required
integer <int64> >= 1
The unique positive non-zero numeric ID for an Etsy Shop.

listing_id
required
integer <int64> >= 1
The numeric ID for the listing associated to this transaction.

Request Body schema: application/x-www-form-urlencoded
image_ids	
Array of integers <int64>
An array of numeric image IDs of the images in a listing, which can include up to 10 images.

title	
string
The listing's title string. When creating or updating a listing, valid title strings contain only letters, numbers, punctuation marks, mathematical symbols, whitespace characters, ™, ©, and ®. (regex: /[^\p{L}\p{Nd}\p{P}\p{Sm}\p{Zs}™©®]/u) You can only use the %, :, & and + characters once each.

description	
string
A description string of the product for sale in the listing.

materials	
Array of strings Nullable
A list of material strings for materials used in the product. Valid materials strings contain only letters, numbers, and whitespace characters. (regex: /[^\p{L}\p{Nd}\p{Zs}]/u) Default value is null.

should_auto_renew	
boolean
When true, renews a listing for four months upon expiration.

shipping_profile_id	
integer <int64> >= 1 Nullable
The numeric ID of the shipping profile associated with the listing. Required when listing type is physical.

shop_section_id	
integer Nullable
The numeric ID of the shop section for this listing. Default value is null.

item_weight	
number <float> [ 0 .. 1.79769313486e+308 ] Nullable
The numeric weight of the product measured in units set in 'item_weight_unit'. Default value is null. If set, the value must be greater than 0.

item_length	
number <float> [ 0 .. 1.79769313486e+308 ] Nullable
The numeric length of the product measured in units set in 'item_dimensions_unit'. Default value is null. If set, the value must be greater than 0.

item_width	
number <float> [ 0 .. 1.79769313486e+308 ] Nullable
The numeric width of the product measured in units set in 'item_dimensions_unit'. Default value is null. If set, the value must be greater than 0.

item_height	
number <float> [ 0 .. 1.79769313486e+308 ] Nullable
The numeric height of the product measured in units set in 'item_dimensions_unit'. Default value is null. If set, the value must be greater than 0.

item_weight_unit	
string Nullable
Enum: "oz" "lb" "g" "kg"
A string defining the units used to measure the weight of the product. Default value is null.

item_dimensions_unit	
string Nullable
Enum: "in" "ft" "mm" "cm" "m" "yd" "inches"
A string defining the units used to measure the dimensions of the product. Default value is null.

is_taxable	
boolean
When true, applicable shop tax rates apply to this listing at checkout.

taxonomy_id	
integer <int64> >= 1
The numerical taxonomy ID of the listing. See SellerTaxonomy and BuyerTaxonomy for more information.

tags	
Array of strings Nullable
A comma-separated list of tag strings for the listing. When creating or updating a listing, valid tag strings contain only letters, numbers, whitespace characters, -, ', ™, ©, and ®. (regex: /[^\p{L}\p{Nd}\p{Zs}-'™©®]/u) Default value is null.

who_made	
string
Enum: "i_did" "someone_else" "collective"
An enumerated string indicating who made the product. Helps buyers locate the listing under the Handmade heading. Requires 'is_supply' and 'when_made'.

when_made	
string
Enum: "made_to_order" "2020_2025" "2010_2019" "2006_2009" "before_2006" "2000_2005" "1990s" "1980s" "1970s" "1960s" "1950s" "1940s" "1930s" "1920s" "1910s" "1900s" "1800s" "1700s" "before_1700"
An enumerated string for the era in which the maker made the product in this listing. Helps buyers locate the listing under the Vintage heading. Requires 'is_supply' and 'who_made'.

featured_rank	
integer Nullable
The positive non-zero numeric position in the featured listings of the shop, with rank 1 listings appearing in the left-most position in featured listing on a shop's home page.

is_personalizable	
boolean
When true, this listing is personalizable. The default value is null.

personalization_is_required	
boolean
When true, this listing requires personalization. The default value is null. Will only change if is_personalizable is 'true'.

personalization_char_count_max	
integer
This is an integer value representing the maximum length for the personalization message entered by the buyer. Will only change if is_personalizable is 'true'.

personalization_instructions	
string
A string representing instructions for the buyer to enter the personalization. Will only change if is_personalizable is 'true'.

state	
string
Enum: "active" "inactive"
When updating a listing, this value can be either active or inactive. Note: Setting a draft listing to active will also publish the listing on etsy.com and requires that the listing have an image set. Setting a sold_out listing to active will update the quantity to 1 and renew the listing on etsy.com.

is_supply	
boolean
When true, tags the listing as a supply product, else indicates that it's a finished product. Helps buyers locate the listing under the Supplies heading. Requires 'who_made' and 'when_made'.

production_partner_ids	
Array of integers <int64> Nullable
An array of unique IDs of production partner ids.

type	
string Nullable
Enum: "physical" "download" "both"
An enumerated type string that indicates whether the listing is physical or a digital download.

Responses
200 A single ShopListing
400 There was a problem with the request data. See the error message for details.
401 The request lacks valid authentication credentials. See the error message for details.
403 The request attempted to perform an operation it is not allowed to. See the error message for details.
404 A resource could not be found. See the error message for details.
409 There was a request conflict with the current state of the target resource. See the error message for details.
500 The server encountered an internal error. See the error message for details.

put
/v3/application/shops/{shop_id}/listings/{listing_id}

Response samples
200400401403404409500
Content type
application/json

Copy
Expand allCollapse all
{
"listing_id": 1,
"user_id": 1,
"shop_id": 1,
"title": "string",
"description": "string",
"state": "active",
"creation_timestamp": 946684800,
"created_timestamp": 946684800,
"ending_timestamp": 946684800,
"original_creation_timestamp": 946684800,
"last_modified_timestamp": 946684800,
"updated_timestamp": 946684800,
"state_timestamp": 946684800,
"quantity": 0,
"shop_section_id": 1,
"featured_rank": 0,
"url": "string",
"num_favorers": 0,
"non_taxable": true,
"is_taxable": true,
"is_customizable": true,
"is_personalizable": true,
"personalization_is_required": true,
"personalization_char_count_max": 0,
"personalization_instructions": "string",
"listing_type": "physical",
"tags": [
"string"
],
"materials": [
"string"
],
"shipping_profile_id": 1,
"return_policy_id": 1,
"processing_min": 0,
"processing_max": 0,
"who_made": "i_did",
"when_made": "made_to_order",
"is_supply": true,
"item_weight": 0,
"item_weight_unit": "oz",
"item_length": 0,
"item_width": 0,
"item_height": 0,
"item_dimensions_unit": "in",
"is_private": true,
"style": [
"string"
],
"file_data": "string",
"has_variations": true,
"should_auto_renew": true,
"language": "string",
"price": {
"amount": 0,
"divisor": 0,
"currency_code": "string"
},
"taxonomy_id": 0,
"readiness_state_id": 1
}
getListingsByShopReceipt
General Release
Report bug
This endpoint is ready for production use.

Gets all listings associated with a receipt.

Authorizations:
api_keyoauth2 (transactions_r)
path Parameters
receipt_id
required
integer <int64> >= 1
The numeric ID for the receipt associated to this transaction.

shop_id
required
integer <int64> >= 1
The unique positive non-zero numeric ID for an Etsy Shop.

query Parameters
limit	
integer [ 1 .. 100 ]
Default: 25
The maximum number of results to return.

offset	
integer >= 0
Default: 0
The number of records to skip before selecting the first result.

Responses
200 A set of ShopListing resources.
400 There was a problem with the request data. See the error message for details.
401 The request lacks valid authentication credentials. See the error message for details.
403 The request attempted to perform an operation it is not allowed to. See the error message for details.
404 A resource could not be found. See the error message for details.
500 The server encountered an internal error. See the error message for details.

get
/v3/application/shops/{shop_id}/receipts/{receipt_id}/listings

Response samples
200400401403404500
Content type
application/json

Copy
Expand allCollapse all
{
"count": 0,
"results": [
{}
]
}
getListingsByShopReturnPolicy
General Release
Report bug
This endpoint is ready for production use.

Gets all listings associated with a Return Policy.

Authorizations:
api_keyoauth2 (listings_r)
path Parameters
return_policy_id
required
integer <int64> >= 1
The numeric ID of the Return Policy.

shop_id
required
integer <int64> >= 1
The unique positive non-zero numeric ID for an Etsy Shop.

Responses
200 A set of ShopListing resources.
400 There was a problem with the request data. See the error message for details.
401 The request lacks valid authentication credentials. See the error message for details.
403 The request attempted to perform an operation it is not allowed to. See the error message for details.
404 A resource could not be found. See the error message for details.
500 The server encountered an internal error. See the error message for details.

get
/v3/application/shops/{shop_id}/policies/return/{return_policy_id}/listings

Response samples
200400401403404500
Content type
application/json

Copy
Expand allCollapse all
{
"count": 0,
"results": [
{}
]
}
getListingsByShopSectionId
General Release
Report bug
This endpoint is ready for production use.

Retrieves all the listings from the section of a specific shop.

Authorizations:
api_key
path Parameters
shop_id
required
integer <int64> >= 1
The unique positive non-zero numeric ID for an Etsy Shop.

query Parameters
shop_section_ids
required
Array of integers <int64>
A list of numeric IDS for all sections in a specific Etsy shop.

limit	
integer [ 1 .. 100 ]
Default: 25
The maximum number of results to return.

offset	
integer >= 0
Default: 0
The number of records to skip before selecting the first result.

sort_on	
string
Default: "created"
Enum: "created" "price" "updated" "score"
The value to sort a search result of listings on. NOTES: a) sort_on only works when combined with one of the search options (keywords, region, etc.). b) when using score the returned results will always be in descending order, regardless of the sort_order parameter.

sort_order	
string
Default: "desc"
Enum: "asc" "ascending" "desc" "descending" "up" "down"
The ascending(up) or descending(down) order to sort listings by. NOTE: sort_order only works when combined with one of the search options (keywords, region, etc.).

Responses
200 A list of listings from a shop section.
400 There was a problem with the request data. See the error message for details.
500 The server encountered an internal error. See the error message for details.

get
/v3/application/shops/{shop_id}/shop-sections/listings

Response samples
200400500
Content type
application/json

Copy
Expand allCollapse all
{
"count": 0,
"results": [
{}
]
}
ShopListing File
deleteListingFile
General Release
Report bug
This endpoint is ready for production use.

Deletes a file from a specific listing. When you delete the final file for a digital listing, the listing converts into a physical listing. The response to a delete request returns a list of the remaining file records associated with the given listing.

Authorizations:
api_keyoauth2 (listings_w)
path Parameters
shop_id
required
integer <int64> >= 1
The unique positive non-zero numeric ID for an Etsy Shop.

listing_id
required
integer <int64> >= 1
The numeric ID for the listing associated to this transaction.

listing_file_id
required
integer <int64> >= 1
The unique numeric ID of a file associated with a digital listing.

Responses
204 The ShopListingFile resource was correctly deleted
400 There was a problem with the request data. See the error message for details.
401 The request lacks valid authentication credentials. See the error message for details.
403 The request attempted to perform an operation it is not allowed to. See the error message for details.
404 A resource could not be found. See the error message for details.
409 There was a request conflict with the current state of the target resource. See the error message for details.
500 The server encountered an internal error. See the error message for details.

delete
/v3/application/shops/{shop_id}/listings/{listing_id}/files/{listing_file_id}

Response samples
400401403404409500
Content type
application/json

Copy
Expand allCollapse all
{
"error": "string"
}
getListingFile
General Release
Report bug
This endpoint is ready for production use.

Retrieves a single file associated with the given digital listing. Requesting a file from a physical listing returns an empty result.

Authorizations:
api_keyoauth2 (listings_r)
path Parameters
shop_id
required
integer <int64> >= 1
The unique positive non-zero numeric ID for an Etsy Shop.

listing_id
required
integer <int64> >= 1
The numeric ID for the listing associated to this transaction.

listing_file_id
required
integer <int64> >= 1
The unique numeric ID of a file associated with a digital listing.

Responses
200 The metatdata for a file associated with a digital listing.
400 There was a problem with the request data. See the error message for details.
401 The request lacks valid authentication credentials. See the error message for details.
403 The request attempted to perform an operation it is not allowed to. See the error message for details.
404 A resource could not be found. See the error message for details.
500 The server encountered an internal error. See the error message for details.

get
/v3/application/shops/{shop_id}/listings/{listing_id}/files/{listing_file_id}

Response samples
200400401403404500
Content type
application/json

Copy
Expand allCollapse all
{
"listing_file_id": 1,
"listing_id": 1,
"rank": 0,
"filename": "string",
"filesize": "string",
"size_bytes": 0,
"filetype": "string",
"create_timestamp": 946684800,
"created_timestamp": 946684800
}


ploadListingVideo
General Release
Report bug
This endpoint is ready for production use.

Uploads a new video for a listing, or associates an existing video with a specific listing. You must either provide the video_id of an existing video, or the name and binary file data for a video to upload.

Authorizations:
api_keyoauth2 (listings_w)
path Parameters
shop_id
required
integer <int64> >= 1
The unique positive non-zero numeric ID for an Etsy Shop.

listing_id
required
integer <int64> >= 1
The numeric ID for the listing associated to this transaction.

Request Body schema: multipart/form-data
video_id	
integer <int64> >= 1
The unique ID of a video associated with a listing.

video	
string <binary> Nullable
A video file to upload.

name	
string
The file name string for the video to upload.

Responses
201 The metadata for a file associated with a digital listing.
400 There was a problem with the request data. See the error message for details.
401 The request lacks valid authentication credentials. See the error message for details.
403 The request attempted to perform an operation it is not allowed to. See the error message for details.
404 A resource could not be found. See the error message for details.
500 The server encountered an internal error. See the error message for details.

post
/v3/application/shops/{shop_id}/listings/{listing_id}/videos

Response samples
201400401403404500
Content type
application/json

Copy
Expand allCollapse all
{
"video_id": 1,
"height": 0,
"width": 0,
"thumbnail_url": "string",
"video_url": "string",
"video_state": "active"
}
Other