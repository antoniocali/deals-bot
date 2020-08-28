import yaml


class Config:
    __instance__ = None

    def __init__(self):
        """ Constructor.
       """
        if Config.__instance__ is None:
            Config.__instance__ = self
            with open("./app/config/config.yaml", "r") as stream:
                config = yaml.safe_load(stream)
                self.api_id = config["api_id"]
                self.api_hash = config["api_hash"]
                self.bot_token = config["bot_token"]
                shorten_url = config["shorten_url"]
                self.short_use_ads = shorten_url.get("use_ads", False)
                if self.short_use_ads and not shorten_url.get("shortest_token"):
                    raise ValueError(
                        "Shortest Token must be set if use_ads is set to True"
                    )
                self.shortest_token = shorten_url["shortest_token"]
                self.amazon_affiliate = config["amazon_affiliate"]
                telegram = config["telegram"]
                self.telegram_channel_id = telegram["channel_id"]
                self.telegram_repost_after_days = telegram["repost_after_days"]
        else:
            raise Exception("You cannot create another SingletonGovt class")

    @staticmethod
    def get_instance():
        """ Static method to fetch the current instance.
       """
        if not Config.__instance__:
            Config()
        return Config.__instance__

