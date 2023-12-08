from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver

from .models import User, UserProfile

@receiver( post_save, sender=User )
def post_save_create_profile_receiver( sender, instance, created, **kwargs ):
  if created:
    UserProfile.objects.create( user=instance )
  else:
    try:
      profile = UserProfile.objects.get( user=instance )
      profile.save()
    except:
      UserProfile.objects.create( user=instance )
#post_save.connect( post_save_create_profile_receiver, sender=User )

@receiver( post_delete, sender=UserProfile )
def post_delete_user_profile( sender, instance, **kwargs ):
  try:
    user = instance.user
    user.delete()
  except:
    pass
