"""
Gunicorn Example App
"""

from stackinabox.services.hello import HelloService

from stackinawsgi import App

app = App([HelloService()])
app.StackInABoxUriUpdate('localhost:8081')
