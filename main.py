#from samples.DQ import bootstrap
#from samples.FF import bootstrap
#from samples.FE import bootstrap

from tomlui.core import TOMLUI,XUStateCore,XUStatePos,XUSelectBase

toml_ui = TOMLUI()
tables = toml_ui.inspector.get_table_names()

for table in tables:
    columns = toml_ui.inspector.get_columns(table)
    print(table, [col["name"] for col in columns])

toml_ui.session.add(XUStateCore(tag="test", pos=XUStatePos(x=12, y=34)))
toml_ui.session.add(XUSelectBase(base=XUStateCore(tag="test", pos=XUStatePos(x=12, y=34))))

#print( toml_ui.session.query(XUStateCore).one().__dict__ )
print( toml_ui.session.query(XUSelectBase).one().base.pos.__dict__ )


