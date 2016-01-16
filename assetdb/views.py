from pyramid.response import Response
from pyramid.httpexceptions import (
    HTTPFound,
    HTTPNotFound
    )
from pyramid.view import (
    view_config,
    forbidden_view_config
    )
from pyramid.security import (
    remember,
    forget
    )

from sqlalchemy.exc import DBAPIError

from .models import (
    DBSession,
    Maker,
    Vendor,
    Model,
    Location,
    Item
    )
from .security import USERS


@view_config(route_name='get_maker', renderer='json')
def get_maker(request):
    try:
        response = {'maker': []}
        makers = DBSession.query(Maker).all()
        for maker in makers:
            models = len(maker.models)
            items = 0
            for model in maker.models:
                items += len(model.items)
            response['maker'].append({'id': maker.id, 'name': maker.name, 'description': maker.description, 'models': models, 'items': items})
        return response
    except DBAPIError as e:
        return Response(conn_err_msg, content_type='text/plain', status_int=500)
    return {'one': one, 'project': 'assetdb'}


@view_config(route_name='show_maker', renderer='templates/maker.html')
def show_maker(request):
    try:
        return {}
    except Exception:
        return Response(conn_err_msg, content_type='text/plain', status_int=500)


@view_config(route_name='show_maker_detail', renderer='templates/maker_detail.html')
def show_maker_detail(request):
    try:
        maker_id = request.matchdict['maker_id']
        return {'maker_id': maker_id}
    except Exception:
        return Response(conn_err_msg, content_type='text/plain', status_int=500)


@view_config(route_name='show_model_detail', renderer='templates/model_detail.html')
def show_model_detail(request):
    try:
        model_id = request.matchdict['model_id']
        return {'model_id': model_id}
    except DBAPIError:
        return Response(conn_err_msg, content_type='text/plain', status_int=500)


@view_config(route_name='get_maker_detail', renderer='json')
def get_maker_detail(request):
    try:
        maker_id = request.matchdict['maker_id']
        maker = DBSession.query(Maker).filter(Maker.id==maker_id).one()
        models = []
        for model in maker.models:
            model_items = []
            for item in model.items:
                installed = None
                if item.installed_id:
                    #installed_item = DBSession.query(Item).filter(Item.id==item.installed_id).one()
                    installed = item.installed_description
                model_items.append({'item_id': item.id, 'item_name': item.name, 'serial': item.serial, 'vendor': item.vendor.name, 'support': item.support, 'support_end': str(item.support_end), 'status': item.status, 'asset_number': item.asset_number, 'description': item.description, 'installed': installed})
            models.append({'id':model.id, 'model_name': model.name, 'description': '-', 'asset_items': model_items})
        return {'name': maker.name, 'description': maker.description, 'models': models}
    except Exception:
        return Response(conn_err_msg, content_type='text/plain', status_int=500)


@view_config(route_name='get_model_detail', renderer='json')
def get_model_detail(request):
    try:
        model_id = request.matchdict['model_id']
        model = DBSession.query(Model).filter(Model.id==model_id).one()
        items = []
        for item in model.items:
            items.append(
                {
                    'id': item.id,
                    'name': item.name,
                    'serial': item.serial,
                    'vendor': {
                      'id': item.vendor.id,
                      'name': item.vendor.name,
                    },
                    'installed': item.installed_id,
                    'support': item.support,
                    'support_end': str(item.support_end),
                    'status': item.status,
                    'asset_number': item.asset_number,
                    'settlement_number': item.settlement_number,
                    'delivery_date': str(item.delivery_date),
                    'description': item.description,
                    'updated_at': str(item.updated_at)
                }
            )
        return {'model_id': model_id, 'name': model.name, 'maker': {'id': model.maker.id, 'name': model.maker.name}, 'asset_items': items}
    except DBAPIError:
        return Response(conn_err_msg, content_type='text/plain', status_int=500)


@view_config(route_name='index', renderer='templates/index.html')
def index(request):
    try:
        return {'name': 'hello'}
    except DBAPIError:
        return Response(conn_err_msg, content_type='text/plain', status_int=500)
    return 

@view_config(route_name='asset', renderer='templates/asset.html')
def asset(request):
    try:
        return {}
    except DBAPIError:
        return Response(conn_err_msg, content_type='text/plain', status_int=500)
    return

@view_config(route_name='login', renderer='templates/login.pt')
@forbidden_view_config(renderer='templates/login.pt')
def login(request):
    login_url = request.route_url('login')
    referrer = request.url
    if referrer == login_url:
        referrer = '/' # never use the login form itself as came_from
    came_from = request.params.get('came_from', referrer)
    message = ''
    login = ''
    password = ''
    if 'form.submitted' in request.params:
        login = request.params['login']
        password = request.params['password']
        if USERS.get(login) == password:
            headers = remember(request, login)
            return HTTPFound(location = came_from,
                             headers = headers)
        message = 'Failed login'

    return dict(
        message = message,
        url = request.application_url + '/login',
        came_from = came_from,
        login = login,
        password = password,
        )

@view_config(route_name='logout')
def logout(request):
    headers = forget(request)
    return HTTPFound(location = request.route_url('view_wiki'),
                     headers = headers)


conn_err_msg = """\
Pyramid is having a problem using your SQL database.  The problem
might be caused by one of the following things:

1.  You may need to run the "initialize_assetdb_db" script
    to initialize your database tables.  Check your virtual
    environment's "bin" directory for this script and try to run it.

2.  Your database server may not be running.  Check that the
    database server referred to by the "sqlalchemy.url" setting in
    your "development.ini" file is running.

After you fix the problem, please restart the Pyramid application to
try it again.
"""

