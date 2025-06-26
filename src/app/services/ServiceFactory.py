from .ImageCaptionService import ImageCaptionService

class ServiceFactory:
    @staticmethod
    def get_image_caption_service():
        return ImageCaptionService()