import os

import PIL
from flask import send_file
from flask_restful import Resource
from resizeimage import resizeimage


class Image(Resource):

    HOME = ""

    def __init__(self):
        from app import HOME
        self.HOME = HOME

    def get(self, wxh, path):
        path = path.replace(' ', '%20')
        w, h = wxh.split('x')
        w = int(w)
        h = int(h)
        obrazok = os.path.join(self.HOME, path)
        ext = os.path.splitext(obrazok)[1]
        # Temp subor do ktoreho ukladam zmenseny/zvacseny obrazok
        if os.path.exists('./static/temp' + ext):
            os.remove('./static/temp' + ext)
        fd_img = open(obrazok, 'r')
        img = PIL.Image.open(fd_img)
        if w == 0:
            temp = resizeimage.resize_height(img, h)
        else:
            if h == 0:
                temp = resizeimage.resize_width(img, w)
            else:
                # ak su zadane obidva rozmery obrazok orezem
                temp = resizeimage.resize_cover(img, [w, h])
        temp.save('./static/temp' + ext, temp.format)
        return send_file('./static/temp' + ext, mimetype='image/' + ext[1:])