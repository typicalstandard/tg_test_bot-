from django.db import models

class Client(models.Model):
    telegram_id = models.BigIntegerField(unique=True)
    name = models.CharField(max_length=255)
    is_active = models.BooleanField(default=True)
    address = models.TextField(null=True, blank=True)
    phone = models.CharField(max_length=15, null=True, blank=True)
    email = models.EmailField(null=True, blank=True)

    def __str__(self):
        return f"{self.name} (ID: {self.telegram_id})"

class Broadcast(models.Model):
    subject = models.CharField(max_length=255)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    sent = models.BooleanField(default=False)

    def __str__(self):
        return self.subject


class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.name

class SubCategory(models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name="subcategories")
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.category.name} -> {self.name}"

class Product(models.Model):
    subcategory = models.ForeignKey(SubCategory, on_delete=models.CASCADE, related_name="products")
    name = models.CharField(max_length=100)
    description = models.TextField()
    photo = models.ImageField(upload_to="product_images/")
    price = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class Cart(models.Model):
    client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name="cart_items")
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="in_carts")
    quantity = models.IntegerField()

    def __str__(self):
        return f"Client: {self.client}, Product: {self.product}, Quantity: {self.quantity}"



class FAQ(models.Model):
    question = models.TextField(verbose_name="Вопрос")
    answer = models.TextField(blank=True, null=True, verbose_name="Ответ")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.question


class UserQuestion(models.Model):
    telegram_id = models.BigIntegerField(verbose_name="ID пользователя")
    question = models.TextField(verbose_name="Вопрос")
    asked_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.question
