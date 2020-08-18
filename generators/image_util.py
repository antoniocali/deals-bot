from PIL import Image, ImageDraw
import urllib.request
# import aggdraw
import os

width = 350
height = 200
url = "http://www.antoniocali.com/blog/wp-content/uploads/2016/12/logo.png"
right = 180
up = 80


def create_image(text, imageUrl, name):
    with Image.new("RGBA", (width, height), (255, 255, 255, 255)) as im:
        current_dir = "C:\\Users\\anton\\Documents\\Developing\\python\deals-bot\\generators\\"
        print(current_dir)
        d = ImageDraw.Draw(im)
        # d = aggdraw.Draw(im)
        # p = aggdraw.Pen((180, 20, 200), 40)
        # # get a font
        # text1 = aggdraw.Font((0, 0, 0), f"{current_dir}billiondream.ttf", 40)
        # text2 = aggdraw.Font((180, 20, 200), f"{current_dir}billiondream.ttf", 42)

        # get image from web
        imageFromWeb = Image.open(urllib.request.urlopen(imageUrl))
        background = Image.new("RGBA", imageFromWeb.size, (255, 255, 255, 0))
        background.paste(imageFromWeb)
        # resize
        basewidth = 100
        wpercent = basewidth / float(imageFromWeb.size[0])
        hsize = int((float(imageFromWeb.size[1]) * float(wpercent)))
        img = background.resize((basewidth, hsize), Image.ANTIALIAS)
        # write text
        d.text((10, height / 2), text, fill="black")
        # d.text((10, height / 2), text, text1)
        # draw arc in the upper part
        d.pieslice((0, -height / 5, width, height / 5), 180, 0, fill="black")
        # d.flush()
        # write to stdout
        im.paste(img, (right, up))
        im.save(f"{name}.png", "PNG")
