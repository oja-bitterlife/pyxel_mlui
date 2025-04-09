#from samples.DQ import bootstrap
#from samples.FF import bootstrap
#from samples.FE import bootstrap
from tomlui import core


from tomlui.ext import orm
from tomlui.ext.orm import XUEStateCore,XUEORM

orm = orm.XUEORM()
session = XUEStateCore.create_session_from_toml(orm, "samples/DQ/assets/ui/title.toml")

# for result in orm.execute(session, "SELECT * FROM STATE_CORE"):
    # print(result)

for result in session.query(XUEStateCore).all():
    print(result.__dict__)
