
class UploadError(Exception):
    """Custom exception for upload failures"""
    def __init__(self, message: str, *, status: int | None = None):
        super().__init__(message)
        self.status = status
