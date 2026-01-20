import uvicorn 
from service import IntegrationService
from fastapi import FastAPI, APIRouter, HTTPException, status
from models import base_prompt_request, inventory_promot_request


class Router:
    def __init__(self, app: FastAPI):
        self.app = app
        self.router = APIRouter()
        self.service = IntegrationService()
        self._register_routes()
        self.app.include_router(self.router)

    def _validate_data(self, request_data):
        for key, value in request_data.items():
            if value == None or value == "":
                return False

        return True

    def _register_routes(self):
        @self.router.get("/health")
        def health_check():
            return {"status": "ok"}
        
        @self.router.post("/start_plugin_integration")
        def base_prompt(body: base_prompt_request.PluginBasePromptRequest):
            payload = body.dict()
            is_valid = self._validate_data(payload)
            if not is_valid:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid data provided"
                )
            
            try:
                session_id = self.service.implement_vendor_integration(payload)
                return {
                    "session_id": session_id
                }
            except Exception as e:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=e
                )


        @self.router.post("/follow-up")
        def send_follow_up(body: inventory_promot_request.InventoryPromptRequest):
            payload = body.dict()
            is_valid = self._validate_data(payload)
            if not is_valid:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid data provided"
                )
            
            try:
                results = self.service.send_followup_on_session_id(payload)
                return {
                    "results": results
                }
            except Exception as e:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=e
                )

        @self.router.get("/session-status/{session_id}")
        def get_session_status(session_id: str):
            if not session_id or session_id == "":
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail= "Session id not found"
                )

            try:
                results = self.service.get_session_status(session_id)
                return {
                    "results": results
                }
            except Exception as e:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=e
                )

app = FastAPI()
router = Router(app)

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )