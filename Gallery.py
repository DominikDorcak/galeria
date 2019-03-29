import datetime
import os
import re
import shutil

import facebook
from flask import request
from flask_restful import Resource, abort


class Gallery(Resource):
    HOME = ""

    def __init__(self):
        from app import HOME
        self.HOME = HOME

    def get(self, path):
        json = {}
        gallery = {}
        gallery['path'] = path
        gallery['name'] = path.replace('%20',' ')
        json['gallery'] = gallery
        images = []
        for root, dirs, files in os.walk(os.path.join(self.HOME, path)):
            for file in files:
                image = {}
                image['path'] = file
                image['name'] = os.path.splitext(file)[0].replace('%20',' ')
                image['fullpath'] = os.path.join(path, file)
                image['modified'] = datetime.datetime.fromtimestamp(
                    os.path.getmtime(os.path.join(self.HOME, image['fullpath']))).strftime(
                    '%d.%m.%Y %H:%M:%S')
                images.append(image)
        json['images'] = images
        return json, 200

    def delete(self, path):
        path = os.path.join(self.HOME, path)
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
        pathf = os.path.join(self.HOME, path)
        if not os.path.exists(pathf):
            abort(404)
        if len(request.files.values()) < 1:
            abort(400)
        ctype = request.headers.get('Content-Type')
        ctype = re.findall(r'multipart/form-data', ctype)
        if len(ctype) < 1:
            abort(500)
        # vytiahnutie tokenu z hlavicky
        auth = request.headers.get('Authorization')
        # regexom vytiahnem slovo bearer alebo Bearer
        match = re.search('[Bb]earer', auth)
        if match is None:
            abort(500)
        # token je potom zbytok auth hodnoty, pridane aj vymazanie whitespace znakov pre pripad, ze by to bolo
        # nejakym oddelene
        token = str(auth[match.span()[1]:]).strip()
        # vytiahnutie udajov o pouzivatelovi z Graph API
        try:
            graph = facebook.GraphAPI(access_token=token, version=2.9)
            me = graph.request('/me')
        except facebook.GraphAPIError:
            abort(401)
        for obr in request.files.values():
            filename = obr.filename.replace(' ','%20')
            if '/' in filename:
                abort(500)
            # teraz vsuniem ziskane id na koniec nazvu obrazka pred priponu
            filename = os.path.splitext(filename)
            filename = filename[0] + me.get('id') + filename[1]
            fullpath = os.path.join(pathf, filename)
            obr.save(fullpath)

            map = {
                "path": filename,
                "fullpath": os.path.join(path, filename),
                "name": os.path.splitext(filename)[0].replace('%20',' '),
                "modified": datetime.datetime.fromtimestamp(os.path.getmtime(fullpath)).strftime('%d.%m.%Y %H:%M:%S')
            }
            list.append(map)
        json['uploaded'] = list
        return json, 201
