import factory

from app.extensions import db
from app.models import Cart, Payment, User, UserPaymentMethod
from app.services.payment_service import CartStatus, PaymentStatus


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


class PaymentFactory(BaseFactory):
    class Meta:
        model = Payment

    user = factory.SubFactory(UserFactory)
    cart = factory.SubFactory(CartFactory)
    payment_method = factory.SubFactory(UserPaymentMethodFactory)
    amount = factory.Faker("pydecimal", left_digits=3, right_digits=2, positive=True)
    currency = "USD"
    status = PaymentStatus.PENDING
