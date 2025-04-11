#from samples.DQ import bootstrap
#from samples.FF import bootstrap
#from samples.FE import bootstrap

from tomlui.core import TOMLUI,XUStateCore,XUStateSelect,XUStateSelectItem

toml_ui = TOMLUI()
print(toml_ui.inspector.get_table_names())

toml_ui.load_toml("samples/DQ/assets/ui/title.toml")
print(toml_ui)

for item in toml_ui.session.query(XUStateSelectItem).all():
    print(item.__dict__)
