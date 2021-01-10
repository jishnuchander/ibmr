from django.db import models


class Profile(models.Model):
	username = models.CharField(max_length = 50)
	user_id   = models.CharField(max_length = 50)
	image_uri = models.CharField(max_length = 50)
	playlist  = models.CharField(max_length = 50)

	def __str__(self):
		return self.username

