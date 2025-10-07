
import dearpygui.dearpygui as dpg
import ezdxf
import math
import svgwrite
import test_G_code
import numpy as np
dpg.create_context()

DEFAULT_LINE_COLOUR = (125, 255, 0,255)


X_AXIS_TAG = "x_axis_tag"
Y_AXIS_TAG = "y_axis_tag"
current_file = None
lines =[]
ts = []
themes = []
components = []
with dpg.theme() as coloured_line_theme1:
    with dpg.theme_component():
        coloured_line_component1 = dpg.add_theme_color(dpg.mvPlotCol_Line, (0, 191, 255, 255), category=dpg.mvThemeCat_Plots)
with dpg.theme() as coloured_line_theme2:
    with dpg.theme_component():
        coloured_line_component2 = dpg.add_theme_color(dpg.mvPlotCol_Line, (255, 20, 147, 255), category=dpg.mvThemeCat_Plots)
with dpg.theme() as coloured_line_theme3:
    with dpg.theme_component():
        coloured_line_component3 = dpg.add_theme_color(dpg.mvPlotCol_Line, (255, 215, 0, 255), category=dpg.mvThemeCat_Plots)
with dpg.theme() as coloured_line_theme4:
    with dpg.theme_component():
        coloured_line_component4 = dpg.add_theme_color(dpg.mvPlotCol_Line, (0, 255, 127, 255), category=dpg.mvThemeCat_Plots)

with dpg.theme() as coloured_line_theme5:
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
        coloured_core_component51= dpg.add_theme_color(dpg.mvThemeCol_Text, (0, 191, 255, 255), category=dpg.mvThemeCat_Core)
with dpg.theme() as coloured_Core_theme2:
    with dpg.theme_component():
        coloured_core_component2 = dpg.add_theme_color(dpg.mvThemeCol_CheckMark, (255, 20, 147, 255), category=dpg.mvThemeCat_Core)
        coloured_core_component51= dpg.add_theme_color(dpg.mvThemeCol_Text, (255, 20, 147, 255), category=dpg.mvThemeCat_Core)
with dpg.theme() as coloured_Core_theme3:
    with dpg.theme_component():
        coloured_core_component3 = dpg.add_theme_color(dpg.mvThemeCol_CheckMark, (255, 215, 0, 255), category=dpg.mvThemeCat_Core)
        coloured_core_component51= dpg.add_theme_color(dpg.mvThemeCol_Text, (255, 215, 0, 255), category=dpg.mvThemeCat_Core)
with dpg.theme() as coloured_Core_theme4 :
    with dpg.theme_component():
        coloured_core_component4 = dpg.add_theme_color(dpg.mvThemeCol_CheckMark, (0, 255, 127, 255), category=dpg.mvThemeCat_Core)
        coloured_core_component51= dpg.add_theme_color(dpg.mvThemeCol_Text, (0, 255, 127, 255), category=dpg.mvThemeCat_Core)
with dpg.theme() as coloured_Core_theme5:
    with dpg.theme_component():
        coloured_core_component5 = dpg.add_theme_color(dpg.mvThemeCol_CheckMark, (255, 69, 0, 255 ), category=dpg.mvThemeCat_Core)
        coloured_core_component51= dpg.add_theme_color(dpg.mvThemeCol_Text, (255, 69, 0, 255 ), category=dpg.mvThemeCat_Core)


def arc_to_lines(center, radius, start_angle, end_angle, num_segments):
    # Преобразование углов из градусов в радианы
    start_angle_rad = np.radians(start_angle)
    end_angle_rad = np.radians(end_angle)

    # Создание массива углов
    angles = np.linspace(start_angle_rad, end_angle_rad, num_segments + 1)

    # Вычисление координат точек на дуге
    points = [(center[0] + radius * np.cos(angle), center[1] + radius * np.sin(angle)) for angle in angles]
    
    return points
def read_dxf_lines(file_path):
    
    doc = ezdxf.readfile(file_path)
    msp = doc.modelspace()
    lines = []

    for line in msp.query('LINE'):
        lines.append({
            'start': (line.dxf.start.x, line.dxf.start.y),
            'end': (line.dxf.end.x, line.dxf.end.y)
        })
    for acdb_line in msp.query('AcDbLine'):
        lines.append({
            'start': (acdb_line.dxf.start.x, acdb_line.dxf.start.y),
            'end': (acdb_line.dxf.end.x, acdb_line.dxf.end.y)
        })

    for arc in msp.query('ARC'):
        center = arc.dxf.center  # Центр арки
        radius = arc.dxf.radius   # Радиус
        start_angle = arc.dxf.start_angle  # Начальный угол
        end_angle = arc.dxf.end_angle
        if radius<10:
            points = arc_to_lines(center, radius, start_angle, end_angle,10)
        else:
            points = arc_to_lines(center, radius, start_angle, end_angle,50)
        
        for i in range(len(points)-1):
            lines.append({
            'start': (points[i][0], points[i][1]),
            'end': (points[i+1][0], points[i+1][1])
        })
    return lines
