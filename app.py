import json

from flask import Flask
from flask_restful import Api

from AllGalleries import AllGalleries
from Gallery import Gallery
from Image import Image

with open('app.config') as json_file:
    conf = json.load(json_file)


# premenna sluziaca na definovanie domovskeho adresara galerie, prvy riadok v konfiguraku
HOME = conf['HOME']



app = Flask(__name__)
api = Api(app)
api.add_resource(AllGalleries, '/gallery')
api.add_resource(Gallery, '/gallery/<path:path>')
api.add_resource(Image, '/image/<string:wxh>/<path:path>')

if __name__ == '__main__':
    app.run(debug=True)
