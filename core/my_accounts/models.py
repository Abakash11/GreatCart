from django.db import models
from django.contrib.auth.models import AbstractBaseUser,BaseUserManager

# Create your models here.

class Myaccount_manager(BaseUserManager):
    def create_user(self,first_name,last_name,username,email,password=None):
        if not email:
            raise ValueError('User must have Username and Email')
        user=self.model(
            email=self.normalize_email(email),
            username=username,
            first_name=first_name,
            last_name=last_name
        )
        user.set_password(password)
        user.save(using=self._db)
        return user
    
    def create_superuser(self,first_name,last_name,username,email,password=None,):
        user=self.create_user(
            email=self.normalize_email(email),
            username=username,
            password=password,
            first_name=first_name,
            last_name=last_name,
            
        )
        user.is_admin=True
        user.is_active=True
        user.is_staff=True
        user.is_superadmin=True
        user.save(using=self._db)
        return user
    def get_by_natural_key(self, email):
        return self.get(email=email)  # Look up user by email


class Accounts(AbstractBaseUser):
    first_name=models.CharField(max_length=20)
    last_name=models.CharField(max_length=30)
    username=models.CharField(max_length=50,unique=True)
    email=models.EmailField(max_length=100,unique=True)
    phone_number=models.CharField( max_length=50)

    # required 
    date_joined=models.DateTimeField(auto_now_add=True)
    last_joined=models.DateTimeField(auto_now_add=True)
    is_admin=models.BooleanField(default=False)
    is_staff=models.BooleanField(default=False)
    is_active=models.BooleanField(default=False)
    is_superadmin=models.BooleanField(default=False)

    USERNAME_FIELD='email'
    REQUIRED_FIELDS=['username','first_name','last_name']

    objects=Myaccount_manager()
    def name(self):
        return f"{self.first_name} {self.last_name}"
    def __str__(self):
        return self.email
    def has_perm(self,perm,obj=None):
        return self.is_admin
    def has_module_perms(self,add_label):
        return True
    @property
    def is_authenticated(self):
        return True
    @property
    def is_anonymous(self):
        return False  # Custom users are never anonymous
    
class UserProfile(models.Model):
    user=models.OneToOneField(Accounts,on_delete=models.CASCADE)
    profile_picture=models.ImageField(upload_to='profile_pictures',default='default_profile.jpg')
    cover_picture=models.ImageField(upload_to='cover_pictures',default='default_cover.jpg')
    bio=models.TextField(max_length=500,blank=True)
    location=models.CharField(max_length=100,blank=True)
    website=models.URLField(blank=True)
    
    def __str__(self):
        return self.user.email