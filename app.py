from chalice import Chalice
from chalice import BadRequestError

# modulos para crear la conexón a la Base de Datos
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from sqlalchemy import Column
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy import Float
from sqlalchemy import Boolean
from sqlalchemy import DateTime
from sqlalchemy import ForeignKey

from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import relationship

from sqlalchemy.exc import IntegrityError

from chalicelib.utils import DateTimeFormat
from datetime import datetime

import os
import json

db_user = os.environ.get('USER', default=None)
db_pass = os.environ.get('PASS', default=None)
db_name = os.environ.get('NAME', default=None)
db_host = os.environ.get('HOST', default=None)
driver  = os.environ.get('DRIVER', default=None)

engine = create_engine(f"{driver}://{db_user}:{db_pass}@{db_host}/{db_name}", future=True)

session = Session(engine)

app = Chalice(app_name='test')

Base = declarative_base()

class UnitMeasure(Base):
    '''
        Clase para la creación de la tabla unit measures.

        Atributos:
            * id
            * name
            * is_active
            * product
    '''
    __tablename__ = 'unit_measures'

    id = Column(Integer(), primary_key = True)
    name = Column(String(50))
    is_active = Column(Boolean(), default=True)
    product = relationship('Products')

    def to_JOSN(self) -> list:
        '''
            Función para hacer el formateo a JSON con base en la estructura de la tabla
            unit measures.
        '''
        return {
            'id': self.id,
            'name': self.name,
            'is_active': self.is_active
        }

    def __repr__(self) -> str:
        '''
            Función para mostrar el nombre del producto al consultar dentro de una petición.
        '''
        return '{}'.format(self.name)

class Products(Base):
    '''
        Clase para la creación de la tabla products

        Atributos:
            * id
            * name
            * price
            * is_active
            * unit_measure_id
    '''
    __tablename__ = 'products'

    id = Column(Integer(), primary_key = True)
    name = Column(String(50))
    price = Column(Float())
    is_active = Column(Boolean(), default=True)
    unit_measure_id = Column(ForeignKey(UnitMeasure.id, ondelete='CASCADE'))

    def to_JOSN(self) -> list:
        '''
            Función para hacer el formateo a JSON con base en la estructura de la tabla
            products.
        '''
        return {
            'id': self.id,
            'name': self.name,
            'price': self.price,
            'is_active': self.is_active,
            'unit_measure_id': self.unit_measure_id
        }

    def __repr__(self) -> str:
        '''
            Función para mostrar el nombre del producto al consultar dentro de una petición.
        '''
        return '{}'.format(self.name)

class Sales(Base):
    '''
        Clase para la creación de la tabla sales

        Atributos:
            * id
            * date
            * quantity
            * is_active
            * product_id
    '''
    __tablename__ = 'sales'

    id = Column(Integer(), primary_key = True)
    date = Column(DateTime(), default=datetime.now())
    quantity = Column(Integer())
    is_active = Column(Boolean(), default=True)
    product_id = Column(ForeignKey(Products.id, ondelete='CASCADE'))

    def to_JOSN(self) -> list:
        '''
            Función para hacer el formateo a JSON con base en la estructura de la tabla
            sales.
        '''
        return {
            'id': self.id,
            'date': DateTimeFormat.convert_date(self.date),
            'quantity': self.quantity,
            'is_active': self.is_active,
            'product_id': self.product_id
        }

    def __repr__(self) -> str:
        '''
            Función para mostrar el nombre del producto al consultar dentro de una petición.
        '''
        return '{}'.format(self.name)

# Base.metadata.drop_all(engine)
# Base.metadata.create_all(engine)

def add_data(result) -> None:
    session.add(result)
    session.commit()

@app.route('/')
def index():
    return {'data': 'Servicio activo'}

