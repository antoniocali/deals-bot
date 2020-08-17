from PIL import Image
import urllib.request
import aggdraw

width = 350
height = 200
url = "http://www.antoniocali.com/blog/wp-content/uploads/2016/12/logo.png"
right = 180
up = 80
with Image.new("RGBA", (width, height), (255, 255, 255, 255)) as im:

    d = aggdraw.Draw(im)
    p = aggdraw.Pen((180, 20, 200), 40)
    # get a font
    text1 = aggdraw.Font((0, 0, 0), "billiondream.ttf", 40)
    text2 = aggdraw.Font((180, 20, 200), "billiondream.ttf", 42)

    # get image from web
    imageFromWeb = Image.open(urllib.request.urlopen(url))
    background = Image.new("RGB", imageFromWeb.size, (255, 255, 255,0))
    background.paste(imageFromWeb, mask=imageFromWeb.split()[3]) 
    # resize
    basewidth = 100
    wpercent = (basewidth/float(imageFromWeb.size[0]))
    hsize = int((float(imageFromWeb.size[1])*float(wpercent)))
    img = background.resize((basewidth,hsize), Image.ANTIALIAS)

    # write text
    d.text((10, height / 2), "Top", text2)
    d.text((10, height / 2), "Top", text1)
    # draw arc in the upper part
    d.pieslice((0, -height / 5, width, height / 5), 180, 0, p)
    d.flush()
    # write to stdout
    im.paste(img, (right,up))
    im.save("try.png", "PNG")
