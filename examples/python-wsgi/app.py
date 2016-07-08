"""
Python WSGI-Ref Example App
"""
import logging

from stackinabox.services.hello import HelloService

from stackinawsgi import App

lf = logging.FileHandler('python-wsgi-ref.log')
lf.setLevel(logging.DEBUG)
log = logging.getLogger()
log.addHandler(lf)
log.setLevel(logging.DEBUG)

app = App([HelloService])
app.StackInABoxUriUpdate('localhost:8081')
