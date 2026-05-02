import os
from django.conf import settings
from cloudinary_storage.storage import MediaCloudinaryStorage

class MixedMediaStorage(MediaCloudinaryStorage):
    def url(self, name):
        if not name:
            return ""
        # Check if the file exists locally
        local_path = os.path.join(str(settings.MEDIA_ROOT), str(name))
        if os.path.exists(local_path):
            return settings.MEDIA_URL + str(name)
        # Otherwise, fall back to Cloudinary URL
        return super().url(name)
