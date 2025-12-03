"""Stateless template processor."""

from typing import List

from pydantic import BaseModel, Field

from stateless_microservice import BaseProcessor, StatelessAction

from service.roistore import IfcbRoiStore

class RoiRequest(BaseModel):
    """Request payload for ROI service."""

    pid: str = Field(..., description="ROI pid")


class IfcbRoiProcessor(BaseProcessor):
    """Processor for accessing IFCB ROI images and associated technical metadata."""

    def __init__(self, data_dir: str = "/data/ifcb"):
        store = IfcbRoiStore.base64_store(data_dir=data_dir)
        self.store = store

    @property
    def name(self) -> str:
        return "ifcb_roi"

    def get_stateless_actions(self) -> List[StatelessAction]:
        return [
            StatelessAction(
                name="roi-image",
                path="/roi-image",
                request_model=RoiRequest,
                handler=self.handle_roi_image,
                summary="Get ROI image.",
                description="Get ROI image.",
                tags=("roi",),
                media_type="application/json",
            ),
        ]

    async def handle_roi_image(self, payload: RoiRequest):
        """Get ROI image."""
        from ifcb import Pid
        pid = Pid(payload.pid)
        bin_lid = pid.bin_lid
        encoded_image_data = self.store.get(payload.pid)
        return {
            "pid": payload.pid,
            "bin-pid": bin_lid,
            "content-type": "image/png",
            "image": encoded_image_data
        }