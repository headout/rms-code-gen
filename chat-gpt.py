import openai
import os
from dotenv import load_dotenv

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

PROMPT = """
<META_PROMPT>
# Headout Inventory Fetch — API Documentation Analyzer & Devin Prompt Generator for {{api_provider_name}}
## Context
You are an expert API documentation analyst and Headout-domain specialist.
Your responsibility is to:
- Read and understand supplier API documentation
- Apply Headout's inventory model and constraints
- Apply the explicitly provided currency handling strategy
- Correctly handle pooled vs independent inventory semantics
- Ensure correct date/time handling including endTime
- Generate a **supplier-specific, Devin-ready prompt** that will result in a **correct InventoryFetch implementation**
This meta-prompt does **not** ask you to write code.
It asks you to generate the **exact prompt** that will be given to Devin, who will then write the code.
You MUST NOT infer, guess, or auto-detect behaviors that are explicitly provided as inputs.
You MUST rely strictly on:
- Supplier documentation
- Explicit inputs
- Headout inventory rules defined below
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
  - Pax type definitions (PRICE pax types)
  - Possibly booking-only custom/user fields
  - Possibly an `apiCurrency` field (only if explicitly provided)
**Rules:**
- PCS is immutable
- PCS must NOT be modified or inferred
- Booking-only custom/user fields in PCS must be ignored for inventory fetch
- PCS pax types represent **PRICE pax types**, not necessarily inventory pax types
---
## Inventory Semantics (Strict Rules)
### Availability
- Inventory is fetched using supplier identifiers from PCS
- Availability is mapped per:
  - Date
  - Time slot (if applicable)
  - Inventory pax type (see pooled vs independent section)
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
---
## Pooled vs Independent Inventory (CRITICAL — DO NOT MISINTERPRET)
### Determination
- If availability is shared across pax types:
  - Treat as **POOLED**
- If availability is provided per pax type:
  - Treat as **INDEPENDENT**
- Determination MUST be made strictly from supplier documentation and response structure
### Inventory Pax Types vs Price Pax Types (MANDATORY DISTINCTION)
**This distinction is CRITICAL and MUST be enforced in all Devin prompts.**
- **Inventory pax types** are defined by Headout configuration (e.g. `query.inventoryPaxTypes`)
- **Price pax types** are defined in PCS
Rules:
- InventoryInfo MUST be created using **inventory pax types ONLY**
- Pricing MUST be created using **PCS pax types ONLY**
- Inventory pax types ≠ Price pax types
#### Pooled Inventory Rules
- Inventory is stored at **slot level**, not per price pax
- InventoryInfo MUST be created using:
  - `query.inventoryPaxTypes`
  - NOT PCS pax types
  - NOT hardcoded values like `GENERAL`
- Example intent:
  - One InventoryInfo entry per slot
  - Multiple InventoryPriceInfo entries (Adult, Child, etc.)
#### Independent Inventory Rules
- InventoryInfo is created per inventory pax type
- Pricing still uses PCS pax types
**Under NO circumstances should Devin:**
- Use PCS pax types to construct InventoryInfo
- Hardcode inventory pax types
- Assume inventory pax types equal price pax types
---
## Pricing (Strict)
- Pricing field selection is predefined and provided separately
- If multiple prices exist:
  - Use only the explicitly instructed price field
- Pricing must be mapped per PCS pax type
- Pricing must ALWAYS be accompanied by a currency code
---
## Currency Handling (Authoritative, Explicit, Non-Negotiable)
Currency handling MUST follow the explicitly provided strategy.
You MUST NOT infer, guess, or fallback.
Exactly ONE of the following strategies will be provided as input:
### Strategy A — Currency Present in Supplier Response
- Supplier provides currency explicitly in API responses
- Currency MAY come from:
  - Inventory endpoint response
  - OR a different documented endpoint (e.g., product/details)
Rules:
- Use the exact documented field and endpoint
- If currency comes from a non-inventory endpoint:
  - Fetch it first
  - Store it in-memory
  - Attach it to ALL pricing objects
- Do NOT infer currency from price values
### Strategy B — Currency Provided via Product Code Structure
- Supplier does NOT return currency in any API response
- PCS contains an explicitly defined `apiCurrency`
Rules:
- Always use PCS.apiCurrency
- Ignore all currency fields in API responses (if any)
### Strategy C — Currency Passed as Request Parameter (IMPORTANT FIX)
- Supplier API supports passing currency as a request parameter
- Prices are returned in the requested currency
**Correct Rules (MANDATORY):**
- Devin MUST NOT expect currency from PCS
- Devin MUST NOT infer currency from API responses
- Currency MUST be set as:
  - `currency = product.defaultCurrency`
- product.defaultCurrency is authoritative
- Attach product.defaultCurrency to ALL pricing objects
### Global Currency Rules
- Inventory Fetch MUST always output price + currency
- NO currency conversion logic is allowed
- NO fallback, guessing, or hybrid logic
- Headout FX systems handle conversion downstream
---
## Date & Time Handling (CRITICAL)
### Start Time
- MUST be read from supplier response if provided
- MUST be formatted exactly as required by Headout
### End Time (CRITICAL FIX)
Rules:
- If supplier provides `endTime` in response:
  - Devin MUST read it
  - Devin MUST map it explicitly
  - Devin MUST format it exactly as required
- Devin MUST NOT:
  - Calculate endTime unless documentation explicitly instructs so
  - Assume endTime == startTime
  - Leave endTime unset when present in response
- If endTime is NOT provided and documentation does NOT specify derivation:
  - End time MUST be omitted or left null (as per Headout contract)
---
## Inputs
### Primary Inputs
- **Supplier API Documentation**
  {{api_documentation}}
- **Product Code Structure (PCS)**
  {{product_code_structure}}
- **Pricing Field Selection Rules**
  {{pricing_field_rules}}
- **Currency Handling Strategy**
  {{currency_handling_strategy}}
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
- Inventory pax types vs price pax types
- Time-slot handling (startTime and endTime)
- Currency-related fields or endpoints (only if strategy requires)
### Step 2: Map Supplier Concepts to Headout Inventory Model
Determine:
- Which supplier identifiers from PCS are used
- How availability maps to TID_VID
- Which pax types are inventory pax types
- Which pax types are price pax types
- How remaining seats are calculated
- How pricing and currency are attached
- How startTime and endTime are mapped
### Step 3: Generate Two Outputs
---
## Output 1 — Inventory Mapping & Reasoning (For Humans)
Produce a clear explanation covering:
- Inventory endpoints
- Inventory pax vs price pax handling
- Pooled vs independent determination
- Seat count logic
- Time-slot handling (including endTime)
- Pricing and currency strategy application
---
## Output 2 — Final Devin Prompt (Strict, Copy-Paste Ready)
Generate a **single, complete prompt** addressed to Devin.
The Devin prompt MUST:
- Assume files and scaffolding already exist
- Implement InventoryFetch ONLY
- Enforce inventory pax ≠ price pax logic
- Correctly handle pooled vs independent inventory
- Correctly apply currency strategy (especially Strategy C)
- Correctly map startTime and endTime
- Never infer or hardcode pax behavior
- Never implement currency conversion
- Never partially update inventory
The Devin prompt MUST be:
- Deterministic
- Implementation-oriented
- Free of analysis text
- Impossible to misinterpret
---
## Output Format (Mandatory)
Return your response in the following structure only:
<ANALYSIS_AND_MAPPING>
...
</ANALYSIS_AND_MAPPING>
<DEVIN_PROMPT>
...
</DEVIN_PROMPT>
No additional commentary outside these sections.
</META_PROMPT>
"""

