from django.db import models
from django.contrib.auth.models import BaseUserManager, AbstractBaseUser, PermissionsMixin
from django.db.models.signals import post_save
from django.core.mail import send_mail
from django.dispatch import receiver
from uuid import uuid4
from django.conf import settings


CATEGORY_CHOICES = [
        ('Podcasts', 'Podcasts'),
        ('Educational', 'Educational'),
        ('Music', 'Music'),
        ('Gaming', 'Gaming'),
        ('Vlogs', 'Vlogs'),
        ('Technology', 'Technology'),
        ('Lifestyle', 'Lifestyle'),
        ('Travel', 'Travel'),
        ('Fitness', 'Fitness'),
        ('Food & Cooking', 'Food & Cooking'),
        ('Beauty & Fashion', 'Beauty & Fashion'),
        ('Comedy', 'Comedy'),
        ('DIY & Crafts', 'DIY & Crafts'),
        ('Reviews & Unboxing', 'Reviews & Unboxing'),
        ('Motivational', 'Motivational'),
        ('Science & Experiments', 'Science & Experiments'),
        ('News & Politics', 'News & Politics'),
        ('Sports', 'Sports'),
        ('Animation', 'Animation'),
        ('Documentary', 'Documentary'),
        ('History', 'History'),
        ('Art & Design', 'Art & Design'),
        ('Business & Finance', 'Business & Finance'),
        ('Health & Wellness', 'Health & Wellness'),
        ('Parenting', 'Parenting'),
        ('ASMR', 'ASMR'),
        ('Short Films', 'Short Films'),
        ('Spirituality', 'Spirituality'),
        ('Wildlife & Nature', 'Wildlife & Nature'),
        ('Tutorials', 'Tutorials'),
    ]

class CustomUserManager(BaseUserManager):
    def create_user(self, email, password = None, **extra_fields):
        if not email:
            raise ValueError("Email field is required")
        email = self.normalize_email(email=email)
        user = self.model(email = email, **extra_fields)

        user.set_password(password)
        user.save(using = self._db)
        return user
    
    def create_superuser(self, email, password=None, **extra_fields):
            if not password:
                raise ValueError("The Password field is required for superusers")
            email = self.normalize_email(email)
            # Set default values for superuser fields
            extra_fields.setdefault("is_superuser", True)
            extra_fields.setdefault("is_staff", True)
            extra_fields.setdefault("is_active", True)

            # Check that fields are correctly set for superuser
            if extra_fields.get("is_superuser") is not True:
                raise ValueError("Superuser must have is_superuser=True.")
            if extra_fields.get("is_staff") is not True:
                raise ValueError("Superuser must have is_staff=True.")

            return self.create_user(email, password, **extra_fields)
    
            
    
class CustomUser(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True)
    secretId = models.UUIDField(default=uuid4)
    is_creater = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    age = models.IntegerField(default=18)
    name = models.CharField(max_length=100)
    history = models.ManyToManyField("videos.Video", related_name="watched_by")
    username = models.CharField(max_length=100, unique=True)
    profile_picture = models.ImageField(upload_to="profile_pictures", default="profile_pictures/default.jpg")

    objects = CustomUserManager()
    USERNAME_FIELD = "email"

    REQUIRED_FIELDS = []
    def save(self, *args, **kwargs):
        # Hash the password if it's not already hashed
        if self.pk is None or not self.password.startswith("pbkdf2_sha256$"):
            self.set_password(self.password)
        super().save(*args, **kwargs)
        
    def __str__(self):
        return self.email
    

class CreatorChannel(models.Model):
    picture = models.ImageField(default="channel_pics/default_creator.jpg")
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    name = models.CharField(max_length=20)
    description = models.CharField(max_length=100)
    fb_link = models.CharField(max_length=100)
    instagram_link = models.CharField(max_length=100)
    category = models.CharField(choices=CATEGORY_CHOICES, max_length=21)

    def __str__(self):
        return self.name


@receiver(post_save, sender = CustomUser)
def sendVerificationMail(sender, instance, created, **kwargs):
    if created:
        if instance.is_active == False:
            send_mail(subject="Email verification", from_email="ha.lowkey.05.ck@gmail.com", recipient_list=[instance.email], message=f"{settings.CLIENT_HOST}/verify/{instance.secretId}")

@receiver(post_save, sender = CreatorChannel)
def make_creator(sender, instance, created, **kwargs):
    instance.user.is_creater = True
    instance.user.save()