def change_colour(_, rgba_values):
    dpg.set_value(components[0], [value*255 for value in rgba_values])
def distance(point1, point2):
    return math.sqrt((point1[0] - point2[0]) ** 2 + (point1[1] - point2[1]) ** 2)
def find_closest_pointt(lines, target_point,nums):
    closest_point = None
    min_distance = float('inf')
    I = 0
    i = 0
    mode = 1
    for line in lines:
        if i in nums:
            m = 1
            for point in [line['start'], line['end']]:
                dist = distance(point, target_point)
                if dist < min_distance:
                    min_distance = dist
                    closest_point = point
                    mode = m
                    I = i
                m = 0
            
        i += 1

    return closest_point,I,mode
def find_closest_point(lines, target_point,nums):
    closest_point = None

    Nums = set(nums)
    min_distance = float('inf')
    I = 0
    i = 0

    lins = []
    mode = 1
    for line in lines:
        if i in nums:
            m = 1
            for point in [line['start'], line['end']]:
                dist = distance(point, target_point)
                if dist < min_distance:
                    min_distance = dist
                    closest_point = point
                    mode = m
                    I = i
                m = 0
            
        i += 1
    Nums.remove(I)
    lins.append(I)
    current_start = closest_point
    while Nums:
        fl = True
        for i in Nums:

            if abs(lines[i]['start'][0] - current_start[0]) < 0.5 and abs(lines[i]['start'][1] - current_start[1]) < 0.5:
                lins.append(i)
                
                current_start = lines[i]['end']
                Nums.remove(i)
                fl = False
                break
            elif abs(lines[i]['end'][0] - current_start[0]) < 0.5 and abs(lines[i]['end'][1] - current_start[1]) < 0.5:
                
                lins.append(i)
                current_start = lines[i]['start']
                Nums.remove(i)
                fl = False
                break
        if fl: 
            break


    return closest_point,I,mode,lins

def dxf_to_svg(dxf_file, svg_file): 

    doc = ezdxf.readfile(dxf_file)
    dwg = svgwrite.Drawing(svg_file, profile='tiny')

    for entity in doc.modelspace().query('LINE'):
        start = entity.dxf.start
        end = entity.dxf.end
        dwg.add(dwg.line(start=(start.x, start.y), end=(end.x, end.y), stroke=svgwrite.rgb(0, 0, 0, '%')))

    dwg.save()

def save_dxf():
    global ts
    global lines
    doc = ezdxf.new()
    msp = doc.modelspace()
    set0 = {index for index, value in enumerate(ts) if value == 0}
    set1 = {index for index, value in enumerate(ts) if value == 1}
    set2 = {index for index, value in enumerate(ts) if value == 2}
    set3 = {index for index, value in enumerate(ts) if value == 3}
    set4 = {index for index, value in enumerate(ts) if value == 4}
    sets =[]
    sets.append(set0)
    sets.append(set1)
    sets.append(set2)
    sets.append(set3)
    sets.append(set4)
    
    current_start = (0,0)
    for sett in sets:
        while sett:
            p,j,m = find_closest_pointt(lines,current_start,sett)

            if m:
                msp.add_line(lines[j]['start'], lines[j]['end'])
                current_start = lines[j]['end']
            else:
                msp.add_line(lines[j]['end'], lines[j]['start'])
                current_start = lines[j]['start']

            sett.remove(j)

    doc.saveas('out.dxf')
    test_G_code.dxf_to_gcode('out.dxf','100.gcode')
    #dxf_to_svg('out.dxf','100.svg')
def load_dxf():
        dpg.show_item("file_dialog_id")

def callback(sender, app_data, user_data):
        current_file = app_data['file_path_name']
        plot_dxf(current_file)
def check_callback(sender):
    for i in ['1','2','3','4','5']:
         if i != sender:
              dpg.set_value(i,False)

