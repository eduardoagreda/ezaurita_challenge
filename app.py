from chalice import Chalice

app = Chalice(app_name='test')

@app.route('/')
def index():
    return {'data': 'hola'}

