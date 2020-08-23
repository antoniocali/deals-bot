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
                self.shortest_token = config["shortest_token"]
                self.amazon_affiliate = config["amazon_affiliate"]
                self.short_url_ads = config["short_url_ads"]
        else:
            raise Exception("You cannot create another SingletonGovt class")

    @staticmethod
    def get_instance():
        """ Static method to fetch the current instance.
       """
        if not Config.__instance__:
            Config()
        return Config.__instance__

