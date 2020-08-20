from PIL import Image, ImageDraw
import urllib.request
import aggdraw
import os

width = 550
height = 350
url = "http://www.antoniocali.com/blog/wp-content/uploads/2016/12/logo.png"
right = 180
up = 80

# urllib.request.ssl.
def create_image(price, imageUrl, name):
    with Image.new("RGBA", (width, height), (255, 255, 255, 255)) as im:
        current_dir = os.path.dirname(os.path.abspath(__file__))
        print(current_dir)
        d = aggdraw.Draw(im)
        p = aggdraw.Pen((180, 20, 200), 80)
        # get a font
        text1 = aggdraw.Font((0, 0, 0), "slotdown.otf", 40)
        # /Users/andav1/Documents/Python/deals-bot/BillionDreams_PERSONAL.ttf

        text2 = aggdraw.Font((180, 20, 200), "slotdown.otf", 42)
        print(price)
        # get image from web
        imageFromWeb = Image.open(urllib.request.urlopen(imageUrl))
        background = Image.new("RGBA", imageFromWeb.size, (255, 255, 255, 0))
        background.paste(imageFromWeb)
        # resize
        basewidth = 150
        baseheight = 200
        landscape = True if imageFromWeb.size[0] >= imageFromWeb.size[1] else False
        if landscape:
            wpercent = basewidth / float(imageFromWeb.size[0])
            hsize = int((float(imageFromWeb.size[1]) * float(wpercent)))
            img = background.resize((basewidth, hsize), Image.ANTIALIAS)
        else:
            wpercent = baseheight / float(imageFromWeb.size[1])
            wsize = int((float(imageFromWeb.size[0]) * float(wpercent)))
            img = background.resize((baseheight, wsize), Image.ANTIALIAS)
        finalHeightSize = img.size[1]
        finalWidthSize = img.size[0]
        # write text
        d.text((50, height / 2 + 10), price, text2)
        d.text((50, height / 2 + 10), price, text1)
        # draw arc in the upper part
        d.pieslice((0, -height / 5, width, height / 5), 180, 0, p)
        d.flush()
        # write to stdout
        im.paste(
            img,
            (
                int(width / 2 + finalWidthSize / 4),
                int(height / 2 - finalHeightSize / 4),
            ),
        )
        im.save(f"{name}.png", "PNG")
