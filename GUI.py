
import dearpygui.dearpygui as dpg


from fdialog import FileDialog
from PIL import Image
from callback import save_dxf,save_as_gcode,print_me,check_callback,find_closest_point,read_dxf_lines,callback_to_gcode
import callback
import numpy as np
import optimize



def plot_mouse_click_callback():
    x,y = dpg.get_plot_mouse_pos()
    p,i,m,l = find_closest_point(callback.lines,(x,y),range(len(callback.lines)))
    
    if dpg.get_value('1'):
        for j in l:
            callback.ts[j] = 0
    elif dpg.get_value('2'):
        for j in l:
            callback.ts[j] = 1
    elif dpg.get_value('3'):
        for j in l:
            callback.ts[j] = 2
    elif dpg.get_value('4'):
        for j in l:
            callback.ts[j] = 3
    elif dpg.get_value('5'):
        for j in l:
            callback.ts[j] = 4
    redraw()
    
def redraw():
    dpg.delete_item(Y_AXIS_TAG, children_only=True, slot=1)

    for i in range(len(callback.lines)):
        start = callback.lines[i]['start']
        end = callback.lines[i]['end']
        
        dpg.add_line_series([start[0], end[0]], [start[1], end[1]],label=f"Line ", parent=Y_AXIS_TAG)
        dpg.bind_item_theme(dpg.last_item(), themes[callback.ts[i]])
def plot_dxf(file_path):
        
        callback.lines,callback.ts  = read_dxf_lines(file_path)
        redraw()
def optimize_():
    
    dpg.set_value('file','temp.dxf')
    optimize.create_continuous_lines('temp.dxf',callback.lines )
    plot_dxf('temp.dxf')

def pr(selected_files):
    current_file = selected_files[0]
    if '.dxf' in current_file:
    
        plot_dxf(current_file)
    if '.png' in current_file:
        print(current_file)
        width, height, channels, data = dpg.load_image('C:\\Users\\kachan\\Desktop\\10лет.png')

        with dpg.texture_registry(show=True):
            dpg.add_static_texture(width=width, height=height, default_value=data, tag="texture_tag")
            dpg.add_image("texture_tag",parent='plot')







dpg.create_context()

X_AXIS_TAG = "x_axis_tag"
Y_AXIS_TAG = "y_axis_tag"

current_file = None
themes = []
components = []

with dpg.theme(tag="coloured_line_theme1") as coloured_line_theme1:
    with dpg.theme_component():
        coloured_line_component1 = dpg.add_theme_color(dpg.mvPlotCol_Line, (0, 191, 255, 255), category=dpg.mvThemeCat_Plots)
with dpg.theme(tag="coloured_line_theme2") as coloured_line_theme2:
    with dpg.theme_component():
        coloured_line_component2 = dpg.add_theme_color(dpg.mvPlotCol_Line, (255, 20, 147, 255), category=dpg.mvThemeCat_Plots)
with dpg.theme(tag="coloured_line_theme3") as coloured_line_theme3:
    with dpg.theme_component():
        coloured_line_component3 = dpg.add_theme_color(dpg.mvPlotCol_Line, (255, 215, 0, 255), category=dpg.mvThemeCat_Plots)
with dpg.theme(tag="coloured_line_theme4") as coloured_line_theme4:
    with dpg.theme_component():
        coloured_line_component4 = dpg.add_theme_color(dpg.mvPlotCol_Line, (0, 255, 127, 255), category=dpg.mvThemeCat_Plots)

with dpg.theme(tag="coloured_line_theme5") as coloured_line_theme5:
    with dpg.theme_component():
        coloured_line_component5 = dpg.add_theme_color(dpg.mvPlotCol_Line, (255, 69, 0, 255 ), category=dpg.mvThemeCat_Plots)
themes.append(coloured_line_theme1)
components.append(coloured_line_component1)
themes.append(coloured_line_theme2)
components.append(coloured_line_component2)
themes.append(coloured_line_theme3)
components.append(coloured_line_component3)
themes.append(coloured_line_theme4)
components.append(coloured_line_component4)
themes.append(coloured_line_theme5)
components.append(coloured_line_component5)


with dpg.theme() as coloured_Core_theme1:
    with dpg.theme_component():
        coloured_core_component1 = dpg.add_theme_color(dpg.mvThemeCol_CheckMark, (0, 191, 255, 255), category=dpg.mvThemeCat_Core)
        coloured_core_component11= dpg.add_theme_color(dpg.mvThemeCol_Text, (0, 191, 255, 255), category=dpg.mvThemeCat_Core)
with dpg.theme() as coloured_Core_theme2:
    with dpg.theme_component():
        coloured_core_component2 = dpg.add_theme_color(dpg.mvThemeCol_CheckMark, (255, 20, 147, 255), category=dpg.mvThemeCat_Core)
        coloured_core_component21= dpg.add_theme_color(dpg.mvThemeCol_Text, (255, 20, 147, 255), category=dpg.mvThemeCat_Core)
with dpg.theme() as coloured_Core_theme3:
    with dpg.theme_component():
        coloured_core_component3 = dpg.add_theme_color(dpg.mvThemeCol_CheckMark, (255, 215, 0, 255), category=dpg.mvThemeCat_Core)
        coloured_core_component31= dpg.add_theme_color(dpg.mvThemeCol_Text, (255, 215, 0, 255), category=dpg.mvThemeCat_Core)
with dpg.theme() as coloured_Core_theme4 :
    with dpg.theme_component():
        coloured_core_component4 = dpg.add_theme_color(dpg.mvThemeCol_CheckMark, (0, 255, 127, 255), category=dpg.mvThemeCat_Core)
        coloured_core_component41= dpg.add_theme_color(dpg.mvThemeCol_Text, (0, 255, 127, 255), category=dpg.mvThemeCat_Core)
