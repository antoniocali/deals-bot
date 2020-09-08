from __future__ import annotations
import yaml
from app.logger import getLogger
from typing import Callable, Optional, Tuple, List
from telethon import TelegramClient
from telethon.errors import BotInvalidError
from telethon.tl.types import InputPeerUser, InputPeerChannel
from telethon.tl.tlobject import TLObject
from app.models import AmazonDealsCategories, ShortenProvider, mappingsCategories

log = getLogger("CONFIG")

templated = set(
    [
        "api_id",
        "api_hash",
        "bot_token",
        "shorten_provider",
        "shorten_bitly_token",
        "shorten_shortest_token",
        "amazon_affiliate",
        "telegram_channel_id",
        "telegram_repost_after_days",
        "telegram_posts_per_day",
        "telegram_start_hour",
        "telegram_end_hour",
        "telegram_id",
        "telegram_type_id",
        "telegram_delay_message_minutes",
        "deals_min_discount",
        "deals_max_price",
        "deals_filter_categories",
        "deals_categories",
        "image_template_uri",
        "font_uri",
        "font_color",
        "font_color_border",
        "font_size",
    ]
)

providers: dict[str, Tuple[str, ShortenProvider]] = {
    "bitly": ("shorten_bitly_token", ShortenProvider.BITLY),
    "shortest": ("shorten_shortest_token", ShortenProvider.SHORTEST),
    "free": ("", ShortenProvider.FREE),
}


class Config:
    __instance__ = None

    def __init__(self):
        """ Constructor.
       """
        if Config.__instance__ is None:
            Config.__instance__ = self
            path = "./app/config/config.yaml"
            log.info(f"Reading configuration from: {path}")
            with open(path, "r", encoding="utf8") as stream:
                config = yaml.safe_load(stream)
                # API
                self.api_id = config["api_id"]
                self.api_hash = config["api_hash"]
                self.bot_token = config["bot_token"]
                # Shorten
                shorten_url = config["shorten_url"]

                shorten_provider = shorten_url["shorten_provider"]
                self.shorten_shortest_token = shorten_url["shortest_token"]
                self.shorten_bitly_token = shorten_url["bitly_token"]
                if shorten_provider not in providers.keys():
                    raise ValueError(
                        f"You chose an {shorten_provider} Provider, available chooses: {str(providers.keys())}"
                    )
                else:
                    if providers[shorten_provider][0] and not getattr(
                        self, providers[shorten_provider][0]
                    ):
                        raise ValueError(
                            f"You specified {shorten_provider} as provider, but you didn't provide the token for it."
                        )
                self.shorten_provider = providers[shorten_provider][1]

                # Amazon
                self.amazon_affiliate = config["amazon_affiliate"]
                # Deals
                deals = config["deals"]
                self.deals_min_discount: Optional[int] = deals.get("min_discount", None)
                self.deals_max_price: Optional[int] = deals.get("max_price", None)
                self.deals_filter_categories: Optional[bool] = deals[
                    "filter_categories"
                ] if deals["filter_categories"] else False
                categories = deals["categories"]
                self.deals_categories: List[AmazonDealsCategories] = list(
                    map(
                        lambda x: mappingsCategories[x],
                        map(lambda e: e[0], filter(lambda k: k[1], categories.items())),
                    )
                )

                # Telegram
                telegram = config["telegram"]
                self.telegram_channel_id = telegram["channel_id"]
                self.telegram_repost_after_days = telegram["repost_after_days"]
                self.telegram_posts_per_day = telegram["posts_per_day"]
                if self.telegram_posts_per_day <= 0:
                    raise ValueError("posts_per_day must be greater than 0")

                if (
                    telegram["start_hour_of_day"]
                    and not 0 <= telegram["start_hour_of_day"] <= 23
                ):
                    raise ValueError("start_hour_of_day must be between 0 and 23")

                self.telegram_start_hour: Optional[int] = (
                    telegram["start_hour_of_day"]
                    if telegram["start_hour_of_day"]
                    else None
                )
                if telegram["end_hour_of_day"]:
                    if not telegram["start_hour_of_day"]:
                        raise ValueError(
                            "you cannot set end_hour_of_day if start_hour_of_day is not specified"
                        )
                    if telegram["end_hour_of_day"] < telegram["start_hour_of_day"]:
                        raise ValueError(
                            "end_hour_of_day must be after start_hour_of_day"
                        )
                    if not 0 <= telegram["end_hour_of_day"] <= 23:
                        raise ValueError("end_hour_of_day must be between 0 and 23")

                    if telegram["delay_message_minutes"]:
                        raise ValueError(
                            "end_hour_of_day mutual exclusive with delay_message_minutes"
                        )

                self.telegram_end_hour: Optional[int] = (
                    telegram["end_hour_of_day"] if telegram["end_hour_of_day"] else None
                )

                self.telegram_delay_message_minutes = telegram["delay_message_minutes"]
                self.telegram_message_template = telegram["message_template"]

                if (
                    not self.telegram_end_hour
                    and not self.telegram_delay_message_minutes
                ):
                    raise ValueError(
                        "you must set end_hour_of_day or delay_message_minutes (Impossible to know how much wait between two posts)"
                    )
                # Image
                image = config["image_generator"]
                self.image_template_uri = image["image_template_uri"]
                if not self.image_template_uri:
                    raise ValueError("image_template_uri must be set")
                self.font_uri = image["font_uri"]
                if not self.font_uri:
                    raise ValueError("font_uri must be set")
                convertRgb: Callable[[str], int] = lambda x: int(x.strip())
                r, g, b = list(map(convertRgb, image["font_color"].split(",")))

                self.font_color: Tuple[int, int, int] = (r, g, b)
                self.font_size: int = image["font_size"]
                colorBorder = image["font_color_border"]
                if colorBorder:
                    r, g, b = list(map(convertRgb, colorBorder.split(",")))
                    self.font_color_border: Optional[Tuple[int, int, int]] = (r, g, b)
                else:
                    self.font_color_border = None

                bot = (
                    TelegramClient("config", self.api_id, self.api_hash)
                    .start(bot_token=self.bot_token)
                    .start()
                )
                with bot:
                    telegram_type: Tuple[int, TLObject] = bot.loop.run_until_complete(
                        self._get_channel_id(bot, self.telegram_channel_id)
                    )
                    self.telegram_id = telegram_type[0]
                    self.telegram_type_id = telegram_type[1]

        else:
            raise Exception("You cannot create another Config class")

    async def _get_channel_id(
        self, bot: TelegramClient, channel_id: str
    ) -> Tuple[int, TLObject]:
        log.info(f"Retrieving ID for {channel_id}")
        channel = await bot.get_input_entity(channel_id)
        if channel:
            if isinstance(channel, InputPeerUser):
                return (channel.user_id, channel)
            elif isinstance(channel, InputPeerChannel):
                return (channel.channel_id, channel)
            else:
                raise BotInvalidError(f"{channel_id} is not a valid channel")
        else:
            raise BotInvalidError(f"{channel_id} is not a valid channel")

    @staticmethod
    def get_instance() -> Config:
        """ Static method to fetch the current instance.
       """
        if not Config.__instance__:
            obj = Config()
            log.info("Configuration Found")
            log.info("{:<35}{:<40}".format("--KEY--", "--VALUE--"))
            for key in sorted(list(templated)):
                log.info(
                    "{:<35}{:<40}".format(
                        key, str(getattr(obj, key)) if getattr(obj, key) else ""
                    )
                )
            log.info("Configuration Finished")
            return obj
        return Config.__instance__


c = Config.get_instance()
