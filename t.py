import dearpygui.dearpygui as dpg



state = False
def button_callback(sender, app_data):
  global state
  state = not state

  dpg.bind_item_theme(sender, enabled_theme if state else disabled_theme)


dpg.create_context()

with dpg.theme() as enabled_theme:
    with dpg.theme_component(dpg.mvAll):
        dpg.add_theme_color(dpg.mvThemeCol_Text, (255, 255, 255), category=dpg.mvThemeCat_Core)


with dpg.theme() as disabled_theme:
    with dpg.theme_component(dpg.mvAll):
        dpg.add_theme_color(dpg.mvThemeCol_Text, (255, 0, 0), category=dpg.mvThemeCat_Core)
dpg.create_viewport(title='Toggle Button Example', width=400, height=200)




with dpg.window(pos=(0,0),width=900, height=725,tag='papa'):
    dpg.add_button(label="Some label", callback=button_callback)





dpg.create_viewport()
dpg.setup_dearpygui()
dpg.show_viewport()
dpg.start_dearpygui()
dpg.destroy_context()