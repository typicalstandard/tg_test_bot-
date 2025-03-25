from django.test import TestCase
from django.core.files.uploadedfile import SimpleUploadedFile
from .models import Client, Broadcast, Category, SubCategory, Product, Cart, FAQ, UserQuestion


class ClientModelTests(TestCase):
    def setUp(self):
        self.client_obj = Client.objects.create(
            telegram_id=123456789,
            name="Test Client",
            is_active=True,
            address="Test Address",
            phone="1234567890",
            email="test@example.com"
        )

    def test_client_str(self):
        expected = "Test Client (ID: 123456789)"
        self.assertEqual(str(self.client_obj), expected)


class BroadcastModelTests(TestCase):
    def setUp(self):
        self.broadcast = Broadcast.objects.create(
            subject="Test Broadcast",
            message="This is a test message.",
            sent=False
        )

    def test_broadcast_str(self):
        self.assertEqual(str(self.broadcast), "Test Broadcast")


class CategoryModelTests(TestCase):
    def setUp(self):
        self.category = Category.objects.create(
            name="Test Category",
            description="Category description"
        )

    def test_category_str(self):
        self.assertEqual(str(self.category), "Test Category")


class SubCategoryModelTests(TestCase):
    def setUp(self):
        self.category = Category.objects.create(
            name="Test Category"
        )
        self.subcategory = SubCategory.objects.create(
            category=self.category,
            name="Test SubCategory",
            description="SubCategory description"
        )

    def test_subcategory_str(self):
        expected = f"{self.category.name} -> {self.subcategory.name}"
        self.assertEqual(str(self.subcategory), expected)


class ProductModelTests(TestCase):
    def setUp(self):
        self.category = Category.objects.create(name="Test Category")
        self.subcategory = SubCategory.objects.create(
            category=self.category,
            name="Test Sub",
            description="Subcategory description"
        )
        # Создаем тестовую картинку с помощью SimpleUploadedFile
        self.image = SimpleUploadedFile(
            name='test_image.jpg',
            content=b'\x47\x49\x46\x00\x00\x00',
            content_type='image/jpeg'
        )
        self.product = Product.objects.create(
            subcategory=self.subcategory,
            name="Test Product",
            description="Product description",
            photo=self.image,
            price="9.99"
        )

    def test_product_str(self):
        self.assertEqual(str(self.product), "Test Product")


class CartModelTests(TestCase):
    def setUp(self):
        self.client_obj = Client.objects.create(
            telegram_id=123456789,
            name="Test Client",
            is_active=True
        )
        self.category = Category.objects.create(name="Test Category")
        self.subcategory = SubCategory.objects.create(
            category=self.category,
            name="Test Sub",
            description="Subcategory description"
        )
        self.image = SimpleUploadedFile(
            name='test_image.jpg',
            content=b'\x47\x49\x46\x00\x00\x00',
            content_type='image/jpeg'
        )
        self.product = Product.objects.create(
            subcategory=self.subcategory,
            name="Test Product",
            description="Product description",
            photo=self.image,
            price="9.99"
        )
        self.cart = Cart.objects.create(
            client=self.client_obj,
            product=self.product,
            quantity=3
        )

    def test_cart_str(self):
        expected = f"Client: {self.client_obj}, Product: {self.product}, Quantity: {self.cart.quantity}"
        self.assertEqual(str(self.cart), expected)


class FAQModelTests(TestCase):
    def setUp(self):
        self.faq = FAQ.objects.create(
            question="What is Django?",
            answer="Django is a high-level Python web framework."
        )

    def test_faq_str(self):
        self.assertEqual(str(self.faq), "What is Django?")


class UserQuestionModelTests(TestCase):
    def setUp(self):
        self.user_question = UserQuestion.objects.create(
            telegram_id=987654321,
            question="How does testing work?"
        )

    def test_user_question_str(self):
        self.assertEqual(str(self.user_question), "How does testing work?")
