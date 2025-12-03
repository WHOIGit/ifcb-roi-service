from storage.object import ObjectStore
from storage.utils import ReadonlyStore, Base64Store, ExceptionLoggingStore

from ifcb import DataDirectory
from ifcb.data.imageio import format_image
from ifcb import Pid

class Base64EncodingStore(Base64Store):
    def transform(self, value):
        super().reverse_transform(value)

    def reverse_transform(self, data):
        return super().transform(data)
    

class IfcbRoiStore(ObjectStore):
    """Readonly store for accessing IFCB ROI images and associated technical metadata."""

    @classmethod
    def base64_store(cls, data_dir: str = "/data/ifcb") -> Base64Store:
        """Create a Base64Store for IFCB ROI images."""
        return Base64EncodingStore(cls(data_dir=data_dir))
    
    def __init__(self, data_dir: str = "/data/ifcb"):
        super().__init__()
        self.data_dir = data_dir

    def get(self, key):
        """Get ROI image and metadata by pid."""
        pid = Pid(key)
        bin_lid = pid.bin_lid
        target_number = int(pid.target)
        data_dir = DataDirectory(self.data_dir)
        b = data_dir[bin_lid]
        with b.as_single(target_number) as single_bin:
            image_array = single_bin.images[target_number]
            image_data = format_image(image_array, "image/png").getvalue()
        print(f'retrieved {len(image_data)} bytes for pid {key}')
        return image_data

    def exists(self, key) -> bool:
        """Check if ROI image exists for given pid."""
        pid = Pid(key)
        bin_lid = pid.bin_lid
        target_number = int(pid.target)
        data_dir = DataDirectory(self.data_dir)
        if bin_lid not in data_dir:
            return False
        b = data_dir[bin_lid]
        return target_number in b.images.keys()

    def put(self, key, value):
        """Put is not supported for readonly store."""
        raise NotImplementedError("Put operation is not supported for IfcbRoiStore.")

    def delete(self, key):
        """Delete is not supported for readonly store."""
        raise NotImplementedError("Delete operation is not supported for IfcbRoiStore.")
