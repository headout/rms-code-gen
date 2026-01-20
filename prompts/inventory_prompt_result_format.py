META_PROMPT_REZDY = """
# Headout Inventory Fetch — API Documentation Analyzer & Devin Prompt Generator for {vendor_plugin_name}

## Context

You are an expert API documentation analyst and Headout-domain specialist.

Your responsibility is to:
- Read and understand supplier API documentation
- Apply Headout's inventory model and constraints
- Apply the explicitly provided currency handling strategy
- Generate a **supplier-specific, Devin-ready prompt** that will result in a **correct InventoryFetch implementation**

This meta-prompt does **not** ask you to write code.
It asks you to generate the **exact prompt** that will be given to Devin, who will then write the code.

You MUST NOT infer, guess, or auto-detect behaviors that are explicitly provided as inputs.

---

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
  https://developers.rezdy.com/rezdyapi/index-agent.html

- **Product Code Structure (PCS)**
  {
  "productId": "XYZ123",
  "personTypeCodes": {
    "ADULT": "Adult",
    "CHILD": "Child 3-14 years"
  },
  "pickupCustomFieldId": 218613
}

- **Pricing Field Selection Rules**
  Pricing must be picked up from inventory results

- **Currency Handling Strategy**
  Strategy A — Currency Provided via Product Code Structure

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

### Step 3: Generate Two Outputs

---

## Output 1 — Inventory Mapping & Reasoning (For Humans)

Produce a clear, structured explanation covering:
- Chosen inventory endpoints
- Request parameters used (mapped from PCS)
- Availability interpretation rules
- Pooled vs independent determination
- Seat count logic
- Closed slot detection logic
- Pricing and currency handling approach (as per provided strategy)
- Any assumptions explicitly dictated by inputs

This section is for **human review and validation**.

---

## Output 2 — Final Devin Prompt (Strict, Copy-Paste Ready)

Generate a **single, complete prompt** addressed to Devin.

This prompt must:
- Assume files and scaffolding already exist
- Assume PCS is already created and correct
- Instruct Devin to:
  - Implement InventoryFetch logic ONLY
  - Not create or modify file structure
  - Not touch booking, cancellation, or plugin wiring
- Specify:
  - Exact endpoints to call
  - How to build requests from PCS
  - How to parse responses
  - How to map availability, seats, pax types, pricing
  - How to attach currency based strictly on provided strategy
  - How to detect closed slots
  - How to handle pooled vs independent inventory
- Explicitly state:
  - What Devin must NOT infer or change
  - What defaults must be applied (e.g., 9999 seats)
  - That NO currency conversion logic is allowed
- End with:
  - Clear expectation of output structure and behavior
  - No ambiguity, no optional steps

The Devin prompt must be:
- Deterministic
- Implementation-oriented
- Free of analysis or reasoning text

---

## Output Format (Mandatory)

Return your response in the following structure only strictly in high fence markdown format:

<ANALYSIS_AND_MAPPING>
...
</ANALYSIS_AND_MAPPING>

<DEVIN_PROMPT>
...
</DEVIN_PROMPT>


No additional commentary outside these sections.
"""




META_PROMPT_REZDY_RESULT = """
<DEVIN_PROMPT>

You are implementing the InventoryFetch logic ONLY for the Rezdy Agent API.

IMPORTANT CONTEXT (DO NOT VIOLATE):
- File structure and plugin scaffolding already exist.
- Product Code Structure (PCS) is already created and immutable.
- You MUST NOT create or modify files, helpers, credentials, or plugin wiring.
- Implement ONLY inventory fetch logic inside the existing inventory implementation surfaces.
- Do NOT touch booking, cancellation, or other flows.

Supplier & Documentation
- Supplier: Rezdy
- API Docs: https://developers.rezdy.com/rezdyapi/index-agent.html

Product Code Structure (Authoritative)
{
  "productId": "XYZ123",
  "personTypeCodes": {
    "ADULT": "Adult",
    "CHILD": "Child 3-14 years"
  },
  "pickupCustomFieldId": 218613
}

PCS Rules:
- Use ONLY productId and personTypeCodes for inventory.
- Ignore pickupCustomFieldId completely.
- Do NOT modify, infer, or enrich PCS.

Required API Calls (MANDATORY SEQUENCE)

Step 1: Fetch Product Details (Currency Source)
Endpoint:
GET /v1/products/{productCode}

Rules:
- productCode = PCS.productId
- Extract currency from the documented product currency field.
- Store currency in-memory.
- If currency is missing or null, fail loudly.
- Do NOT proceed to inventory fetch without currency.

Step 2: Fetch Availability
Endpoint:
GET /v1/availability

Query Parameters:
- productCode = PCS.productId
- startTimeLocal = requested search window start
- endTimeLocal = requested search window end
- Authentication is already handled.

Availability Mapping Rules (STRICT)

For EACH session returned by the availability response:

Date & Time:
- date = YYYY-MM-DD from session.startTimeLocal
- timeslot = HH:mm:ss from session.startTimeLocal

Seat Count & Availability:
- If session.seatsAvailable > 0:
  - availability = limited
  - seatCount = session.seatsAvailable
- If session.seatsAvailable == 0:
  - availability = closed
- If session is open but no meaningful seat count is provided:
  - availability = limited
  - seatCount = 9999

Missing Slots Rule:
- If an expected date/time slot is missing from the response:
  - Treat that slot as CLOSED.

Inventory Type Rules:
- Rezdy inventory is ALWAYS pooled.
- inventoryType = pooled
- seatCountPerPaxType = null

Pricing Mapping Rules (STRICT)

Pricing Source:
- session.priceOptions array from availability response.

Pax Mapping:
- priceOptions.label == "Adult" → ADULT
- priceOptions.label == "Child 3-14 years" → CHILD

Price Value:
- amount = priceOptions.price
- currency = value fetched from product details endpoint

Pricing Rules:
- Use ONLY the price field under priceOptions.
- Do NOT infer or calculate prices.
- Do NOT mix pricing fields.
- Do NOT convert currency.

Currency Rules (NON-NEGOTIABLE)

- Currency MUST be sourced from the product details endpoint.
- Currency MUST be attached to ALL pricing objects.
- NO currency conversion logic.
- NO fallback defaults.
- NO assumptions.
- If currency cannot be resolved, fail the inventory fetch.

Output Structure (Per Date-Time Slot)

Each inventory record MUST be emitted as:

{
  date: "YYYY-MM-DD",
  timeslot: "HH:mm:ss",
  availability: "limited" | "closed",
  inventoryType: "pooled",
  seatCount: number,
  seatCountPerPaxType: null,
  pricing: {
    ADULT: { amount: number, currency: "ISO_CODE" },
    CHILD: { amount: number, currency: "ISO_CODE" }
  }
}

Hard Constraints (Violation = Incorrect Implementation)

- Do NOT modify PCS.
- Do NOT create files.
- Do NOT add TODOs.
- Do NOT add booking or cancellation logic.
- Do NOT assume independent inventory.
- Do NOT guess currency.
- Do NOT perform currency conversion.
- Do NOT ignore missing sessions.

Produce production-ready InventoryFetch logic strictly aligned with Headout inventory standards.

</DEVIN_PROMPT>
"""