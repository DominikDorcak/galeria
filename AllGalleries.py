import datetime
import os

from flask import request
from flask_restful import Resource, abort



class AllGalleries(Resource):

    HOME = ""

    def __init__(self):
        from app import HOME
        self.HOME = HOME

    def get(self):
        galleries = []
        json = {}
        for root, dirs, files in os.walk(self.HOME):
            for name in dirs:
                galeria = {}
                galeria['path'] = name
                galeria['name'] = name.replace('%20',' ')
                for r, d, f in os.walk(os.path.join(root, name)):
                    poc = 0
                    for file in f:
                        if poc == 0:
                            obr = {}
                            obr['path'] = file
                            obr['name'] = os.path.splitext(file)[0]
                            obr['fullpath'] = os.path.join(name, file)
                            obr['modified'] = datetime.datetime.fromtimestamp(
                                os.path.getmtime(os.path.join(self.HOME, obr['fullpath']))).strftime(
                                '%d.%m.%Y %H:%M:%S')
                            galeria['image'] = obr
                            poc = 1
                galleries.append(galeria)
        json['galleries'] = galleries
        return json, 200

    def post(self):
        req = request.get_json()
        if not 'name' in req.keys():
            abort(400)
        name = req['name']
        if '/' in name:
            abort(500)
        pathFromName = name.replace(' ','%20')
        path = os.path.join(self.HOME, pathFromName)
        if os.path.isdir(path):
            abort(409)
        os.mkdir(path)
        resp = {}
        resp['name'] = name
        resp['path'] = pathFromName
        return resp, 201