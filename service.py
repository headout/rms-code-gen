from agent_integration import Devin
from prompts.base_prompt import DEVIN_VENDOR_PLUGIN_BASE_PROMPT
from prompts.inventory_promot import DEVIN_INVENTORY_FETCH_PROMPT
from prompts.delimiter_prompt import DEVIN_INVENTORY_DELIMITER
from models.base_prompt_request import PluginBasePromptRequest
from models.follow_up_request import PluguinFollowUp

class IntegrationService:
    def __init__(self):
        self.devin_instance = Devin()

    def implement_vendor_integration(self, payload: PluginBasePromptRequest):
        base_prompt = DEVIN_VENDOR_PLUGIN_BASE_PROMPT.format(
            vendor_plugin_name = payload["plugin_name"],
            api_documentation = payload["resource_link"],
            pull_request_title = payload["pull_request_title"]
        )

        session_id = self.devin_instance.create_new_devin_session(prompt=base_prompt)
        return session_id
    
    def send_followup_on_session_id(self, payload: PluguinFollowUp):
        inventory_prompt = DEVIN_INVENTORY_FETCH_PROMPT.format()
        result = self.devin_instance.send_followp_message_on_session(
            session_id=payload["session_id"], prompt=inventory_prompt
        )
        return result
    
    def get_session_status(self, session_id):
        result = self.devin_instance.get_session_status(session_id)
        return result
