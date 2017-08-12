import os
basedir = os.path.abspath(os.path.dirname(__file__))


class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'secret'

    SQLALCHEMY_COMMIT_ON_TEARDOWN = True
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_RECORD_QUERIES = True

    DEFAULT_SHOP_EMAIL = os.environ.get('DEFAULT_SHOP_EMAIL') or 'vincent.houba.test@gmail.com'

    
    @staticmethod
    def init_app(app):
        '''after the basic setting you can access the the app instancec'''
        pass


class DevelopmentConfig(Config):
    DEBUG = True
    DEBUG_TB_ENABLED = True
    DEBUG_TB_INTERCEPT_REDIRECTS = False
    DEBUG_TB_PROFILER_ENABLED = True
    DEBUG_TB_TEMPLATE_EDITOR_ENABLED = True
    SQLALCHEMY_DATABASE_URI = os.environ.get('DEV_DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, 'data-dev.sqlite')

    ADMIN_EMAIL = os.environ.get('ADMIN_EMAIL') or 'vincent.houba.test@gmail.com'
    ADMIN_PASSWORD = os.environ.get('ADMIN_PASSWORD') or 'password'
    COMPANY_ADDRESS = os.environ.get('COMPANY_ADDRESS') or 'company address 03 Liege Observatoire'
    


class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = os.environ.get('TEST_DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, 'data-test.sqlite')
    WTF_CSRF_ENABLED = False


class ProductionConfig(Config):
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, 'data-prod.sqlite')

    ADMIN_EMAIL = os.environ.get('ADMIN_EMAIL')
    ADMIN_PASSWORD = os.environ.get('ADMIN_PASSWORD')
    COMPANY_ADDRESS = os.environ.get('COMPANY_ADDRESS')
    

config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}