def plot_mouse_click_callback():
    x,y = dpg.get_plot_mouse_pos()
    p,i,m,l = find_closest_point(lines,(x,y),range(len(lines)))
    global ts
    if dpg.get_value('1'):
        for j in l:
            ts[j] = 0
    elif dpg.get_value('2'):
        for j in l:
            ts[j] = 1
    elif dpg.get_value('3'):
        for j in l:
            ts[j] = 2
    elif dpg.get_value('4'):
        for j in l:
            ts[j] = 3
    elif dpg.get_value('5'):
        for j in l:
            ts[j] = 4
    redraw()
    
def redraw():
    dpg.delete_item(Y_AXIS_TAG, children_only=True, slot=1)

    for i in range(len(lines)):
        start = lines[i]['start']
        end = lines[i]['end']
        
        dpg.add_line_series([start[0], end[0]], [start[1], end[1]],label=f"Line ", parent=Y_AXIS_TAG)
        dpg.bind_item_theme(dpg.last_item(), themes[ts[i]])
def plot_dxf(file_path):
        global lines
        global ts
        lines = read_dxf_lines(file_path)
        ts = [0 for i in range(len(lines))]
        redraw()
           
with dpg.window(pos=(0,0),width=850, height=700):
    with dpg.group(horizontal=True):
        with dpg.group():
            with dpg.file_dialog(directory_selector=False, show=False, callback=callback, id="file_dialog_id", width=700 ,height=400):
                    dpg.add_file_extension("", color=(150, 255, 150, 255))
                    dpg.add_file_extension(".dxf", color=(255, 0, 255, 255), custom_text="[DXF]")
            with dpg.group(horizontal=True):   
                dpg.add_button(label="Load DXF", callback=load_dxf)
                dpg.add_button(label="Save DXF", callback=save_dxf)
            with dpg.plot(label="DXF Plot", width=600, height=600, tag="plot",no_menus=True, no_box_select=True) as plot:
                dpg.add_plot_axis(dpg.mvXAxis, label="X-Axis", tag=X_AXIS_TAG)
                

                yaxis = dpg.add_plot_axis(dpg.mvYAxis, label="Y-Axis", tag=Y_AXIS_TAG)
                dpg.set_axis_limits(Y_AXIS_TAG,-50,300)
                dpg.set_axis_limits(X_AXIS_TAG,-50,300)

            with dpg.group(horizontal=True):
                with dpg.group():
                    dpg.add_checkbox(label="1",tag='1',callback=check_callback)
                    dpg.bind_item_theme(dpg.last_item(), coloured_Core_theme1)
                    dpg.add_input_text(width=50,scientific=True,tag='1_value',default_value='100')
                with dpg.group():
                    dpg.add_checkbox(label="2",tag='2',callback=check_callback)
                    dpg.bind_item_theme(dpg.last_item(), coloured_Core_theme2)
                    dpg.add_input_text(width=50,scientific=True,tag='2_value',default_value='100')
                with dpg.group():
                    dpg.add_checkbox(label="3",tag='3',callback=check_callback)
                    dpg.bind_item_theme(dpg.last_item(), coloured_Core_theme3)
                    dpg.add_input_text(width=50,scientific=True,tag='3_value',default_value='100')
                with dpg.group():
                    dpg.add_checkbox(label="4",tag='4',callback=check_callback)
                    dpg.bind_item_theme(dpg.last_item(), coloured_Core_theme4)
                    dpg.add_input_text(width=50,scientific=True,tag='4_value',default_value='100')
                with dpg.group():
                    dpg.add_checkbox(label="5",tag='5',callback=check_callback)
                    dpg.bind_item_theme(dpg.last_item(), coloured_Core_theme5)
                    dpg.add_input_text(width=50,scientific=True,tag='5_value',default_value='100')

        dpg.add_input_text(multiline=True, label="Input Text", default_value="G00 X5 Y5; point B\nG01 X0 Y20 F200; point C\nG01 X20 Y0; point D\nG02 X10 Y-10 I0 J-10; point E\nG02 X-4 Y-8 I-10 J0; point F\nG01 X-26 Y-2 ; point B\n", tag="multiline_input", readonly=True,width=300)
    
with dpg.item_handler_registry() as registry:
    dpg.add_item_clicked_handler(button=dpg.mvMouseButton_Right, callback=plot_mouse_click_callback)
dpg.bind_item_handler_registry(plot, registry)



dpg.create_viewport(width=900, height=750, title="Plot Update Line Colour")
dpg.setup_dearpygui()
dpg.show_viewport()
dpg.start_dearpygui()
dpg.destroy_context()