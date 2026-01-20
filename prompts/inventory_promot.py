DEVIN_INVENTORY_FETCH_PROMPT = """

## Context
## Headout Inventory Model (Authoritative)

### Product Hierarchy
- TGID → TID → TID_VID
- Inventory is always fetched, stored, and processed at **TID_VID level**
- A TID_VID represents the lowest sellable unit on Headout

### Variant Constraints
- A TID_VID:
  - MAY have multiple date/time slots
  - MUST NOT have multiple languages
- If supplier exposes language variants:
  - Each language must be mapped to a **separate TID_VID**

### Product Code Structure (PCS)
- PCS is a **JSON object**, already created and provided as input
- PCS contains:
  - Supplier product identifiers (productId, optionId, rateId, UUIDs, etc.)
  - Pax type definitions
  - Possibly booking-only custom/user fields
  - Possibly an `apiCurrency` field (if explicitly provided)

**Rules:**
- PCS is immutable
- PCS must NOT be modified or inferred
- Booking-only custom/user fields in PCS must be ignored for inventory fetch
- Only supplier identifiers, pax types, and explicitly declared currency fields are relevant

---

## Inventory Semantics (Strict Rules)

### Availability
- Inventory is fetched using supplier identifiers from PCS
- Availability is mapped per:
  - Date
  - Time slot (if applicable)
  - Pax type

### Seat Count Rules
- If supplier explicitly provides remaining capacity:
  - Use that value
- If supplier shows availability as "open" but does NOT provide seat count:
  - Treat as **LIMITED**
  - Set remainingSeats = **9999**
- If supplier marks availability as unlimited:
  - Set remainingSeats = **9999**

### Closed / Sold-Out Detection
- If supplier explicitly marks a slot as sold out / unavailable:
  - Mark slot as CLOSED
- If supplier omits a previously expected date/time slot from response:
  - Treat it as **CLOSED** on Headout side

### Pooled vs Independent Inventory
- If availability is shared across pax types:
  - Treat as **POOLED**
- If availability is provided per pax type:
  - Treat as **INDEPENDENT**
- Determination must be made strictly from API documentation and responses

### Pricing
- Pricing field selection is predefined and provided separately
- If multiple prices exist:
  - Use only the explicitly instructed price field
- Pricing must be mapped per pax type
- Pricing must ALWAYS be accompanied by a currency code

---

## Currency Handling (Authoritative, Explicit)

Currency handling MUST follow the explicitly provided strategy.
You MUST NOT infer or auto-detect currency behavior.

Exactly ONE of the following strategies will be provided as input:

### Strategy A — Currency Present in Supplier Response
- Supplier provides currency explicitly in API responses
- Currency MAY come from:
  - Inventory endpoint response
  - OR a different documented endpoint (e.g., product/details)

Rules:
- Use the exact field and endpoint specified in the input
- If currency is obtained from a non-inventory endpoint:
  - Inventory logic MUST fetch currency first
  - Store it in-memory
  - Attach it to all inventory pricing objects
- Do NOT attempt to infer currency from price values

### Strategy B — Currency Provided via Product Code Structure
- Supplier does NOT return currency in any API response
- PCS contains an explicitly defined `apiCurrency` (or equivalent) field

Rules:
- Ignore currency detection from API responses
- Always use the currency value from PCS
- Attach this currency to all pricing objects

### Strategy C — Currency Passed as Request Parameter
- Supplier API supports passing currency as a request parameter
- Prices are returned in the requested currency

Rules:
- Always pass **Tour City Currency** (provided by Headout context) as the request parameter
- Use returned prices as-is
- Attach Tour City Currency to all pricing objects

### Global Currency Rules
- Inventory Fetch MUST always output price + currency
- NO currency conversion must be implemented
- NO fallback or guessing is allowed
- Headout FX systems handle conversion downstream

---

## Inputs

### Primary Inputs
- **Supplier API Documentation**
https://docs.ventrata.com/

- **Product Code Structure (PCS)**
  { "productId": "2d343f5d-dc9f-42d1-8166-202aee884836", "optionId": "cf15cb08-fa82-49e0-a5bf-8458147fbfab", "personTypeMap": { "ADULT": "unit_8c07647f-e750-4592-9adf-874728fdee03", "CHILD": "unit_6fe07069-4b42-4d98-af1f-7be8b09df4fc", "INFANT": "unit_63ccc8cd-e657-4f80-ae6c-7067d3351a88" }, "customFieldMap": { "PICK_UP_POINT": 12345 }, "contactOptionCustomFieldMap": { "country": 67890 } }

- **Pricing Field Selection Rules**
Price to be picked up from "retail" field under unitPricing for each pax type

- **Currency Handling Strategy**
Currency Handling Strategy will be strategy C we will send a currency param

---

## Assumptions
- Authentication is already handled
- Devin has access to full API documentation
- File structure and plugin scaffolding already exist
- Inventory logic must be implemented ONLY within existing files

---

## Your Task

### Step 1: Analyze Supplier API Documentation
Identify and document:
- Inventory / availability endpoints
- Required identifiers and filters
- Availability response structure
- Seat count semantics
- Sold-out / closed indicators
- Pooled vs independent behavior
- Time-slot handling (start/end time)
- Currency-related fields or endpoints (only if explicitly instructed)

### Step 2: Map Supplier Concepts to Headout Inventory Model
Determine:
- Which supplier identifiers from PCS are used in inventory calls
- How availability maps to TID_VID
- How pax types are represented
- How remaining seats are calculated
- How missing data should be interpreted
- How pricing and currency are attached to pax types
"""