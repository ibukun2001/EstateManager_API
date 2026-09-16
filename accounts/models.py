from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.utils.text import slugify


class UserManager(BaseUserManager):
    def create_user(self,email,password=None,**extra_fields):
        if not email:
            raise ValueError("Email is required")

        email=self.normalize_email(email)

        user=self.model(
            email=email,
            username=email,   # keep username populated internally
            **extra_fields
        )

        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self,email,password=None,**extra_fields):
        extra_fields.setdefault("is_staff",True)
        extra_fields.setdefault("is_superuser",True)
        extra_fields.setdefault("is_active",True)

        return self.create_user(email,password,**extra_fields)


class Company(models.Model):
    name=models.CharField(max_length=255)
    slug=models.SlugField(max_length=255,unique=True,blank=True)
    email=models.EmailField(unique=True)
    phone=models.CharField(max_length=20,blank=True)
    address=models.TextField(blank=True)
    website=models.URLField(blank=True)
    created_at=models.DateTimeField(auto_now_add=True)

    def save(self,*args,**kwargs):
        if not self.slug:
            base_slug=slugify(self.name)[:240] or "company"
            slug=base_slug
            counter=2
            while Company.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                slug=f"{base_slug}-{counter}"
                counter+=1
            self.slug=slug
        super().save(*args,**kwargs)

    def __str__(self):
        return self.name


class User(AbstractUser):
    username=models.CharField(max_length=150,blank=True)

    email=models.EmailField(unique=True)

    USERNAME_FIELD="email"
    REQUIRED_FIELDS=[]

    USER_ROLES=(
        ("buyer","Buyer"),
        ("company","Company"),
        ("staff","Staff"),
    )

    company=models.ForeignKey(
        Company,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="users"
    )

    role=models.CharField(
        max_length=20,
        choices=USER_ROLES,
        default="buyer"
    )

    phone=models.CharField(
        max_length=20,
        blank=True
    )

    # For buyers only: which company's site they arrived from, and
    # optionally the specific page to send them back to. Persists on
    # the account so the "back to website" link survives future logins.
    referred_by_company=models.ForeignKey(
        Company,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="referred_buyers"
    )
    referred_by_url=models.URLField(blank=True)

    created_at=models.DateTimeField(auto_now_add=True)

    objects=UserManager()

    def __str__(self):
        return self.email