from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

class Product(models.Model):
    name = models.CharField(max_length=255,)
    description = models.TextField(null=True, blank=True)
    barcode = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name

class PantryPosition(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    best_before = models.DateField()

    class Meta:
        unique_together = [['user', 'product', 'best_before']]
        verbose_name_plural = "Pantry positions"
        ordering = ['best_before']

    def __str__(self):
        return f"{self.product.name} ({self.quantity})"