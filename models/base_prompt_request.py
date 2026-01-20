from pydantic import BaseModel

class PluginBasePromptRequest(BaseModel):
    resource_link: str
    plugin_name: str
    pull_request_title: str