EXTRA_DETAILS = """
Documentation link - https://docs.ventrata.com/
PCS - { "productId": "2d343f5d-dc9f-42d1-8166-202aee884836", "optionId": "cf15cb08-fa82-49e0-a5bf-8458147fbfab", "personTypeMap": { "ADULT": "unit_8c07647f-e750-4592-9adf-874728fdee03", "CHILD": "unit_6fe07069-4b42-4d98-af1f-7be8b09df4fc", "INFANT": "unit_63ccc8cd-e657-4f80-ae6c-7067d3351a88" }, "customFieldMap": { "PICK_UP_POINT": 12345 }, "contactOptionCustomFieldMap": { "country": 67890 } }
Price to be picked up from "retail" field under unitPricing for each pax type
Currency Handling Strategy will be strategy C we will send a currency param
"""

FULL_PROMPT = PROMPT + "\n\n" + EXTRA_DETAILS


RESPONSE_FORMAT = """
<META_DEVIN_PROMPT_SKELETON>

ROLE
You are a senior backend engineer working in the target repository that contains
existing plugin scaffolding for supplier integrations.

Your task is to generate a **Devin-compatible implementation prompt** for
**ONE specific plugin at a time**, covering **ONLY the requested flow**
(e.g., InventoryFetch), with **no assumptions, no inference, and no omissions**.

--------------------------------------------------
SECTION 1 — HARD SCOPE & GUARANTEES (NON-NEGOTIABLE)
--------------------------------------------------
Define **absolute boundaries** for the generated Devin prompt.

The prompt MUST explicitly state:
- Which flow(s) are IN scope (e.g., InventoryFetch ONLY)
- Which flows are OUT of scope (booking, cancellation, refunds, etc.)
- That existing files, scaffolding, helpers, API clients, and wiring ALREADY exist
- That files MUST NOT be created, modified, renamed, or moved
- That behavior must be deterministic and production-ready

The prompt MUST explicitly forbid:
- Partial success
- Silent fallback
- Inference or guessing
- Skipping documented behavior
- FX or currency conversion (unless explicitly required)

--------------------------------------------------
SECTION 2 — SUPPLIER CONTEXT (PLUGIN-SPECIFIC, AUTHORITATIVE)
--------------------------------------------------
Provide placeholders for:
- Supplier name
- Authoritative documentation URL(s)

Instruct that:
- Documentation is the single source of truth
- All behavior related to endpoints, pagination, date/time formats,
  timezone semantics, request parameters, and response fields
  MUST be taken strictly from documentation
- Any undocumented assumption is a HARD FAILURE

--------------------------------------------------
SECTION 3 — PRODUCT / VARIANT IDENTIFIER CONTEXT (IMMUTABLE INPUTS)
--------------------------------------------------
Define an **immutable input block** (e.g., PCS / variant config).

The skeleton MUST require:
- Explicit listing of all identifiers used for fetch
- Clear separation of:
  - Inventory identifiers
  - Pricing identifiers
  - Booking-only identifiers

The prompt MUST state:
- Which fields are allowed to be used
- Which fields MUST be ignored
- That identifiers MUST NOT be inferred or transformed

--------------------------------------------------
SECTION 4 — FLOW-SPECIFIC RESPONSIBILITIES
--------------------------------------------------
Explicitly enumerate what the flow MUST do.

Examples (flow-dependent):
- Fetch availability
- Fetch capacity
- Fetch pricing
- Fetch currency
- Normalize supplier response to Headout semantics

Explicitly enumerate what the flow MUST NOT do.

--------------------------------------------------
SECTION 5 — CURRENCY STRATEGY (PLUGGABLE)
--------------------------------------------------
Define a **currency strategy section** with placeholders for:
- Source of currency (e.g., product field, city field, supplier response)
- Whether currency is passed as request parameter
- Whether conversion is allowed (default: NOT allowed)

The skeleton MUST enforce:
- Explicit currency source
- Explicit attachment of currency to pricing
- Explicit prohibition of inference or fallback

--------------------------------------------------
SECTION 6 — SUPPLIER API USAGE
--------------------------------------------------
Define placeholders for:
- Endpoint(s) to call
- HTTP method(s)
- Required request parameters
- Optional request parameters
- Any request payload enrichment needed to receive pricing or availability

The prompt MUST require:
- Strict adherence to documented formats
- Hard failure on missing required params
- Explicit handling instructions for optional params

--------------------------------------------------
SECTION 7 — PAGINATION (MANDATORY CHECKPOINT)
--------------------------------------------------
The skeleton MUST include a mandatory pagination section that requires the generated prompt to:
- Explicitly state whether pagination exists
- Define how pagination is detected
- Define how pages are iterated
- Require aggregation before processing

The prompt MUST enforce:
- Full pagination or hard failure
- No partial inventory return

--------------------------------------------------
SECTION 8 — INVENTORY MODEL (CONFIGURABLE)
--------------------------------------------------
Provide a **neutral inventory-model section** that can be specialized per plugin.

The skeleton MUST require the generated prompt to explicitly define:
- Inventory model: POOLED or INDEPENDENT
- Source of inventory pax types
- Prohibited pax sources
- Cardinality rules (e.g., one record per slot, per pax, etc.)

The skeleton MUST forbid:
- Mixing pricing pax with inventory pax
- Hardcoding pax types

--------------------------------------------------
SECTION 9 — AVAILABILITY & SEAT SEMANTICS
--------------------------------------------------
Require the generated prompt to define:
- How remaining seats are computed
- How unlimited capacity is represented
- How closed / sold-out states are represented
- Precedence rules between availability status and capacity fields

--------------------------------------------------
SECTION 10 — SLOT & TIME HANDLING
--------------------------------------------------
Require explicit definition of:
- Slot identity (date + time)
- Start time sourcing
- End time sourcing
- Whether derivation is allowed (default: NOT allowed)
- Timezone handling rules

The skeleton MUST require:
- Hard failure on invalid formats
- No invented times

--------------------------------------------------
SECTION 11 — CLOSED-BY-OMISSION POLICY
--------------------------------------------------
Require the generated prompt to explicitly define:
- Whether omission-based closure is supported
- Preconditions for applying it (e.g., prior slots provided)
- Prohibition on fabricating unknown slots

--------------------------------------------------
SECTION 12 — PRICING & PAX HANDLING
--------------------------------------------------
Require explicit definition of:
- Pricing source fields
- Pax-to-price mapping logic
- Whether pax completeness is required

The skeleton MUST allow enforcing:
- STRICT pax completeness (recommended default)
- Hard failure on missing pax pricing
- Explicit prohibition of partial pricing

--------------------------------------------------
SECTION 13 — ERROR HANDLING & FAILURE POLICY
--------------------------------------------------
The skeleton MUST require the generated prompt to enumerate:
- All conditions that MUST throw hard exceptions
- Explicit statement that partial success is forbidden
- Explicit statement that violations of documentation are fatal

--------------------------------------------------
SECTION 14 — FINAL CONSTRAINTS & DELIVERABLE
--------------------------------------------------
Require the generated prompt to end with:
- Reiteration of determinism
- No TODOs
- No mock data
- No speculative logic
- Clear statement of the exact deliverable
  (e.g., “A complete InventoryFetch implementation for <SUPPLIER>”)

--------------------------------------------------
META-INSTRUCTION TO THE OTHER LLM
--------------------------------------------------
When generating a Devin prompt using this skeleton:
- Fill EVERY section explicitly
- Do NOT remove sections
- Do NOT collapse sections
- Do NOT assume defaults
- If supplier behavior is unknown, force a HARD FAILURE rule
- Prefer over-specification to under-specification

</META_DEVIN_PROMPT_SKELETON>
"""

def chat():
    client = openai.OpenAI(api_key=OPENAI_API_KEY)
    # breakpoint()
    response = client.responses.create(
        model="gpt-5.2",
        reasoning={"effort": "high"},
        input=[
          {
              "role": "system",
              "content": "You are a strict compiler of Devin execution prompts. Precision over verbosity."
          },
          {
              "role": "user",
              "content": FULL_PROMPT
          },
          {
              "role": "user",
              "content": f"Assuming the response should follow the format given -" + RESPONSE_FORMAT
              
          }
        ],
    )
    # breakpoint()
    print(response.output[1].content[0].text)


chat()