with dpg.theme() as coloured_Core_theme5:
    with dpg.theme_component():
        coloured_core_component5 = dpg.add_theme_color(dpg.mvThemeCol_CheckMark, (255, 69, 0, 255 ), category=dpg.mvThemeCat_Core)
        coloured_core_component51= dpg.add_theme_color(dpg.mvThemeCol_Text, (255, 69, 0, 255 ), category=dpg.mvThemeCat_Core)


fd = FileDialog(callback=pr, show_dir_size=False, modal=False, allow_drag=False,width=800,height=400,filter_list=[".dxf",".png"],)

with dpg.viewport_menu_bar():
    with dpg.menu(label="File"):
        dpg.add_menu_item(label="Open", callback=fd.show_file_dialog)
        dpg.add_menu_item(label="Save As Gcode", callback=save_as_gcode)
        dpg.add_menu_item(label="Save As", callback=save_dxf)
        
        
        with dpg.menu(label="Settings"):
            dpg.add_menu_item(label="Setting 1", callback=print_me, check=True)
            dpg.add_menu_item(label="Setting 2", callback=print_me)

    dpg.add_menu_item(label="Optimize", callback=optimize_)

    with dpg.menu(label="Widget Items"):
        dpg.add_checkbox(label="Pick Me", callback=print_me)
        dpg.add_button(label="Press Me", callback=print_me)
        dpg.add_color_picker(label="Color Me", callback=print_me)      



with dpg.window(pos=(0,0),width=900, height=700,tag='papa'):
    with dpg.group(horizontal=True):
        with dpg.group():
            # with dpg.file_dialog(directory_selector=False, show=False, callback=callback_, id="file_dialog_id", width=700 ,height=400):
            #         dpg.add_file_extension("", color=(150, 255, 150, 255))
            #         dpg.add_file_extension(".dxf", color=(255, 0, 255, 255), custom_text="[DXF]")
            #         dpg.add_file_extension(".png", color=(255, 0, 0, 255), custom_text="[PNG]")
            with dpg.file_dialog(directory_selector=False, show=False, callback=callback_to_gcode, id="file_dialog_id2", width=700 ,height=400):
                    dpg.add_file_extension(".gcode", color=(255, 0, 255, 255), custom_text="[DXF]")
            dpg.add_text(tag='file')
            with dpg.plot(label="DXF Plot", width=600, height=600, tag="plot",no_menus=True, no_box_select=True) as plot:
                dpg.add_plot_axis(dpg.mvXAxis, label="X-Axis", tag=X_AXIS_TAG)
                
            
                yaxis = dpg.add_plot_axis(dpg.mvYAxis, label="Y-Axis", tag=Y_AXIS_TAG)
                
                dpg.set_axis_limits_constraints(Y_AXIS_TAG,-10,310)
                dpg.set_axis_limits_constraints(X_AXIS_TAG,-10,310)
            
            with dpg.group(horizontal=True):
                with dpg.group():
                    dpg.add_text("order")
                    dpg.add_text("power")
                    dpg.add_text("speed")
                with dpg.group():
                    dpg.add_checkbox(label="1",tag='1',callback=check_callback)
                    dpg.bind_item_theme(dpg.last_item(), coloured_Core_theme1)
                    dpg.add_input_text(width=50,scientific=True,tag='1_value',default_value='100')
                    dpg.add_input_text(width=50,scientific=True,tag='11_value',default_value='1000')
                with dpg.group():
                    dpg.add_checkbox(label="2",tag='2',callback=check_callback)
                    dpg.bind_item_theme(dpg.last_item(), coloured_Core_theme2)
                    dpg.add_input_text(width=50,scientific=True,tag='2_value',default_value='100')
                    dpg.add_input_text(width=50,scientific=True,tag='21_value',default_value='1000')
                with dpg.group():
                    dpg.add_checkbox(label="3",tag='3',callback=check_callback)
                    dpg.bind_item_theme(dpg.last_item(), coloured_Core_theme3)
                    dpg.add_input_text(width=50,scientific=True,tag='3_value',default_value='100')
                    dpg.add_input_text(width=50,scientific=True,tag='31_value',default_value='1000')
                with dpg.group():
                    dpg.add_checkbox(label="4",tag='4',callback=check_callback)
                    dpg.bind_item_theme(dpg.last_item(), coloured_Core_theme4)
                    dpg.add_input_text(width=50,scientific=True,tag='4_value',default_value='100')
                    dpg.add_input_text(width=50,scientific=True,tag='41_value',default_value='1000')
                with dpg.group():
                    dpg.add_checkbox(label="5",tag='5',callback=check_callback)
                    dpg.bind_item_theme(dpg.last_item(), coloured_Core_theme5)
                    dpg.add_input_text(width=50,scientific=True,tag='5_value',default_value='100')
                    dpg.add_input_text(width=50,scientific=True,tag='51_value',default_value='1000')

        dpg.add_input_text(multiline=True, label="", default_value="G00 X5 Y5; point B\nG01 X0 Y20 F200; point C\nG01 X20 Y0; point D\nG02 X10 Y-10 I0 J-10; point E\nG02 X-4 Y-8 I-10 J0; point F\nG01 X-26 Y-2 ; point B\n", tag="multiline_input", readonly=True,width=300,height=600)
    
with dpg.item_handler_registry() as registry:
    dpg.add_item_clicked_handler(button=dpg.mvMouseButton_Right, callback=plot_mouse_click_callback)
dpg.bind_item_handler_registry(plot, registry)



dpg.create_viewport(width=915, height=765, title="Plot Update Line Colour")
dpg.setup_dearpygui()
dpg.show_viewport()
dpg.start_dearpygui()
dpg.destroy_context()