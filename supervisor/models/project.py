from django.contrib.gis.db          import models
from django.utils                   import timezone
from location_field.models.plain    import PlainLocationField
from client.models                  import Client

class Project(models.Model):
    name            = models.CharField(max_length=30)
    geomp           = models.MultiPolygonField(null=True)
    descp           = models.TextField(null=True)
    date_debut      = models.DateTimeField(default=timezone.now)
    date_fin        = models.DateTimeField()
    city            = models.CharField(max_length=255)
    piece_joindre   = models.FileField(upload_to='uploads/%Y/%m/%d/', null=True, blank=True)
    location        = PlainLocationField(based_fields=['city'], zoom=7,null=True)
    client          = models.ForeignKey(Client, on_delete=models.CASCADE, null=True)
    polygon_id      = models.BigAutoField(primary_key=True, default=None)


    def __str__(self):
        return f'Project: {self.name}'
    