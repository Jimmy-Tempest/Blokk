# Modules import
import rsa

# Django import
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.signing import Signer
# Create your models here.


def pfp_path(instance, filename):
    return f'pfp/{instance.username}/{filename}'

class User(AbstractUser):
    publickey = models.TextField(max_length=5000, blank=True, null=True)
    privatekey = models.TextField(max_length=5000, blank=True, null=True)

    pfp = models.ImageField(upload_to=pfp_path, blank=True, null=True)


    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email', 'password']


    def __str__(self):
        return self.username

    def generateKey(self):
        (pubkey, privkey) = rsa.newkeys(2048)
        self.publickey = pubkey.save_pkcs1()
        self.privatekey = privkey.save_pkcs1()
        self.save()
        return (pubkey, privkey)
    
    def create_user(self, username, email, password):
        self.username = username
        self.email = email
        self.set_password(password)
        self.generateKey()
        self.save()
        return self
    
    def create_superuser(self, username, email, password):
        self.username = username
        self.email = email
        self.set_password(password)
        self.is_superuser = True
        self.is_staff = True
        self.generateKey()
        self.save()
        return self
    
    def get_publickey(self):
        return self.publickey
    
    def get_privatekey(self):
        return self.privatekey


class Currency(models.Model):
    name = models.CharField(max_length=100)
    symbol = models.CharField(max_length=10)
    invite_code = models.CharField(max_length=100, blank=True, null=True)
    users = models.ManyToManyField(User, blank=True, related_name='currencies')
    admin = models.ForeignKey(User, on_delete=models.CASCADE, related_name='admin')
    market_cap = models.IntegerField(default=-1)
    # ledger = models.ForeignKey('Ledger', on_delete=models.CASCADE, related_name='currencies', blank=True, null=True)


    def __str__(self):
        return self.name

    def generateInvite(self):
        signer = Signer()
        self.invite_code = signer.sign(f"{self.id}-{self.name}-{self.symbol}")
        self.save()
        return self.invite_code
    
    def create(self, name, symbol, admin):
        self.name = name
        self.symbol = symbol
        self.admin = admin
        self.save()
        self.generateInvite()
        return self