from django.db import models


# Create your models here.
class Todo(models.Model):
    status_options = [
        ('Pending', 'Pending'),
        ('Done', 'Done'),
    ]

    category_options = [
        ('None', 'None'),
        ('Work', 'Work'),
        ('Personal', 'Personal'),
        ('Family affair', 'Family affair'),
        ('Study', 'Study'),
    ]

    task = models.CharField(max_length=225)
    details = models.TextField()
    category = models.CharField(max_length=15, choices=category_options, default='None')
    status = models.CharField(max_length=10, choices=status_options, default='Pending')
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)

    # Sort post data in descending order
    class Meta:
        ordering = ['-created_on']

    def __str__(self):
        return f'{self.task} : {self.category}'
