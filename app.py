from flask import Flask
from flask_restful import Api

from AllGalleries import AllGalleries
from Gallery import Gallery
from Image import Image

conf = open('./app.config','r')
# premenna sluziaca na definovanie domovskeho adresara galerie, prvy riadok v konfiguraku
HOME = conf.readline()



app = Flask(__name__)
api = Api(app)
api.add_resource(AllGalleries, '/gallery')
api.add_resource(Gallery, '/gallery/<path:path>')
api.add_resource(Image, '/image/<string:wxh>/<path:path>')

if __name__ == '__main__':
    app.run()
