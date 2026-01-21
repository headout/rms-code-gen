VENDOR_PLUGIN_INVENTORY_PROMPT_RESPONSE_FORMAT = """
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
"""