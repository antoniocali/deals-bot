from app.config.config import Config
from app.utils import Utils

c = Config.get_instance()
print(Utils.shortUrl("https://www.google.it", c.shorten_provider))
