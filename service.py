from agent_integration import Devin, ChatGPT
from prompts.base_prompt.base_prompt import VEDNOR_PLUGIN_BASE_PROMPT
from prompts.inventory_prompt.inventory_prompt import VENDOR_PLUGIN_INVENTORY_PROMPT
from prompts.inventory_prompt.inventory_prompt_response_format import VENDOR_PLUGIN_INVENTORY_PROMPT_RESPONSE_FORMAT
from models.base_prompt_request import PluginBasePromptRequest
from models.inventory_promot_request import InventoryPromptRequest

class IntegrationService:
    def __init__(self):
        self.devin_instance = Devin()
        self.chat_gpt = ChatGPT()

    def implement_vendor_integration(self, payload: PluginBasePromptRequest):
        base_prompt = VEDNOR_PLUGIN_BASE_PROMPT.format(
            vendor_plugin_name = payload["plugin_name"],
            api_documentation = payload["resource_link"],
            pull_request_title = payload["pull_request_title"]
        )

        session_id = self.devin_instance.create_new_devin_session(prompt=base_prompt)
        return session_id
    
    def send_followup_on_session_id(self, payload: InventoryPromptRequest):
        inventory_prompt = VENDOR_PLUGIN_INVENTORY_PROMPT.format(
            api_documentation = payload["api_documentation"],
            product_code_structure =      payload["product_code_structure"],
            pricing_field_rules = payload["pricing_field_rules"],
            currency_handling_strategy = payload["currency_handling_strategy"]
        )

        response_format = VENDOR_PLUGIN_INVENTORY_PROMPT
        final_prompt = self.chat_gpt.get_devin_prompt(inventory_prompt, response_format)
        result = self.devin_instance.send_followp_message_on_session(
            session_id=payload["session_id"], prompt=final_prompt
        )
        return result
    
    def get_session_status(self, session_id):
        result = self.devin_instance.get_session_status(session_id)
        return result
