from django.db import models

class Event(models.Model):
    CATEGORY_CHOICES = [
        ('Music','Music'),
        ('Sports','Sports'),
        ('Comedy','Comedy'),
        ('Tech','Tech')
    ]

    title = models.CharField(max_length=200)
    image = models.CharField(max_length=200)  # just store image file name
    date = models.DateField()
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES)
    location = models.CharField(max_length=200)
    price = models.IntegerField()
    description = models.TextField()

    def __str__(self):
        return self.title
    

    