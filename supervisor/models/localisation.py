from django.db     import models

class Localisation(models.Model):
    gouvernorat_libelle = models.CharField(max_length=255, blank=True, null=True)
    delegation_libelle  = models.CharField(max_length=255, blank=True, null=True)
    localite_libelle    = models.CharField(max_length=255)

    class Meta:
        #* Enforce uniqueness based on combination of fields
        unique_together = ['gouvernorat_libelle', 'delegation_libelle', 'localite_libelle']

    def __str__(self):
        return f"{self.localite_libelle} ({self.delegation_libelle}, {self.gouvernorat_libelle})"
    def __str__(self):
        return f"{self.localite_libelle} ({self.delegation_libelle}, {self.gouvernorat_libelle})"
