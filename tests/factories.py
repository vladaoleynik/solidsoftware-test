import factory

from app.extensions import db
from app.models import Cart, CartItem, Payment, Product, User, UserPaymentMethod
from app.models.enums import CartStatus, PaymentStatus


class BaseFactory(factory.alchemy.SQLAlchemyModelFactory):
    class Meta:
        abstract = True
        sqlalchemy_session = db.session
        sqlalchemy_session_persistence = "flush"


class UserFactory(BaseFactory):
    class Meta:
        model = User

    email = factory.Sequence(lambda n: f"user{n}@example.com")
    name = factory.Faker("name")


class CartFactory(BaseFactory):
    class Meta:
        model = Cart

    user = factory.SubFactory(UserFactory)
    status = CartStatus.ACTIVE


class UserPaymentMethodFactory(BaseFactory):
    class Meta:
        model = UserPaymentMethod

    user = factory.SubFactory(UserFactory)
    provider_token = "pm_mock_success"
    last_four = "1234"
    is_default = False


class ProductFactory(BaseFactory):
    class Meta:
        model = Product

    name = factory.Faker("word")
    price = factory.Faker("pydecimal", left_digits=2, right_digits=2, positive=True)
    stock_quantity = 100


class CartItemFactory(BaseFactory):
    class Meta:
        model = CartItem

    cart = factory.SubFactory(CartFactory)
    product = factory.SubFactory(ProductFactory)
    quantity = 1
    unit_price = factory.SelfAttribute("product.price")


class PaymentFactory(BaseFactory):
    class Meta:
        model = Payment

    user = factory.SubFactory(UserFactory)
    cart = factory.SubFactory(CartFactory)
    payment_method = factory.SubFactory(UserPaymentMethodFactory)
    amount = factory.Faker("pydecimal", left_digits=3, right_digits=2, positive=True)
    currency = "USD"
    status = PaymentStatus.PENDING
