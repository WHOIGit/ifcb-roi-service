"""Stateless processor for IFCB ROI images stored in S3."""

from typing import List

from pydantic import BaseModel, Field

from stateless_microservice import BaseProcessor, StatelessAction, run_blocking

from service.roistore import IfcbRoiStore


class RoiParams(BaseModel):
    pid: str = Field(..., description="ROI pid")


class IfcbRoiProcessor(BaseProcessor):
    """Processor for accessing IFCB ROI images from S3."""

    def __init__(
        self,
        bucket_name: str,
        endpoint_url: str = None,
        s3_access_key: str = None,
        s3_secret_key: str = None,
        prefix: str = "",
    ):
        """Initialize processor with S3 configuration.
        
        Args:
            bucket_name: S3 bucket name
            endpoint_url: S3 endpoint URL (optional for AWS S3)
            s3_access_key: S3 access key
            s3_secret_key: S3 secret key
            prefix: Optional key prefix for all objects
        """
        self.store = IfcbRoiStore.base64_store(
            bucket_name=bucket_name,
            endpoint_url=endpoint_url,
            s3_access_key=s3_access_key,
            s3_secret_key=s3_secret_key,
            prefix=prefix,
        )

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
                summary="Get ROI image from S3.",
                description="Get ROI image from S3 by PID.",
                tags=("roi",),
                media_type="application/json",
            ),
        ]

    async def handle_roi_image(self, path_params: RoiParams):
        """Get ROI image from S3."""
        from ifcb import Pid
        
        print(f"[PROCESSOR] Received request for PID: {path_params.pid}")
        
        pid = Pid(path_params.pid)
        bin_lid = pid.bin_lid
        print(f"[PROCESSOR] Parsed - bin_lid: {bin_lid}, target: {pid.target}")
        
        # Get base64-encoded image data from S3
        encoded_image_data = await run_blocking(self.store.get, path_params.pid)
        print(f"[PROCESSOR] Retrieved {len(encoded_image_data)} bytes")
        
        return {
            "pid": path_params.pid,
            "bin-pid": bin_lid,
            "content-type": "image/png",
            "image": encoded_image_data,
        }
