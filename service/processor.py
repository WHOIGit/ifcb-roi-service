"""Stateless template processor."""

from typing import List

from pydantic import BaseModel, Field

from stateless_microservice import BaseProcessor, StatelessAction, run_blocking

from service.roistore import IfcbRoiStore

class RoiParams(BaseModel):
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
                path="/roi-image/{pid}",
                path_params_model=RoiParams,
                handler=self.handle_roi_image,
                methods=["GET"],
                summary="Get ROI image.",
                description="Get ROI image.",
                tags=("roi",),
                media_type="application/json",
            ),
        ]

    async def handle_roi_image(self, path_params: RoiParams):
        """Get ROI image."""
        from ifcb import Pid
        pid = Pid(path_params.pid)
        bin_lid = pid.bin_lid
        encoded_image_data = await run_blocking(self.store.get, path_params.pid)
        return {
            "pid": path_params.pid,
            "bin-pid": bin_lid,
            "content-type": "image/png",
            "image": encoded_image_data
        }
