VEDNOR_PLUGIN_BASE_PROMPT = """
ROLE
You are a senior backend engineer working in the `devin-testing-rms-code-gen` repository.

Your task is to integrate a new vendor plugin named {vendor_plugin_name}
by generating all required files, models, APIs, helpers, and plugin scaffolding
STRICTLY based on the vendor API documentation provided.

Pull Request should be titled with {pull_request_title}


MANDATORY CONTEXT LOADING (DO THIS FIRST)
Before reading the vendor documentation or generating any code, you MUST:

1. Explore the `vendor-plugins` directory in the repository (https://github.com/headout/devin-testing-rms-code-gen/).
2. Identify all existing vendor plugins already integrated.
3. Understand, at a high level, for EACH plugin:
   - Folder structure
   - Which files exist
   - Which interfaces are implemented
   - How APIs, helpers, credentials, authentication, and rate limiting are structured
4. Treat the existing plugins as the canonical source of truth for:
   - Architecture
   - File layout
   - Naming conventions
   - Class responsibilities
   - Wiring and initialization flow

You must align the new plugin with these established patterns unless the vendor
documentation explicitly requires a deviation.


REFERENCE REPOSITORY
https://github.com/headout/devin-testing-rms-code-gen


INPUTS
- Vendor Plugin Name: {vendor_plugin_name}
- Vendor Documentation Source:
  - Either a documentation URL
  - OR an attached documentation file (PDF / DOC / Markdown)

Documentation input:
{api_documentation}


MANDATORY PRE-EXECUTION REQUIREMENT
After loading repository context and BEFORE generating any code, you MUST open
and fully parse the provided documentation (link OR attached file).

You must extract ONLY what is explicitly documented, including:
- API endpoints (HTTP method, path)
- Authentication mechanism
- Headers, query params, and path params
- Request schemas (field names, data types, optionality)
- Response schemas (success and error)
- Nested objects
- Enum values and allowed values
- Pagination or cursor models (if present)
- Sample request and response payloads
- Rate-limiting information (if documented)

DO NOT guess, infer, or fabricate any fields, APIs, or behavior.


STEP 1: FOLDER STRUCTURE
Create a new folder at:

devin-testing-rms-code-gen/
└── vendor-plugins/
    └── src/main/java/com/headout/vendor/plugins/{vendor_plugin_name}/


STEP 2: API MODELS (PATH-FIXED & STRICTLY NON-AGGREGATED)

All API models MUST be created under:

vendor-plugins/
└── src/main/java/com/headout/vendor/plugins/{vendor_plugin_name}/
    └── models/

Create the following directory structure EXACTLY:

models/
├── requests/
├── responses/
├── errors/
└── enums/

Package declarations MUST exactly match directory paths:

- requests:
  package com.headout.vendor.plugins.{vendor_plugin_name}.models.requests
- responses:
  package com.headout.vendor.plugins.{vendor_plugin_name}.models.responses
- errors:
  package com.headout.vendor.plugins.{vendor_plugin_name}.models.errors
- enums:
  package com.headout.vendor.plugins.{vendor_plugin_name}.models.enums


FILE-LEVEL CONSTRAINTS (MANDATORY)

Requests:
- Each request payload MUST be in its own file
- File name: <OperationName>Request.kt
- File MUST contain exactly ONE top-level request data class

Responses:
- Each response payload MUST be in its own file
- File name: <OperationName>Response.kt
- File MUST contain exactly ONE top-level response data class

Errors:
- Each documented error response MUST be in its own file

Enums:
- Each enum MUST be in its own file
- Enums MUST NOT be embedded in request/response files


NESTED OBJECT RULES (CRITICAL)

- Nested DTOs MUST NOT be defined as inner classes
- Each nested object MUST:
  - Be extracted into its own file
  - Live in the same directory as its parent
- File naming:
  <ParentName><NestedName>.kt


STRICTLY FORBIDDEN (HARD FAIL)

DO NOT create:
- Requests.kt
- Responses.kt
- Models.kt
- Dtos.kt
- Any file that aggregates multiple request or response models

DO NOT place more than one top-level request or response class in a single file.

If any forbidden pattern is produced, the output is invalid.


STEP 3: API INTERFACE AND RATE LIMITING
Create:

api/{vendor_plugin_name}API.kt

Implement:
1. A Retrofit (or vendor-appropriate) API interface
   - One function per documented API endpoint
   - Correct HTTP method, path, headers, parameters, and request body

2. A rate-limited wrapper class
   - Class name: {vendor_plugin_name}ApiRateLimited (or repository-consistent equivalent)
   - Wrap all API calls
   - Follow rate-limiting patterns used in other vendor plugins


STEP 4: CREDENTIALS HANDLING
Create:

{vendor_plugin_name}Credentials.kt

Requirements:
- Implement credentials handling based strictly on the vendor authentication mechanism
- Follow patterns used in other vendor plugins
- Do not hardcode secrets or tokens


STEP 5: PLUGIN HELPER (STRICT WIRING-ONLY, NO FACTORIES)

Create:

{vendor_plugin_name}PluginHelper.kt

The PluginHelper MUST:

- Extend `AbstractPluginHelper`
- Act ONLY as a wiring container
- Contain NO business logic
- Contain NO runtime decision-making
- Contain NO factory methods

API INSTANTIATION RULES (CRITICAL)

You MUST create EXACTLY TWO concrete API instances as properties:

1. One NON-rate-limited API instance
2. One rate-limited API instance

Both instances MUST:
- Be eagerly initialized
- Be independent
- Be explicitly named
- Decide rate limiting at construction time

REQUIRED PROPERTY PATTERN:

val {vendor_plugin_name}Api: VendorApiInterface
val {vendor_plugin_name}RateLimitedApi: VendorApiInterface

FORBIDDEN PATTERNS (HARD FAIL)

DO NOT:
- Create methods like `getApi()`, `getRateLimitedApi()`, or `getRetrofitApi()`
- Use boolean flags such as `limiterEnabled`, `useRateLimiter`, etc.
- Use conditional logic to choose APIs
- Lazily initialize APIs
- Share a single API instance with multiple behaviors

If any forbidden pattern is generated, the output is invalid.

Follow the structural patterns of:
- OutboxPluginHelper
- BookingKitPluginHelper
- Burj2PluginHelper
- GoCityPluginHelper

STEP 6: PRODUCT CODE LOGIC
Create:

{vendor_plugin_name}Code.kt

Requirements:
- Implement product code structure following existing plugin conventions
- If vendor rules are unclear or undocumented, keep logic minimal and deterministic


STEP 7: MAIN PLUGIN CLASS

Create:

{vendor_plugin_name}Plugin.kt

CRITICAL RULE — NO BUSINESS LOGIC IN {vendor_plugin_name}Plugin

The plugin class MUST:
- Contain ONLY method signatures and wiring
- NOT call vendor APIs
- NOT perform transformations or computations

All overridden methods must:
- Have empty bodies, OR
- Return default/empty values, OR
- Throw UnsupportedOperationException

Implement:

class {vendor_plugin_name}Plugin :
    IVendorBookingPlugin<{vendor_plugin_name}>,
    IPluginDescription,
    IPrimaryProductCodeValidator,
    IVendorPcgHelper<{vendor_plugin_name}>,
    ProductCodeValidationSupport<{vendor_plugin_name}>,
    IVendorInventoryCheckPluginV1<{vendor_plugin_name}>,
    IVendorInventoryCheckPluginV2<{vendor_plugin_name}>,
    IVendorInventoryPluginV2<{vendor_plugin_name}>


GLOBAL CONSTRAINTS
- Follow existing repository formatting and conventions exactly
- No TODOs, mock data, or speculative implementations
- No breaking changes to shared code
- Assume the output will be compiled immediately


FINAL OUTPUT EXPECTATION
Produce a complete, compilable vendor plugin implementation that:
- Strictly reflects the provided documentation
- Matches the architecture of existing vendor plugins
- Is ready for further business-logic iteration
"""