@app.route('/products', methods=['GET', 'POST'], content_types=['application/json'])
def products():
    try:
        request = app.current_request
        with session.begin():
            if request.method == 'GET':
                products = session.query(Products).filter_by(is_active=True).all()
                data = []
                for product in products:
                    data.append(product.to_JOSN())
                if len(data) != 0:
                    return data
                return {'data': 'No se encontraron los datos'}
            elif request.method == 'POST':
                json_data = json.loads(request.raw_body)
                result = Products(name=json_data['name'], price=json_data['price'], unit_measure_id=json_data['unit_measure_id'])
                add_data(result)
                return {'data': 'Dato insertado correctamente'}
    except IntegrityError:
        raise BadRequestError("No se pudieron procesar los datos")
    except Exception as e:
        session.rollback()
        raise Exception(e)

@app.route('/products/{id}', methods=['GET', 'PUT', 'DELETE'], content_types=['application/json'])
def products(id):
    try:
        request = app.current_request
        with session.begin():
            if request.method == 'GET':
                unit_measures = session.query(Products).filter_by(id=id)
                data = []
                for unit_measure in unit_measures:
                    data.append(unit_measure.to_JOSN())
                if data[0]['is_active'] != False:
                    return data
                return {'data': 'Dato no encontrado'}
            elif request.method == 'PUT':
                json_data = json.loads(request.raw_body)
                result = session.query(Products).filter_by(id=id).first()
                if result.is_active == False:
                    return {'data': 'Dato no encontrado'}
                result.name = json_data['name']
                add_data(result)
                return {'data': 'Dato actualizado correctamente'}
            elif request.method == 'DELETE':
                result = session.query(Products).filter_by(id=id).first()
                if result.is_active == False:
                    return {'data': 'Dato no encontrado'}    
                result.is_active = False
                add_data(result)
                return {'data': 'Dato eliminado correctamente'}
    except Exception as e:
        session.rollback()
        raise Exception(e)

@app.route('/unit_measures', methods=['GET', 'POST'], content_types=['application/json'])
def unit_measures():
    try:
        request = app.current_request
        with session.begin():
            if request.method == 'GET':
                unit_measures = session.query(UnitMeasure).filter_by(is_active=True).all()
                data = []
                for unit_measure in unit_measures:
                    data.append(unit_measure.to_JOSN())            
                if len(data) != 0:
                    return data
                return {'data': 'No se encontraron los datos'}
            elif request.method == 'POST':
                json_data = json.loads(request.raw_body)
                print(json_data)
                result = UnitMeasure(name=json_data['name'])
                add_data(result)
                return {'data': 'Dato insertado correctamente'}
    except Exception as e:
        session.rollback()
        raise Exception(e)

@app.route('/unit_measures/{id}', methods=['GET', 'PUT', 'DELETE'], content_types=['application/json'])
def unit_measures(id):
    try:
        request = app.current_request
        with session.begin():
            if request.method == 'GET':
                unit_measures = session.query(UnitMeasure).filter_by(id=id)
                data = []
                for unit_measure in unit_measures:
                    data.append(unit_measure.to_JOSN())
                if len(data) == 0:
                    return {'data': 'Dato no encontrado'}
                if data[0]['is_active'] != False:
                    return data
                return {'data': 'Dato no encontrado'}
            elif request.method == 'PUT':
                json_data = json.loads(request.raw_body)
                result = session.query(UnitMeasure).filter_by(id=id).first()
                if result.is_active == False:
                    return {'data': 'Dato no encontrado'}    
                result.name = json_data['name']
                add_data(result)
                return {'data': 'Dato actualizado correctamente'}
            elif request.method == 'DELETE':
                result = session.query(UnitMeasure).filter_by(id=id).first()
                if result.is_active == False:
                    return {'data': 'Dato no encontrado'}    
                result.is_active = False
                add_data(result)
                return {'data': 'Dato eliminado correctamente'}
    except Exception as e:
        session.rollback()
        raise Exception(e)