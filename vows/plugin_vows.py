#!/usr/bin/python
# -*- coding: utf-8 -*-

# thumbor imaging service
# https://github.com/thumbor/thumbor/wiki

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2011 globo.com timehome@corp.globo.com

from os.path import abspath, join, dirname, exists
from shutil import rmtree

from pyvows import Vows, expect
from tornado_pyvows.context import TornadoHTTPContext

from thumbor import __version__
from thumbor.app import ThumborServiceApp
from thumbor.importer import Importer
from thumbor.config import Config
from thumbor.context import Context, ServerParameters

storage_path = abspath(join(dirname(__file__), 'fixtures/'))

FILE_STORAGE_ROOT_PATH = '/tmp/thumbor-vows/handler_image_vows'


class BaseContext(TornadoHTTPContext):
    def __init__(self, *args, **kw):
        super(BaseContext, self).__init__(*args, **kw)


@Vows.batch
class GetImage(BaseContext):
    def get_app(self):
        cfg = Config(SECURITY_KEY='ACME-SEC')
        cfg.LOADER = "thumbor.loaders.file_loader"
        cfg.FILE_LOADER_ROOT_PATH = storage_path
        cfg.STORAGE = "thumbor.storages.file_storage"
        cfg.FILE_STORAGE_ROOT_PATH = FILE_STORAGE_ROOT_PATH
        if exists(FILE_STORAGE_ROOT_PATH):
            rmtree(FILE_STORAGE_ROOT_PATH)

        importer = Importer(cfg)
        importer.import_modules()
        server = ServerParameters(8889, 'localhost', 'thumbor.conf', None, 'info', None)
        server.security_key = 'ACME-SEC'
        ctx = Context(server, cfg, importer)
        application = ThumborServiceApp(ctx)

        return application

    class WithRegularImage(TornadoHTTPContext):
        def topic(self):
            response = self.get('/unsafe/smart/image.jpg')
            return (response.code, response.headers)

        def should_be_200(self, response):
            code, _ = response
            expect(code).to_equal(200)

        def should_include_server_name(self, response):
            _, headers = response
            expect(headers).to_include('Server')
            expect(headers['Server']).to_equal('Thumbor/%s' % __version__)
