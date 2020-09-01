from app.models import DealsModel
from app.utils import Utils
from typing import List

text_1 = "Fitbit Versa con Rilevazione del Battito Cardiaco, oltre 4 Giorni di Autonomia della Batteria, Resistente All'acqua, Nero"
text_2 = "Fitbit Versa Edizione Speciale con Rilevazione del Battito Cardiaco, oltre 4 Giorni di Autonomia della Batteria, Resistente All'acqua, Lavanda"
text_3 = "Fitbit Versa Edizione Speciale con Rilevazione del Battito Cardiaco, oltre 4 Giorni di Autonomia della Batteria, Resistente All'acqua, Grigio"
text_4 = "Superga 2750-Plus Cotu, Scarpe da Ginnastica Unisex – Adulto, Bianco White 901, 37 EU"
text_5 = "Superga 2750-Plus Cotu, Scarpe da Ginnastica Unisex – Adulto, Bianco (White 901), 39 EU"
test_list = [text_1, text_2, text_3, text_4, text_5]
# for x, y in itertools.product(test_list, test_list):
#     print(x)
#     print(y)
#     print(Utils.cosine_distance(x, y))
# description: str
# impressionAsin: str
# imageUrl: str
# originalPrice: float
# dealPrice: float
# percentOff: int
# slug: str
# reviewRating: float = -1
deal_1 = DealsModel(
    description=text_4,
    impressionAsin="B008BSRE0W",
    imageUrl="https://images-na.ssl-images-amazon.com/images/I/61ejJSt6RlL._AC_UX625_.jpg",
    originalPrice=53.99,
    dealPrice=27.99,
    percentOff=49,
    slug="hello",
)

deal_2 = DealsModel(
    description=text_5,
    impressionAsin="B008BSREIE",
    imageUrl="https://images-na.ssl-images-amazon.com/images/I/61ejJSt6RlL._AC_UX625_.jpg",
    originalPrice=53.99,
    dealPrice=27.99,
    percentOff=49,
    slug="hello",
)
deal_3 = DealsModel(
    description=text_1,
    impressionAsin="B008BSREIE",
    imageUrl="https://images-na.ssl-images-amazon.com/images/I/61ejJSt6RlL._AC_UX625_.jpg",
    originalPrice=53.99,
    dealPrice=27.99,
    percentOff=49,
    slug="hello",
)
deal_4 = DealsModel(
    description=text_2,
    impressionAsin="B008BSREIE",
    imageUrl="https://images-na.ssl-images-amazon.com/images/I/61ejJSt6RlL._AC_UX625_.jpg",
    originalPrice=53.99,
    dealPrice=27.99,
    percentOff=49,
    slug="hello",
)
deal_5 = DealsModel(
    description=text_3,
    impressionAsin="B008BSREIE",
    imageUrl="https://images-na.ssl-images-amazon.com/images/I/61ejJSt6RlL._AC_UX625_.jpg",
    originalPrice=53.99,
    dealPrice=27.99,
    percentOff=49,
    slug="hello",
)
test_model = [deal_1, deal_2, deal_4, deal_3, deal_5]


def _remove_similar_products(deals: List[DealsModel]) -> List[DealsModel]:
    tmpList: List[DealsModel] = list()
    for deal in deals:
        if not any(
            map(
                lambda x: False
                if x == deal
                else Utils.cosine_distance(x.description, deal.description) > 0.85,
                tmpList,
            )
        ):
            tmpList.append(deal)

    return tmpList


for elem in _remove_similar_products(test_model):
    print(elem)
