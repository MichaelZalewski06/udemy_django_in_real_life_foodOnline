from datetime import date, datetime, time

from django.db import models

from django.contrib.auth.models import AbstractBaseUser, BaseUserManager

from accounts.models import User, UserProfile
from accounts.utils import send_notification

# Create your models here.

class Vendor( models.Model ):
  user = models.OneToOneField( User, related_name='user', on_delete=models.CASCADE )
  user_profile = models.OneToOneField( UserProfile, related_name='userprofile', on_delete=models.CASCADE )
  vendor_name = models.CharField( max_length=50 )
  vendor_slug = models.CharField( max_length=100, unique=True )
  vendor_license = models.ImageField( upload_to='vendor/license' )
  is_approved = models.BooleanField( default=False )
  created_at = models.DateTimeField( auto_now_add=True )
  modified_at = models.DateTimeField( auto_now=True )

  def __str__( self ):
    return self.vendor_name

  def is_open( self ):
    today = date.today()
    weekday = today.isoweekday()
    current_hours = OpeningHour.objects.filter( vendor=self, day=weekday )

    now = datetime.now()
    now_time = now.strftime( "%H:%M:%S" )
    is_open = None
    for hour in current_hours:
      if hour.is_closed:
        is_open = False
        break
      open = str( datetime.strptime( hour.from_hour, "%I:%M %p" ).time() )
      close = str( datetime.strptime( hour.to_hour, "%I:%M %p" ).time() )
      if now_time >= open and now_time <= close:
        is_open = True
        break
      else:
        is_open = False
    return is_open

  def save( self, *args, **kwargs ):
    if self.pk is not None:
      orig = Vendor.objects.get( pk=self.pk )
      if orig.is_approved != self.is_approved:
        mail_subject = 'Congratulations! Your restaurant has been approved!'
        mail_template = 'accounts/emails/admin_approval_email.html'
        if self.is_approved != True:
          mail_subject = 'Sorry, you are not eligible for publishing your menu in our marketplace.'
          mail_template = 'accounts/emails/admin_approval_email.html'

        context = {
          'user': self.user,
          'is_approved': self.is_approved,
          'to_email': self.user.email,
        }
        send_notification( mail_subject, mail_template, context )
    
    return super( Vendor, self ).save( *args, **kwargs )

DAYS = [
  (1, ("Monday")),
  (2, ("Tuesday")),
  (3, ("Wednesday")),
  (4, ("Thursday")),
  (5, ("Friday")),
  (6, ("Saturday")),
  (7, ("Sunday")),
]

HOUR_OF_DAY_24 = [(time(h, m).strftime('%I:%M %p'), time(h, m).strftime('%I:%M %p')) 
    for h in range(0, 24) for m in (0, 30)]

class OpeningHour(models.Model):
  vendor = models.ForeignKey( Vendor, on_delete=models.CASCADE )
  day = models.IntegerField( choices=DAYS )
  from_hour = models.CharField( choices=HOUR_OF_DAY_24, max_length=10, blank=True )
  to_hour = models.CharField( choices=HOUR_OF_DAY_24, max_length=10, blank=True )
  is_closed = models.BooleanField( default=False )

  class Meta:
    ordering = ( 'day', '-from_hour' )
    unique_together = ('vendor', 'day', 'from_hour', 'to_hour')

  def __str__(self):
    return self.get_day_display()