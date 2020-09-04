from genericpath import exists
from app.config.config import Config
from PIL import Image, ImageDraw, ImageFont
import urllib.request
from os import path, makedirs, remove

right = 180
up = 80

config = Config.get_instance()
tmpPath = "./app/generators/tmp"
if not path.exists(path.abspath(tmpPath)):
    makedirs(path.abspath(path.dirname(tmpPath)))


def create_image(
    originalPrice: float,
    dealPrice: float,
    imageUrl: str,
    save_as: str,
    currency: str = "€",
    to_test: bool = False,
) -> str:
    with Image.open(config.image_template_uri) as im:
        tmpPathUri = path.abspath(tmpPath)
        height = im.size[1]
        width = im.size[0]
        # Text for DealPrice
        txtDeal = Image.new("RGBA", im.size, (255, 255, 255, 0))
        d = ImageDraw.Draw(txtDeal)

        # Check if I have to put border
        if config.font_color_border:
            dealPriceBorderFont = ImageFont.truetype(
                config.font_uri, config.font_size + 2
            )
            d.text(
                (width * 0.2, height / 2 + 10),
                ("%.2f" % dealPrice) + currency,
                font=dealPriceBorderFont,
                fill=(0, 0, 0, 255),
            )

        dealPriceFont = ImageFont.truetype(config.font_uri, config.font_size)
        d.text(
            (width * 0.2, height / 2 + 8),
            ("%.2f" % dealPrice) + currency,
            font=dealPriceFont,
            fill=config.font_color,
        )

        # Text for OriginalPrice
        txtOriginal = Image.new("RGBA", im.size, (255, 255, 255, 0))
        dOriginal = ImageDraw.Draw(txtOriginal)
        # write text

        originalPriceFont = ImageFont.truetype(config.font_uri, int(config.font_size / 2))
        dOriginal.text(
            (width * 0.2, height / 2 - 20),
            ("%.2f" % originalPrice) + currency,
            font=originalPriceFont,
            fill=config.font_color,
        )
        dOriginal.line(
            (width * 0.2 - 5, height / 2 - 5, width * 0.2 + 75, height / 2 - 5),
            fill="black",
            width=4,
        )
        # Get Image From Web
        imageFromWeb = Image.open(urllib.request.urlopen(imageUrl))
        background = Image.new("RGBA", imageFromWeb.size, (255, 255, 255, 0))
        background.paste(imageFromWeb)
        # Resize Image From Web
        basewidth = 180
        baseheight = 220
        landscape = True if imageFromWeb.size[0] >= imageFromWeb.size[1] else False
        if landscape:
            wpercent = basewidth / float(imageFromWeb.size[0])
            hsize = int((float(imageFromWeb.size[1]) * float(wpercent)))
            img = background.resize((basewidth, hsize), Image.ANTIALIAS)
        else:
            wpercent = baseheight / float(imageFromWeb.size[1])
            wsize = int((float(imageFromWeb.size[0]) * float(wpercent)))
            img = background.resize((wsize, baseheight), Image.ANTIALIAS)
        finalHeightSize = img.size[1]
        finalWidthSize = img.size[0]

        out = Image.alpha_composite(im, txtDeal)
        out = Image.alpha_composite(out, txtOriginal)
        out.paste(
            img,
            (
                int(width / 2 + finalWidthSize / 4),
                int(height / 2 - finalHeightSize / 4),
            ),
        )
        if to_test:
            out.show()
            return ""
        else:
            out.save(f"{tmpPathUri}/{save_as}.png", "PNG")
    return f"{tmpPathUri}/{save_as}.png"


def delete_tmp_image(path: str):
    if exists(path):
        remove(path)
