"""S3-backed store for IFCB ROI images."""

from storage.object import ObjectStore
from storage.s3 import BucketStore
from storage.utils import Base64Store

from ifcb import Pid
from ifcb.data.imageio import format_image


class IfcbRoiStore(ObjectStore):
    """S3-backed store for accessing IFCB ROI images."""

    @classmethod
    def base64_store(
        cls,
        bucket_name: str,
        endpoint_url: str = None,
        s3_access_key: str = None,
        s3_secret_key: str = None,
        prefix: str = "",
    ) -> Base64Store:
        """Create a Base64Store for IFCB ROI images stored in S3.
        
        Args:
            bucket_name: S3 bucket name
            endpoint_url: S3 endpoint URL (optional for AWS S3)
            s3_access_key: S3 access key
            s3_secret_key: S3 secret key
            prefix: Optional key prefix for all objects in the bucket
        """
        store = cls(
            bucket_name=bucket_name,
            endpoint_url=endpoint_url,
            s3_access_key=s3_access_key,
            s3_secret_key=s3_secret_key,
            prefix=prefix,
        )
        return Base64Store(store)

    def __init__(
        self,
        bucket_name: str,
        endpoint_url: str = None,
        s3_access_key: str = None,
        s3_secret_key: str = None,
        prefix: str = "",
    ):
        """Initialize S3-backed ROI store.
        
        Args:
            bucket_name: S3 bucket name
            endpoint_url: S3 endpoint URL (optional for AWS S3)
            s3_access_key: S3 access key
            s3_secret_key: S3 secret key
            prefix: Optional key prefix for all objects in the bucket
        """
        super().__init__()
        self.bucket_store = BucketStore(
            bucket_name=bucket_name,
            endpoint_url=endpoint_url,
            s3_access_key=s3_access_key,
            s3_secret_key=s3_secret_key,
        )
        self.prefix = prefix.rstrip("/")

    def _make_key(self, pid: str) -> str:
        """Convert PID to S3 key.
        
        The key structure is:
        {prefix}/{year}/{bin_lid}/{roi_number:05d}.png
        
        PID format: <bin_lid>_<roi_number>
        roi_number is zero-padded to 5 digits.
        
        Example: ifcb-data/2017/D20170512T092752_IFCB010/00319.png
        """
        parsed_pid = Pid(pid)
        bin_lid = parsed_pid.bin_lid
        roi_number = int(parsed_pid.target)
        
        # Extract year from bin_lid (bins start with 'D' followed by year)
        year = bin_lid[1:5] if bin_lid.startswith("D") else "legacy"
        
        # Generate key with 5-digit zero-padded ROI number
        if self.prefix:
            key = f"{self.prefix}/{year}/{bin_lid}/{roi_number:05d}.png"
        else:
            key = f"{year}/{bin_lid}/{roi_number:05d}.png"
            
        return key

    def get(self, key: str) -> bytes:
        """Get ROI image data by PID.
        
        Args:
            key: ROI PID
            
        Returns:
            PNG image data as bytes
        """
        s3_key = self._make_key(key)
        print(f"Retrieving S3 object: {s3_key}")
        
        try:
            image_data = self.bucket_store.get(s3_key)
            print(f"Retrieved {len(image_data)} bytes for pid {key}")
            return image_data
        except Exception as e:
            print(f"Error retrieving {s3_key}: {e}")
            raise

    def exists(self, key: str) -> bool:
        """Check if ROI image exists for given PID.
        
        Args:
            key: ROI PID
            
        Returns:
            True if the image exists in S3
        """
        s3_key = self._make_key(key)
        return self.bucket_store.exists(s3_key)

    def put(self, key: str, value: bytes):
        """Store ROI image data.
        
        Args:
            key: ROI PID
            value: PNG image data as bytes
        """
        s3_key = self._make_key(key)
        print(f"Storing S3 object: {s3_key} ({len(value)} bytes)")
        self.bucket_store.put(s3_key, value)

    def delete(self, key: str):
        """Delete ROI image.
        
        Args:
            key: ROI PID
        """
        s3_key = self._make_key(key)
        print(f"Deleting S3 object: {s3_key}")
        self.bucket_store.delete(s3_key)

    def keys(self):
        """List all PID keys in the store.
        
        Yields:
            PID strings
        """
        # This would need to parse S3 keys back into PIDs
        # Implementation depends on your specific key structure needs
        for s3_key in self.bucket_store.keys():
            # Parse back to PID format if needed
            yield s3_key
