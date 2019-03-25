import os, datetime, shutil, PIL.Image, requests, urllib3, facebook

from werkzeug.utils import secure_filename
from flask import Flask, request, send_file
from flask_restful import Resource, Api, abort
from resizeimage import resizeimage

# premenna sluziaca na definovanie domovskeho adresara galerie
HOME = '/home/dominik/Gallery'

app = Flask(__name__)
api = Api(app)


class AllGalleries(Resource):
    def get(self):
        galleries = []
        json = {}
        for root, dirs, files in os.walk(HOME):
            for name in dirs:
                galeria = {}
                galeria['path'] = name
                galeria['name'] = name
                for r, d, f in os.walk(os.path.join(root, name)):
                    poc = 0
                    for file in f:
                        if poc == 0:
                            obr = {}
                            obr['path'] = file
                            obr['name'] = os.path.splitext(file)[0]
                            obr['fullpath'] = os.path.join(name, file)
                            obr['modified'] = datetime.datetime.fromtimestamp(
                                os.path.getmtime(os.path.join(HOME, obr['fullpath']))).strftime(
                                '%d.%m.%Y %H:%M:%S')
                            galeria['image'] = obr
                            poc = 1
                galleries.append(galeria)
        json['galleries'] = galleries
        return json, 200

    def post(self):
        req = request.get_json()
        name = req['name']
        path = os.path.join(HOME, secure_filename(name))
        if os.path.isdir(path):
            abort(409)
        if len(name) < 1:
            abort(400)

        else:
            os.mkdir(path)
            resp = {}
            resp['name'] = name
            resp['path'] = secure_filename(name)
            return resp, 201


api.add_resource(AllGalleries, '/gallery')


class Gallery(Resource):
    def get(self, path):
        json = {}
        gallery = {}
        gallery['path'] = path
        gallery['name'] = path
        json['gallery'] = gallery
        images = []
        for root, dirs, files in os.walk(os.path.join(HOME, path)):
            for file in files:
                image = {}
                image['path'] = file
                image['name'] = os.path.splitext(file)[0]
                image['fullpath'] = os.path.join(path, file)
                image['modified'] = datetime.datetime.fromtimestamp(
                    os.path.getmtime(os.path.join(HOME, image['fullpath']))).strftime(
                    '%d.%m.%Y %H:%M:%S')
                images.append(image)
        json['images'] = images
        return json, 200

    def delete(self, path):
        path = os.path.join(HOME, path)
        if os.path.isdir(path):
            shutil.rmtree(path)
            return
        else:
            if os.path.isfile(path):
                os.remove(path)
                return
            else:
                abort(404)

    def post(self, path):
        json = {}
        list = []
        ctype = request.headers['Content-Type']
        if not ctype.split(';')[0] == "multipart/form-data":
            abort(500)
        #vytiahnutie tokenu z hlavicky
        bearer, token = request.headers['Authorization'].split(' ')
        if not bearer == 'Bearer':
            abort(500)
        #vytiahnutie udajov o pouzivatelovi z Graph API
        graph = facebook.GraphAPI(access_token=token, version=2.7)
        me = graph.request('/me')
        pathf = os.path.join(HOME, path)
        if not os.path.exists(pathf):
            abort(404)
        obr = request.files['image']
        filename = secure_filename(obr.filename)
        #teraz vsuniem ziskane id na koniec nazvu obrazka pred priponu
        filename = os.path.splitext(filename)
        filename = filename[0]+me['id']+filename[1]
        fullpath = os.path.join(pathf, filename)
        obr.save(fullpath)

        map = {
            "path": filename,
            "fullpath": os.path.join(path, filename),
            "name": os.path.splitext(filename)[0],
            "modified": datetime.datetime.fromtimestamp(os.path.getmtime(fullpath)).strftime('%d.%m.%Y %H:%M:%S')
        }
        list.append(map)
        json['uploaded'] = list
        return json, 201


api.add_resource(Gallery, '/gallery/<string:path>')


class Image(Resource):
    def get(self, wxh, path):
        w, h = wxh.split('x')
        w = int(w)
        h = int(h)
        obrazok = os.path.join(HOME, path)
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
                # ak su zadane obidva rozmery pokusim sa co najlepsie obrazok napchat do
                # zadanej velkosti so zachovanym pomeru stran
                temp = resizeimage.resize_thumbnail(img, [w, h])
        temp.save('./static/temp' + ext, temp.format)
        return send_file('./static/temp' + ext, mimetype='image/' + ext[1:])


api.add_resource(Image, '/image/<string:wxh>/<path:path>')

if __name__ == '__main__':
    app.run()
