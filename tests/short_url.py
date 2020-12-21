from app.config.config import Config
from app.utils import Utils
from app.models import DealsModel

deal_1 = DealsModel(
    description="text_4",
    id="B008BSRE0W",
    imageUrl="https://images-na.ssl-images-amazon.com/images/I/61ejJSt6RlL._AC_UX625_.jpg",
    originalPrice=53.99,
    dealPrice=27.99,
    percentOff=49,
    slug="hello",
)

print(Utils.affiliateAmazon(deal_1))