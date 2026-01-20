from pydantic import BaseModel

class InventoryPromptRequest(BaseModel):
    session_id: str
    api_documentation: str
    product_code_structure: str
    pricing_field_rules: str
    currency_handling_strategy: str