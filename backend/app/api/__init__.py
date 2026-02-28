from app.api.requirements import router as requirements_router
from app.api.defect_prediction import router as defect_prediction_router
from app.api.design_upload import router as design_upload_router

__all__ = ["requirements_router", "defect_prediction_router", "design_upload_router"]

