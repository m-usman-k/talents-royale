from django.db.models.signals import pre_delete
from django.dispatch import receiver
import logging

from .models import CustomUser, Contestant

logger = logging.getLogger(__name__)


@receiver(pre_delete, sender=CustomUser)
def delete_user_media(sender, instance, **kwargs):
    """Delete user's profile photo when user is deleted.
    
    Note: Contestant submissions (videos/images) will be automatically deleted
    via CASCADE relationship, which will trigger the Contestant pre_delete signal.
    """
    # Delete profile photo
    if instance.profile_photo:
        try:
            # Use storage.delete() which works with any storage backend
            instance.profile_photo.delete(save=False)
            logger.info(f"Deleted profile photo for user {instance.username}")
        except Exception as e:
            # Log error but don't prevent deletion
            logger.error(f"Error deleting profile photo for user {instance.username}: {str(e)}")


@receiver(pre_delete, sender=Contestant)
def delete_contestant_media(sender, instance, **kwargs):
    """Delete contestant's video/image files when contestant is deleted"""
    # Delete video file if it exists
    if instance.video_file:
        try:
            instance.video_file.delete(save=False)
            logger.info(f"Deleted video file for contestant {instance.id}")
        except Exception as e:
            logger.error(f"Error deleting video file for contestant {instance.id}: {str(e)}")
    
    # Delete image file if it exists
    if instance.image_file:
        try:
            instance.image_file.delete(save=False)
            logger.info(f"Deleted image file for contestant {instance.id}")
        except Exception as e:
            logger.error(f"Error deleting image file for contestant {instance.id}: {str(e)}")

