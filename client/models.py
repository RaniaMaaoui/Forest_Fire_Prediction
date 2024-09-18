from django.contrib.auth.models     import User, BaseUserManager
from django.db                      import models
from django.contrib.auth.hashers    import make_password, check_password
from django.core.exceptions         import ValidationError
from django.core.mail               import send_mail
from django.template.loader         import render_to_string
from django.utils.html              import strip_tags

class Client(models.Model):
    firstName   = models.CharField(max_length=25, blank=True)
    lastName    = models.CharField(max_length=25, blank=True)
    email       = models.EmailField(max_length=255, unique=True)
    phone       = models.IntegerField(blank=True)
    username    = models.CharField(max_length=30)
    password    = models.CharField(max_length=128)
    image       = models.ImageField(null=True, blank=True, upload_to='img')
    user        = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        return f'{self.firstName} {self.lastName}'

    def save(self, *args, **kwargs):
        is_new = self.pk is None

        if is_new:
            if User.objects.filter(username=self.username).exists():
                raise ValidationError(f"Username {self.username} already exists.")

            #! Générer un mot de passe sécurisé pour l'envoi
            password = BaseUserManager().make_random_password()
            hashed_password = make_password(password)
            self.password = hashed_password

            self.user = User.objects.create_user(username=self.username, email=self.email, password=password)
        else:
            if self.user:
                self.user.username = self.username
                self.user.email = self.email
                if not check_password(self.password, self.user.password):
                    self.user.set_password(self.password)
                self.user.save()

        super().save(*args, **kwargs)

        if is_new:
            context = {
                'client': self,
                'password': password,
                'image_url': 'https://smartforgreen.com/wp-content/uploads/2023/07/featured_page.png'
                }
            subject = 'Welcome to Smart For Green'
            html_message = render_to_string('message.html', context)
            plain_message = strip_tags(html_message)
            from_email = 'From <mohamedhedigharbi101@gmail.com>'
            to = self.email

            send_mail(subject, plain_message, from_email, [to], html_message=html_message)

    def delete(self, *args, **kwargs):
        if self.user:
            self.user.delete()
        super().delete(*args, **kwargs)

    def clean(self):
        if not self.firstName and not self.lastName:
            raise ValidationError("Either first name or last name must be provided.")
        if Client.objects.exclude(pk=self.pk).filter(email=self.email).exists():
            raise ValidationError("This email is already in use.")
