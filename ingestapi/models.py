from djongo import models


# Create your models here.
class Users(models.Model):
	#id = models.IntegerField(primary_key=True)
	username = models.CharField(max_length=10)
	trialID = models.TextField()
	role = models.CharField(max_length=10)
	comments = models.CharField(max_length=10)
	multi = models.CharField(max_length=10)
	pdf_history = models.TextField()
	total_edc = models.TextField()
	edc_time = models.TextField()

	def __str__(self):
		return str(self.id)