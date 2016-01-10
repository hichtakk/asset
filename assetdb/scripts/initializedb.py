import os
import sys
import transaction

from sqlalchemy import (
    engine_from_config,
    )

from pyramid.paster import (
    get_appsettings,
    setup_logging,
    )

from pyramid.scripts.common import parse_vars

from ..models import (
    DBSession,
    Maker,
    Vendor,
    Model,
    Location,
    Item,
    Base,
    )


def usage(argv):
    cmd = os.path.basename(argv[0])
    print('usage: %s <config_uri> [var=value]\n'
          '(example: "%s development.ini")' % (cmd, cmd))
    sys.exit(1)


def main(argv=sys.argv):
    if len(argv) < 2:
        usage(argv)
    config_uri = argv[1]
    options = parse_vars(argv[2:])
    setup_logging(config_uri)
    settings = get_appsettings(config_uri, options=options)
    engine = engine_from_config(settings, 'sqlalchemy.')
    DBSession.configure(bind=engine)
    Base.metadata.create_all(engine)
    with transaction.manager:
        maker = Maker(name='Juniper Networks')
        vendor = Vendor(name='NTT Facilities USA', description='NTT Communications')
        model = Model(name='MX960', maker_id=maker.id)
        model_mpc = Model(name='MPC3D-10G', maker_id=maker.id)
        model_sfp = Model(name='SFPP-LR', maker_id=maker.id)
        maker.models.append(model)
        maker.models.append(model_mpc)
        maker.models.append(model_sfp)
        location = Location(name='MDFAXX', description='CC1 3F MDFAXX')
        item = Item(name='luke.net.cc1', serial='XXXXKKKKYYYYY', status='in use', support='send back')
        model.items.append(item)
        vendor.items.append(item)
        location.items.append(item)
        mpc = Item(serial='XXXXKKKKzzzzz', status='in use', support='send back')
        model_mpc.items.append(mpc)
        vendor.items.append(mpc)
        location.items.append(mpc)
        item.attachments.append(mpc)
        DBSession.add(maker)
        DBSession.add(vendor)
        DBSession.add(location)

