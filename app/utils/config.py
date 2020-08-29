import yaml
from app.logger import getLogger

log = getLogger("CONFIG")

templated = set(
    [
        "api_id",
        "api_hash",
        "bot_token",
        "short_use_ads",
        "shortest_token",
        "amazon_affiliate",
        "telegram_channel_id",
        "telegram_respost_after_days",
        "telegram_posts_per_day",
        "telegram_start_hour",
        "telegram_end_hour",
        "telegram_delay_message_minutes",
    ]
)


class Config:
    __instance__ = None

    def __init__(self):
        """ Constructor.
       """
        if Config.__instance__ is None:
            Config.__instance__ = self
            path = "./app/config/config.yaml"
            log.info(f"Reading configuration from: {path}")
            with open(path, "r") as stream:
                config = yaml.safe_load(stream)
                # API
                self.api_id = config["api_id"]
                self.api_hash = config["api_hash"]
                self.bot_token = config["bot_token"]
                # Shorten
                shorten_url = config["shorten_url"]
                self.short_use_ads = shorten_url.get("use_ads", False)
                if self.short_use_ads and not shorten_url.get("shortest_token"):
                    raise ValueError(
                        "Shortest Token must be set if use_ads is set to True"
                    )
                self.shortest_token = shorten_url["shortest_token"]
                # Amazon
                self.amazon_affiliate = config["amazon_affiliate"]
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

                self.telegram_start_hour = (
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

                self.telegram_end_hour = (
                    telegram["end_hour_of_day"] if telegram["end_hour_of_day"] else None
                )

                self.telegram_delay_message_minutes = telegram["delay_message_minutes"]

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

        else:
            raise Exception("You cannot create another Config class")

    @staticmethod
    def get_instance():
        """ Static method to fetch the current instance.
       """
        if not Config.__instance__:
            obj = Config()
            log.info("Configuration Finished")
            for key in sorted(list(set(dir(obj)).intersection(templated))):
                log.info(
                    "{:<35}{:<40}".format(
                        key, getattr(obj, key) if getattr(obj, key) else ""
                    )
                )
        return Config.__instance__
