import dearpygui.dearpygui as dpg
from fdialog import FileDialog
import optimize

import dearpygui.dearpygui as dpg
import ezdxf
import numpy as np
import math
import svgwrite
import test_G_code
from PIL import Image
import os

def get_state_by_tag(tag):
    global active_obj
    for person in active_obj:
        if person["tag"] == tag:
            return person["bool"]
    return None 
def set_state_by_tag(tag):
    global active_obj
    for person in active_obj:
        
        if person["tag"] == tag:
            state = person["bool"]
            person["bool"] = 0 if state == 1 else 1

    return None 
def active_but(sender,app_data):
    state = get_state_by_tag(sender)
    
    dpg.bind_item_theme(sender, enabled_theme if state else disabled_theme)
    set_state_by_tag(sender)
    redraw()

def arc_to_lines(center, radius, start_angle, end_angle, num_segments):
    start_angle_rad = np.radians(start_angle)
    end_angle_rad = np.radians(end_angle)

    angles = np.linspace(start_angle_rad, end_angle_rad, num_segments + 1)

    points = [(center[0] + radius * np.cos(angle), center[1] + radius * np.sin(angle)) for angle in angles]
    return points
def extract_black_lines(image_path, pixel_distance):
    active_objj = []
    ob = []
    nice_path = os.path.basename(image_path)
    iter = 1
    while 1:
        for i in active_obj:
            if i['tag'] == nice_path:
                nice_path = image_path + f' (copy {iter})'
                iter +=1
        else: 
            break
    
    dpg.add_button(label=os.path.basename(image_path) + f" (copy {iter-1})",parent='butonss',tag=nice_path,callback=active_but)
    active_objj.append({'tag':nice_path,
                       'bool':0})
    
    img = Image.open(image_path).convert('L') 
    img_array = np.array(img)

    height, width = img_array.shape

    liness = []
    tsss = []
    
    for y in range(height):
        start = None
        for x in range(0, width):
            
            if img_array[y, x] < 128:  
                if start is None:
                    start = (x, y) 
            else:
                if start is not None:
                    
                    liness.append({
                    'start': (round(start[0]*pixel_distance,2), round(start[1]*pixel_distance,2)),
                    'end': (round(x*pixel_distance,2), round(y*pixel_distance,2))
                    })
                    
                    tsss.append(0)
                    ob.append(nice_path)
                    
                    start = None
        
        if start is not None:
            liness.append((start, (width - pixel_distance, y)))

    return liness,tsss,active_objj,ob


def calculate_boundary_coordinates(x1, y1, x2, y2, width):
    # Вычисление вектора линии
    dx = x2 - x1
    dy = y2 - y1
    
    # Длина вектора
    d = math.sqrt(dx**2 + dy**2)
    
    # Нормализованный вектор
    if d == 0:
        raise ValueError("Начало и конец линии совпадают")
    
    ux = dx / d
    uy = dy / d
    
    # Перпендикулярный вектор
    nx, ny = -uy, ux  # Поворот на 90 градусов
    
    # Вычисление координат границ
    half_width = width / 2
    
    left_start = (x1 + half_width * nx, y1 + half_width * ny)
    right_start = (x1 - half_width * nx, y1 - half_width * ny)
    
    left_end = (x2 + half_width * nx, y2 + half_width * ny)
    right_end = (x2 - half_width * nx, y2 - half_width * ny)
    
    return {
        "left_start": left_start,
        "right_start": right_start,
        "left_end": left_end,
        "right_end": right_end
    }



def read_dxf_lines_from_esyeda(file_path):
    global active_obj
    

    nice_path = os.path.basename(file_path)
    iter = 1
    while 1:
        for i in active_obj:
            if i['tag'] == nice_path:
                nice_path = file_path + f' (copy {iter})'
                iter +=1
        else: 
            break

    dpg.add_button(label=os.path.basename(file_path) + f" (copy {iter-1})",parent='butonss',tag=nice_path,callback=active_but)
    active_obj.append({'tag':nice_path,
                        'bool':0})
    
    tss = []
    doc = ezdxf.readfile(file_path)
    msp = doc.modelspace()
    lines = []
    objectss = []
    for line in msp.query('LINE'):
        lines.append({
            'start': (line.dxf.start.x, line.dxf.start.y),
            'end': (line.dxf.end.x, line.dxf.end.y)
        })
        tss.append(0)
        objectss.append(nice_path)
    for acdb_line in msp.query('AcDbLine'):
        lines.append({
            'start': (acdb_line.dxf.start.x, acdb_line.dxf.start.y),
            'end': (acdb_line.dxf.end.x, acdb_line.dxf.end.y)
        })
        tss.append(0)
        objectss.append(nice_path)
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
            tss.append(0)
            objectss.append(nice_path)
    for circle in msp.query('CIRCLE'):
        center = circle.dxf.center 
        radius = circle.dxf.radius  
        num_points = 50  

        
        points = [
            (
                center.x + radius * math.cos(2 * math.pi * i / num_points),
                center.y + radius * math.sin(2 * math.pi * i / num_points)
            )
            for i in range(num_points)
        ]

        
        for i in range(len(points)):
            lines.append({
                'start': (points[i][0], points[i][1]),
                'end': (points[(i + 1) % num_points][0], points[(i + 1) % num_points][1])
            })
            tss.append(0)
            objectss.append(nice_path)
    for polyline in msp.query('LWPOLYLINE'):
        w = polyline.dxf.const_width
        
        points = polyline.get_points()  
        for i in range(len(points) - 1):
            boundaries = calculate_boundary_coordinates(points[i][0], points[i][1], points[i + 1][0], points[i + 1][1], w)
            lines.append({
                'start': (points[i][0], points[i][1]),
                'end': (points[i + 1][0], points[i + 1][1])
            })
            tss.append(0)
            objectss.append(nice_path)
            lines.append({
                'start': (boundaries['left_start'][0], boundaries['left_start'][1]),
                'end': (boundaries['left_end'][0],boundaries['left_end'][1])
            })
            tss.append(0)
            objectss.append(nice_path)
            lines.append({
                'start': (boundaries['right_start'][0], boundaries['right_start'][1]),
                'end': (boundaries['right_end'][0],boundaries['right_end'][1])
            })
            tss.append(0)
            objectss.append(nice_path)
    for hatch in msp.query('HATCH'):
        for path in hatch.paths:
        
            points = path.vertices

            lines.append({
                'start': (points[0][0], points[0][1]),
                'end': (points[1][0],points[1][1])
            })
            tss.append(3)
            objectss.append(nice_path)
    return lines,tss,objectss














def read_dxf_lines(file_path):
    global active_obj
    

    nice_path = os.path.basename(file_path)
    iter = 1
    while 1:
        for i in active_obj:
            if i['tag'] == nice_path:
                nice_path = os.path.basename(file_path) + f' (copy {iter})'
                iter +=1
        else: 
            break


    
    dpg.add_button(label=os.path.basename(file_path) + f" (copy {iter-1})",parent='butonss',tag=nice_path,callback=active_but)
    active_obj.append({'tag':nice_path,
                        'bool':0})
    
    tss = []
    doc = ezdxf.readfile(file_path)
    msp = doc.modelspace()
    lines = []
    objectss = []
    for line in msp.query('LINE'):
        lines.append({
            'start': (line.dxf.start.x, line.dxf.start.y),
            'end': (line.dxf.end.x, line.dxf.end.y)
        })
        tss.append(0)
        objectss.append(nice_path)

    
    hlines = []
    for line in msp.query('3DFACE'):
        hlines.append({
            'start': (line.dxf.vtx0[0], line.dxf.vtx0[1]),
            'end': (line.dxf.vtx1[0], line.dxf.vtx1[1])
        })
        
        hlines.append({
            'start': (line.dxf.vtx1[0], line.dxf.vtx1[1]),
            'end': (line.dxf.vtx2[0], line.dxf.vtx2[1])
        })
        
        hlines.append({
            'start': (line.dxf.vtx2[0], line.dxf.vtx2[1]),
            'end': (line.dxf.vtx0[0], line.dxf.vtx0[1])
        })
        
    sett = {i for i in range(len(hlines))}
    settt = []
    while sett:
        found = False
        for i in sett:
            for j in sett:
                if i != j:
                    if (abs(hlines[i]['start'][0] - hlines[j]['start'][0])<0.0001 and abs(hlines[i]['start'][1] - hlines[j]['start'][1])<0.0001 and abs(hlines[i]['end'][0] - hlines[j]['end'][0])<0.0001 and abs(hlines[i]['end'][1] - hlines[j]['end'][1])<0.0001) or (abs(hlines[i]['start'][0] - hlines[j]['end'][0])<0.0001 and abs(hlines[i]['start'][1] - hlines[j]['end'][1])<0.0001 and abs(hlines[j]['start'][0] - hlines[i]['end'][0])<0.0001 and abs(hlines[j]['start'][1] - hlines[i]['end'][1])<0.0001):
                        sett.remove(i)
                        sett.remove(j)
                        found = True
                        break
            if found:
                break
            settt.append(i)
            sett.remove(i)
            break
        
    for i in settt:
        
        lines.append(hlines[i])
        tss.append(0)
        objectss.append(nice_path)


    for acdb_line in msp.query('AcDbLine'):
        lines.append({
            'start': (acdb_line.dxf.start.x, acdb_line.dxf.start.y),
            'end': (acdb_line.dxf.end.x, acdb_line.dxf.end.y)
        })
        tss.append(0)
        objectss.append(nice_path)
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
            tss.append(0)
            objectss.append(nice_path)
    for circle in msp.query('CIRCLE'):
        center = circle.dxf.center 
        radius = circle.dxf.radius  
        num_points = 50  

        
        points = [
            (
                center.x + radius * math.cos(2 * math.pi * i / num_points),
                center.y + radius * math.sin(2 * math.pi * i / num_points)
            )
            for i in range(num_points)
        ]

        
        for i in range(len(points)):
            lines.append({
                'start': (points[i][0], points[i][1]),
                'end': (points[(i + 1) % num_points][0], points[(i + 1) % num_points][1])
            })
            tss.append(0)
            objectss.append(nice_path)
    for polyline in msp.query('LWPOLYLINE'):
        
        points = polyline.get_points()  
        for i in range(len(points) - 1):
            
            lines.append({
                'start': (points[i][0], points[i][1]),
                'end': (points[i + 1][0], points[i + 1][1])
            })
            tss.append(0)
            objectss.append(nice_path)
            
    for hatch in msp.query('HATCH'):
        for path in hatch.paths:
        
            points = path.vertices

            lines.append({
                'start': (points[0][0], points[0][1]),
                'end': (points[1][0],points[1][1])
            })
            tss.append(3)
            objectss.append(nice_path)
    return lines,tss,objectss

def distance(point1, point2):
    return math.sqrt((point1[0] - point2[0]) ** 2 + (point1[1] - point2[1]) ** 2)
def find_closest_pointt(lines, target_point,nums):### возвращает точку, индекс линии, старт (1) или конец(0), и растояние до нее  
    closest_point = None
    min_distance = float('inf')
    I = 0
    
    mode = 1
    for i,line in enumerate(lines):
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
            

    return closest_point,I,mode,min_distance
def find_closest_lines(lines, target_point,nums):
    
    
    Nums = set(nums)
    lins = []

    closest_point,I,mode,min_distance = find_closest_pointt(lines, target_point,Nums)

    current_point = closest_point

    while 1:
        closest_point,I,mode,min_distance = find_closest_pointt(lines, current_point,Nums)

        if min_distance < 1:
            Nums.remove(I)
            lins.append(I)
            if mode:
                current_point = lines[I]['end']
            else:
                current_point = lines[I]['start']
        else:
            return lins

def dxf_to_svg(dxf_file, svg_file): 

    doc = ezdxf.readfile(dxf_file)
    dwg = svgwrite.Drawing(svg_file, profile='tiny')

    for entity in doc.modelspace().query('LINE'):
        start = entity.dxf.start
        end = entity.dxf.end
        dwg.add(dwg.line(start=(start.x, start.y), end=(end.x, end.y), stroke=svgwrite.rgb(0, 0, 0, '%')))
    dwg.save()
def save_as_gcode():
    dpg.show_item("file_dialog_id2")
def callback_to_gcode(sender, app_data, user_data):
    global lines
    global ts


    current_file = app_data['file_path_name']
    gcode_lines = []

    gcode_lines.append("G90")
    gcode_lines.append("M4 S0")
    

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
    h = 1
    for sett in sets:

        power = dpg.get_value(f"{h}_value")
        speed = dpg.get_value(f"{h}1_value")
        while sett:

            p,j,m,d = find_closest_pointt(lines,current_start,sett)
            if abs(current_start[0] - p[0]) > 0.01 or abs(current_start[1] - p[1]) > 0.01:
                gcode_lines.append(f"S0")
                gcode_lines.append(f"G0 X{round(p[0],4)} Y{round(p[1],4)}")         
            if m:
                gcode_lines.append(f"S{speed}")
                gcode_lines.append(f"G1 X{round(lines[j]['end'][0],4)} Y{round(lines[j]['end'][1],4)}F{power}")
                gcode_lines.append(f"S0")

                current_start = lines[j]['end']
            else:
                gcode_lines.append(f"S{speed}")
                gcode_lines.append(f"G1 X{round(lines[j]['start'][0],4)} Y{round(lines[j]['start'][1],4)}F{power}")
                gcode_lines.append(f"S0")
                current_start = lines[j]['start']

            sett.remove(j)
        h+=1
    

    gcode_lines.append(f"M5 S0")
    with open(current_file, 'w') as f:
        f.write("\n".join(gcode_lines))

    dpg.set_value('multiline_input',"\n".join(gcode_lines))

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
            p,j,m,d = find_closest_pointt(lines,current_start,sett)

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
# def load_dxf():
#         dpg.show_item("file_dialog_id")

def check_callback(sender):
    for i in ['1','2','3','4','5']:
         if i != sender:
              dpg.set_value(i,False)

def print_me(sender):
    print(f"Menu Item: {sender}")

digit_lines = {
        '0': [(( 1.8 ,  6.6  ), ( 2.7 , 6.6 )),
(( 1.4 ,  6.5  ), ( 3.0 , 6.5 )),
(( 1.2 ,  6.4  ), ( 3.2 , 6.4 )),
(( 1.1 ,  6.3  ), ( 1.7 , 6.3 )),
(( 2.4 ,  6.3  ), ( 3.3 , 6.3 )),
(( 0.9 ,  6.2  ), ( 1.5 , 6.2 )),
(( 2.6 ,  6.2  ), ( 3.5 , 6.2 )),
(( 0.8 ,  6.1  ), ( 1.4 , 6.1 )),
(( 2.7 ,  6.1  ), ( 3.6 , 6.1 )),
(( 0.7 ,  6.0  ), ( 1.3 , 6.0 )),
(( 2.8 ,  6.0  ), ( 3.7 , 6.0 )),
(( 0.7 ,  5.9  ), ( 1.2 , 5.9 )),
(( 2.9 ,  5.9  ), ( 3.7 , 5.9 )),
(( 0.6 ,  5.8  ), ( 1.2 , 5.8 )),
(( 3.0 ,  5.8  ), ( 3.8 , 5.8 )),
(( 0.5 ,  5.7  ), ( 1.1 , 5.7 )),
(( 3.0 ,  5.7  ), ( 3.8 , 5.7 )),
(( 0.5 ,  5.6  ), ( 1.1 , 5.6 )),
(( 3.1 ,  5.6  ), ( 3.9 , 5.6 )),
(( 0.4 ,  5.5  ), ( 1.1 , 5.5 )),
(( 3.1 ,  5.5  ), ( 3.9 , 5.5 )),
(( 0.4 ,  5.4  ), ( 1.0 , 5.4 )),
(( 3.1 ,  5.4  ), ( 4.0 , 5.4 )),
(( 0.3 ,  5.3  ), ( 1.0 , 5.3 )),
(( 3.2 ,  5.3  ), ( 4.0 , 5.3 )),
(( 0.3 ,  5.2  ), ( 1.0 , 5.2 )),
(( 3.2 ,  5.2  ), ( 4.0 , 5.2 )),
(( 0.2 ,  5.1  ), ( 1.0 , 5.1 )),
(( 3.2 ,  5.1  ), ( 4.1 , 5.1 )),
(( 0.2 ,  5.0  ), ( 0.9 , 5.0 )),
(( 3.2 ,  5.0  ), ( 4.1 , 5.0 )),
(( 0.2 ,  4.9  ), ( 0.9 , 4.9 )),
(( 3.3 ,  4.9  ), ( 4.1 , 4.9 )),
(( 0.2 ,  4.8  ), ( 0.9 , 4.8 )),
(( 3.3 ,  4.8  ), ( 4.1 , 4.8 )),
(( 0.1 ,  4.7  ), ( 0.9 , 4.7 )),
(( 3.3 ,  4.7  ), ( 4.1 , 4.7 )),
(( 0.1 ,  4.6  ), ( 0.9 , 4.6 )),
(( 3.3 ,  4.6  ), ( 4.2 , 4.6 )),
(( 0.1 ,  4.5  ), ( 0.9 , 4.5 )),
(( 3.3 ,  4.5  ), ( 4.2 , 4.5 )),
(( 0.1 ,  4.4  ), ( 0.9 , 4.4 )),
(( 3.3 ,  4.4  ), ( 4.2 , 4.4 )),
(( 0.1 ,  4.3  ), ( 0.9 , 4.3 )),
(( 3.3 ,  4.3  ), ( 4.2 , 4.3 )),
(( 0.1 ,  4.2  ), ( 0.9 , 4.2 )),
(( 3.3 ,  4.2  ), ( 4.2 , 4.2 )),
(( 0.1 ,  4.1  ), ( 0.9 , 4.1 )),
(( 3.4 ,  4.1  ), ( 4.2 , 4.1 )),
(( 0.0 ,  4.0  ), ( 0.8 , 4.0 )),
(( 3.4 ,  4.0  ), ( 4.2 , 4.0 )),
(( 0.0 ,  3.9  ), ( 0.8 , 3.9 )),
(( 3.4 ,  3.9  ), ( 4.2 , 3.9 )),
(( 0.0 ,  3.8  ), ( 0.8 , 3.8 )),
(( 3.4 ,  3.8  ), ( 4.2 , 3.8 )),
(( 0.0 ,  3.7  ), ( 0.8 , 3.7 )),
(( 3.4 ,  3.7  ), ( 4.2 , 3.7 )),
(( 0.0 ,  3.6  ), ( 0.8 , 3.6 )),
(( 3.4 ,  3.6  ), ( 4.2 , 3.6 )),
(( 0.0 ,  3.5  ), ( 0.8 , 3.5 )),
(( 3.4 ,  3.5  ), ( 4.2 , 3.5 )),
(( 0.0 ,  3.4  ), ( 0.8 , 3.4 )),
(( 3.4 ,  3.4  ), ( 4.2 , 3.4 )),
(( 0.0 ,  3.3  ), ( 0.8 , 3.3 )),
(( 3.4 ,  3.3  ), ( 4.2 , 3.3 )),
(( 0.0 ,  3.2  ), ( 0.8 , 3.2 )),
(( 3.4 ,  3.2  ), ( 4.2 , 3.2 )),
(( 0.0 ,  3.1  ), ( 0.8 , 3.1 )),
(( 3.4 ,  3.1  ), ( 4.2 , 3.1 )),
(( 0.0 ,  3.0  ), ( 0.8 , 3.0 )),
(( 3.4 ,  3.0  ), ( 4.2 , 3.0 )),
(( 0.0 ,  2.9  ), ( 0.8 , 2.9 )),
(( 3.4 ,  2.9  ), ( 4.2 , 2.9 )),
(( 0.0 ,  2.8  ), ( 0.9 , 2.8 )),
(( 3.4 ,  2.8  ), ( 4.2 , 2.8 )),
(( 0.0 ,  2.7  ), ( 0.9 , 2.7 )),
(( 3.4 ,  2.7  ), ( 4.2 , 2.7 )),
(( 0.0 ,  2.6  ), ( 0.9 , 2.6 )),
(( 3.4 ,  2.6  ), ( 4.2 , 2.6 )),
(( 0.0 ,  2.5  ), ( 0.9 , 2.5 )),
(( 3.4 ,  2.5  ), ( 4.1 , 2.5 )),
(( 0.0 ,  2.4  ), ( 0.9 , 2.4 )),
(( 3.4 ,  2.4  ), ( 4.1 , 2.4 )),
(( 0.1 ,  2.3  ), ( 0.9 , 2.3 )),
(( 3.4 ,  2.3  ), ( 4.1 , 2.3 )),
(( 0.1 ,  2.2  ), ( 0.9 , 2.2 )),
(( 3.3 ,  2.2  ), ( 4.1 , 2.2 )),
(( 0.1 ,  2.1  ), ( 0.9 , 2.1 )),
(( 3.3 ,  2.1  ), ( 4.1 , 2.1 )),
(( 0.1 ,  2.0  ), ( 0.9 , 2.0 )),
(( 3.3 ,  2.0  ), ( 4.1 , 2.0 )),
(( 0.1 ,  1.9  ), ( 0.9 , 1.9 )),
(( 3.3 ,  1.9  ), ( 4.0 , 1.9 )),
(( 0.1 ,  1.8  ), ( 0.9 , 1.8 )),
(( 3.3 ,  1.8  ), ( 4.0 , 1.8 )),
(( 0.1 ,  1.7  ), ( 1.0 , 1.7 )),
(( 3.3 ,  1.7  ), ( 4.0 , 1.7 )),
(( 0.1 ,  1.6  ), ( 1.0 , 1.6 )),
(( 3.3 ,  1.6  ), ( 4.0 , 1.6 )),
(( 0.2 ,  1.5  ), ( 1.0 , 1.5 )),
(( 3.3 ,  1.5  ), ( 3.9 , 1.5 )),
(( 0.2 ,  1.4  ), ( 1.0 , 1.4 )),
(( 3.2 ,  1.4  ), ( 3.9 , 1.4 )),
(( 0.2 ,  1.3  ), ( 1.0 , 1.3 )),
(( 3.2 ,  1.3  ), ( 3.9 , 1.3 )),
(( 0.3 ,  1.2  ), ( 1.1 , 1.2 )),
(( 3.2 ,  1.2  ), ( 3.8 , 1.2 )),
(( 0.3 ,  1.1  ), ( 1.1 , 1.1 )),
(( 3.2 ,  1.1  ), ( 3.8 , 1.1 )),
(( 0.4 ,  1.0  ), ( 1.2 , 1.0 )),
(( 3.1 ,  1.0  ), ( 3.7 , 1.0 )),
(( 0.4 ,  0.9  ), ( 1.2 , 0.9 )),
(( 3.1 ,  0.9  ), ( 3.7 , 0.9 )),
(( 0.5 ,  0.8  ), ( 1.2 , 0.8 )),
(( 3.0 ,  0.8  ), ( 3.6 , 0.8 )),
(( 0.5 ,  0.7  ), ( 1.3 , 0.7 )),
(( 3.0 ,  0.7  ), ( 3.5 , 0.7 )),
(( 0.6 ,  0.6  ), ( 1.4 , 0.6 )),
(( 2.9 ,  0.6  ), ( 3.5 , 0.6 )),
(( 0.7 ,  0.5  ), ( 1.5 , 0.5 )),
(( 2.8 ,  0.5  ), ( 3.4 , 0.5 )),
(( 0.8 ,  0.4  ), ( 1.6 , 0.4 )),
(( 2.7 ,  0.4  ), ( 3.3 , 0.4 )),
(( 0.9 ,  0.3  ), ( 1.8 , 0.3 )),
(( 2.5 ,  0.3  ), ( 3.1 , 0.3 )),
(( 1.1 ,  0.2  ), ( 3.0 , 0.2 )),
(( 1.2 ,  0.1  ), ( 2.8 , 0.1 )),
(( 1.6 ,  0.0  ), ( 2.4 , 0.0 ))],
        '1': [(( 2.4 ,  6.5  ), ( 2.6 , 6.5 )),
(( 2.2 ,  6.4  ), ( 2.7 , 6.4 )),
(( 2.0 ,  6.3  ), ( 2.7 , 6.3 )),
(( 1.8 ,  6.2  ), ( 2.7 , 6.2 )),
(( 1.5 ,  6.1  ), ( 2.7 , 6.1 )),
(( 1.3 ,  6.0  ), ( 2.6 , 6.0 )),
(( 1.0 ,  5.9  ), ( 2.6 , 5.9 )),
(( 0.7 ,  5.8  ), ( 2.6 , 5.8 )),
(( 0.4 ,  5.7  ), ( 1.5 , 5.7 )),
(( 1.7 ,  5.7  ), ( 2.6 , 5.7 )),
(( 0.1 ,  5.6  ), ( 1.3 , 5.6 )),
(( 1.8 ,  5.6  ), ( 2.6 , 5.6 )),
(( 0.0 ,  5.5  ), ( 1.0 , 5.5 )),
(( 1.8 ,  5.5  ), ( 2.6 , 5.5 )),
(( 0.0 ,  5.4  ), ( 0.8 , 5.4 )),
(( 1.8 ,  5.4  ), ( 2.6 , 5.4 )),
(( 0.0 ,  5.3  ), ( 0.6 , 5.3 )),
(( 1.8 ,  5.3  ), ( 2.6 , 5.3 )),
(( 0.0 ,  5.2  ), ( 0.4 , 5.2 )),
(( 1.8 ,  5.2  ), ( 2.6 , 5.2 )),
(( 0.1 ,  5.1  ), ( 0.2 , 5.1 )),
(( 1.8 ,  5.1  ), ( 2.6 , 5.1 )),
(( 1.8 ,  5.0  ), ( 2.6 , 5.0 )),
(( 1.8 ,  4.9  ), ( 2.6 , 4.9 )),
(( 1.8 ,  4.8  ), ( 2.6 , 4.8 )),
(( 1.8 ,  4.7  ), ( 2.6 , 4.7 )),
(( 1.8 ,  4.6  ), ( 2.6 , 4.6 )),
(( 1.8 ,  4.5  ), ( 2.6 , 4.5 )),
(( 1.8 ,  4.4  ), ( 2.6 , 4.4 )),
(( 1.8 ,  4.3  ), ( 2.6 , 4.3 )),
(( 1.8 ,  4.2  ), ( 2.6 , 4.2 )),
(( 1.8 ,  4.1  ), ( 2.6 , 4.1 )),
(( 1.8 ,  4.0  ), ( 2.6 , 4.0 )),
(( 1.8 ,  3.9  ), ( 2.6 , 3.9 )),
(( 1.8 ,  3.8  ), ( 2.6 , 3.8 )),
(( 1.8 ,  3.7  ), ( 2.6 , 3.7 )),
(( 1.8 ,  3.6  ), ( 2.6 , 3.6 )),
(( 1.8 ,  3.5  ), ( 2.6 , 3.5 )),
(( 1.8 ,  3.4  ), ( 2.6 , 3.4 )),
(( 1.8 ,  3.3  ), ( 2.6 , 3.3 )),
(( 1.8 ,  3.2  ), ( 2.6 , 3.2 )),
(( 1.8 ,  3.1  ), ( 2.6 , 3.1 )),
(( 1.8 ,  3.0  ), ( 2.6 , 3.0 )),
(( 1.8 ,  2.9  ), ( 2.6 , 2.9 )),
(( 1.8 ,  2.8  ), ( 2.6 , 2.8 )),
(( 1.8 ,  2.7  ), ( 2.6 , 2.7 )),
(( 1.8 ,  2.6  ), ( 2.6 , 2.6 )),
(( 1.8 ,  2.5  ), ( 2.6 , 2.5 )),
(( 1.8 ,  2.4  ), ( 2.6 , 2.4 )),
(( 1.8 ,  2.3  ), ( 2.6 , 2.3 )),
(( 1.8 ,  2.2  ), ( 2.6 , 2.2 )),
(( 1.8 ,  2.1  ), ( 2.6 , 2.1 )),
(( 1.7 ,  2.0  ), ( 2.6 , 2.0 )),
(( 1.7 ,  1.9  ), ( 2.6 , 1.9 )),
(( 1.7 ,  1.8  ), ( 2.6 , 1.8 )),
(( 1.7 ,  1.7  ), ( 2.6 , 1.7 )),
(( 1.7 ,  1.6  ), ( 2.6 , 1.6 )),
(( 1.7 ,  1.5  ), ( 2.6 , 1.5 )),
(( 1.7 ,  1.4  ), ( 2.6 , 1.4 )),
(( 1.7 ,  1.3  ), ( 2.6 , 1.3 )),
(( 1.7 ,  1.2  ), ( 2.6 , 1.2 )),
(( 1.7 ,  1.1  ), ( 2.6 , 1.1 )),
(( 1.7 ,  1.0  ), ( 2.6 , 1.0 )),
(( 1.7 ,  0.9  ), ( 2.6 , 0.9 )),
(( 1.7 ,  0.8  ), ( 2.6 , 0.8 )),
(( 1.7 ,  0.7  ), ( 2.6 , 0.7 )),
(( 1.7 ,  0.6  ), ( 2.6 , 0.6 )),
(( 1.7 ,  0.5  ), ( 2.7 , 0.5 )),
(( 1.6 ,  0.4  ), ( 2.7 , 0.4 )),
(( 1.3 ,  0.3  ), ( 2.9 , 0.3 )),
(( 0.5 ,  0.2  ), ( 3.8 , 0.2 )),
(( 0.5 ,  0.1  ), ( 3.8 , 0.1 )),
(( 0.5 ,  0.0  ), ( 3.8 , 0.0 ))],
        '2': [(( 1.6 ,  6.5  ), ( 2.6 , 6.5 )),
(( 1.2 ,  6.4  ), ( 2.9 , 6.4 )),
(( 1.0 ,  6.3  ), ( 3.2 , 6.3 )),
(( 0.8 ,  6.2  ), ( 3.3 , 6.2 )),
(( 0.7 ,  6.1  ), ( 3.5 , 6.1 )),
(( 0.6 ,  6.0  ), ( 3.6 , 6.0 )),
(( 0.5 ,  5.9  ), ( 3.7 , 5.9 )),
(( 0.4 ,  5.8  ), ( 3.7 , 5.8 )),
(( 0.4 ,  5.7  ), ( 1.4 , 5.7 )),
(( 2.3 ,  5.7  ), ( 3.8 , 5.7 )),
(( 0.4 ,  5.6  ), ( 1.1 , 5.6 )),
(( 2.5 ,  5.6  ), ( 3.9 , 5.6 )),
(( 0.4 ,  5.5  ), ( 1.0 , 5.5 )),
(( 2.7 ,  5.5  ), ( 3.9 , 5.5 )),
(( 0.4 ,  5.4  ), ( 0.8 , 5.4 )),
(( 2.8 ,  5.4  ), ( 4.0 , 5.4 )),
(( 0.3 ,  5.3  ), ( 0.8 , 5.3 )),
(( 2.9 ,  5.3  ), ( 4.0 , 5.3 )),
(( 0.3 ,  5.2  ), ( 0.7 , 5.2 )),
(( 3.0 ,  5.2  ), ( 4.0 , 5.2 )),
(( 0.3 ,  5.1  ), ( 0.7 , 5.1 )),
(( 3.0 ,  5.1  ), ( 4.0 , 5.1 )),
(( 0.3 ,  5.0  ), ( 0.7 , 5.0 )),
(( 3.1 ,  5.0  ), ( 4.0 , 5.0 )),
(( 0.3 ,  4.9  ), ( 0.6 , 4.9 )),
(( 3.1 ,  4.9  ), ( 4.1 , 4.9 )),
(( 0.3 ,  4.8  ), ( 0.6 , 4.8 )),
(( 3.1 ,  4.8  ), ( 4.1 , 4.8 )),
(( 0.3 ,  4.7  ), ( 0.6 , 4.7 )),
(( 3.1 ,  4.7  ), ( 4.1 , 4.7 )),
(( 0.3 ,  4.6  ), ( 0.6 , 4.6 )),
(( 3.2 ,  4.6  ), ( 4.1 , 4.6 )),
(( 0.2 ,  4.5  ), ( 0.5 , 4.5 )),
(( 3.2 ,  4.5  ), ( 4.0 , 4.5 )),
(( 3.2 ,  4.4  ), ( 4.0 , 4.4 )),
(( 3.2 ,  4.3  ), ( 4.0 , 4.3 )),
(( 3.2 ,  4.2  ), ( 4.0 , 4.2 )),
(( 3.1 ,  4.1  ), ( 4.0 , 4.1 )),
(( 3.1 ,  4.0  ), ( 3.9 , 4.0 )),
(( 3.1 ,  3.9  ), ( 3.9 , 3.9 )),
(( 3.1 ,  3.8  ), ( 3.8 , 3.8 )),
(( 3.0 ,  3.7  ), ( 3.8 , 3.7 )),
(( 3.0 ,  3.6  ), ( 3.7 , 3.6 )),
(( 2.9 ,  3.5  ), ( 3.7 , 3.5 )),
(( 2.9 ,  3.4  ), ( 3.6 , 3.4 )),
(( 2.8 ,  3.3  ), ( 3.5 , 3.3 )),
(( 2.8 ,  3.2  ), ( 3.5 , 3.2 )),
(( 2.7 ,  3.1  ), ( 3.4 , 3.1 )),
(( 2.6 ,  3.0  ), ( 3.3 , 3.0 )),
(( 2.6 ,  2.9  ), ( 3.2 , 2.9 )),
(( 2.5 ,  2.8  ), ( 3.1 , 2.8 )),
(( 2.4 ,  2.7  ), ( 3.0 , 2.7 )),
(( 2.3 ,  2.6  ), ( 2.9 , 2.6 )),
(( 2.2 ,  2.5  ), ( 2.8 , 2.5 )),
(( 2.1 ,  2.4  ), ( 2.7 , 2.4 )),
(( 2.1 ,  2.3  ), ( 2.6 , 2.3 )),
(( 2.0 ,  2.2  ), ( 2.5 , 2.2 )),
(( 1.9 ,  2.1  ), ( 2.4 , 2.1 )),
(( 1.8 ,  2.0  ), ( 2.3 , 2.0 )),
(( 1.7 ,  1.9  ), ( 2.2 , 1.9 )),
(( 1.6 ,  1.8  ), ( 2.1 , 1.8 )),
(( 1.5 ,  1.7  ), ( 2.0 , 1.7 )),
(( 1.4 ,  1.6  ), ( 1.9 , 1.6 )),
(( 1.3 ,  1.5  ), ( 1.8 , 1.5 )),
(( 1.2 ,  1.4  ), ( 1.7 , 1.4 )),
(( 1.1 ,  1.3  ), ( 1.6 , 1.3 )),
(( 1.0 ,  1.2  ), ( 1.5 , 1.2 )),
(( 0.9 ,  1.1  ), ( 1.4 , 1.1 )),
(( 0.8 ,  1.0  ), ( 1.3 , 1.0 )),
(( 0.7 ,  0.9  ), ( 1.2 , 0.9 )),
(( 0.6 ,  0.8  ), ( 1.1 , 0.8 )),
(( 4.0 ,  0.8  ), ( 4.4 , 0.8 )),
(( 0.5 ,  0.7  ), ( 4.4 , 0.7 )),
(( 0.4 ,  0.6  ), ( 4.4 , 0.6 )),
(( 0.3 ,  0.5  ), ( 4.4 , 0.5 )),
(( 0.2 ,  0.4  ), ( 4.4 , 0.4 )),
(( 0.1 ,  0.3  ), ( 4.4 , 0.3 )),
(( 0.0 ,  0.2  ), ( 4.4 , 0.2 )),
(( 0.0 ,  0.1  ), ( 4.4 , 0.1 )),
(( 0.0 ,  0.0  ), ( 4.4 , 0.0 ))],
        '3': [(( 1.5 ,  6.6  ), ( 2.5 , 6.6 )),
(( 1.2 ,  6.5  ), ( 2.8 , 6.5 )),
(( 1.0 ,  6.4  ), ( 3.0 , 6.4 )),
(( 0.8 ,  6.3  ), ( 3.2 , 6.3 )),
(( 0.7 ,  6.2  ), ( 3.3 , 6.2 )),
(( 0.6 ,  6.1  ), ( 3.4 , 6.1 )),
(( 0.5 ,  6.0  ), ( 3.5 , 6.0 )),
(( 0.4 ,  5.9  ), ( 1.4 , 5.9 )),
(( 2.2 ,  5.9  ), ( 3.5 , 5.9 )),
(( 0.3 ,  5.8  ), ( 1.1 , 5.8 )),
(( 2.4 ,  5.8  ), ( 3.6 , 5.8 )),
(( 0.3 ,  5.7  ), ( 1.0 , 5.7 )),
(( 2.5 ,  5.7  ), ( 3.6 , 5.7 )),
(( 0.3 ,  5.6  ), ( 0.9 , 5.6 )),
(( 2.6 ,  5.6  ), ( 3.7 , 5.6 )),
(( 0.3 ,  5.5  ), ( 0.8 , 5.5 )),
(( 2.7 ,  5.5  ), ( 3.7 , 5.5 )),
(( 0.3 ,  5.4  ), ( 0.7 , 5.4 )),
(( 2.8 ,  5.4  ), ( 3.7 , 5.4 )),
(( 0.2 ,  5.3  ), ( 0.6 , 5.3 )),
(( 2.8 ,  5.3  ), ( 3.7 , 5.3 )),
(( 0.2 ,  5.2  ), ( 0.6 , 5.2 )),
(( 2.9 ,  5.2  ), ( 3.7 , 5.2 )),
(( 0.2 ,  5.1  ), ( 0.5 , 5.1 )),
(( 2.9 ,  5.1  ), ( 3.7 , 5.1 )),
(( 0.2 ,  5.0  ), ( 0.5 , 5.0 )),
(( 2.9 ,  5.0  ), ( 3.7 , 5.0 )),
(( 0.2 ,  4.9  ), ( 0.5 , 4.9 )),
(( 2.9 ,  4.9  ), ( 3.7 , 4.9 )),
(( 0.2 ,  4.8  ), ( 0.5 , 4.8 )),
(( 2.9 ,  4.8  ), ( 3.6 , 4.8 )),
(( 0.1 ,  4.7  ), ( 0.4 , 4.7 )),
(( 2.9 ,  4.7  ), ( 3.6 , 4.7 )),
(( 0.1 ,  4.6  ), ( 0.4 , 4.6 )),
(( 2.9 ,  4.6  ), ( 3.6 , 4.6 )),
(( 2.9 ,  4.5  ), ( 3.5 , 4.5 )),
(( 2.9 ,  4.4  ), ( 3.4 , 4.4 )),
(( 2.8 ,  4.3  ), ( 3.4 , 4.3 )),
(( 2.8 ,  4.2  ), ( 3.3 , 4.2 )),
(( 2.7 ,  4.1  ), ( 3.2 , 4.1 )),
(( 2.6 ,  4.0  ), ( 3.1 , 4.0 )),
(( 2.6 ,  3.9  ), ( 3.0 , 3.9 )),
(( 2.4 ,  3.8  ), ( 2.9 , 3.8 )),
(( 2.3 ,  3.7  ), ( 2.8 , 3.7 )),
(( 2.0 ,  3.6  ), ( 3.1 , 3.6 )),
(( 1.2 ,  3.5  ), ( 3.4 , 3.5 )),
(( 1.2 ,  3.4  ), ( 3.6 , 3.4 )),
(( 1.2 ,  3.3  ), ( 3.8 , 3.3 )),
(( 1.2 ,  3.2  ), ( 1.6 , 3.2 )),
(( 2.5 ,  3.2  ), ( 3.9 , 3.2 )),
(( 1.2 ,  3.1  ), ( 1.3 , 3.1 )),
(( 2.7 ,  3.1  ), ( 4.0 , 3.1 )),
(( 2.9 ,  3.0  ), ( 4.0 , 3.0 )),
(( 3.0 ,  2.9  ), ( 4.1 , 2.9 )),
(( 3.1 ,  2.8  ), ( 4.1 , 2.8 )),
(( 3.1 ,  2.7  ), ( 4.2 , 2.7 )),
(( 3.2 ,  2.6  ), ( 4.2 , 2.6 )),
(( 3.2 ,  2.5  ), ( 4.2 , 2.5 )),
(( 3.3 ,  2.4  ), ( 4.2 , 2.4 )),
(( 3.3 ,  2.3  ), ( 4.2 , 2.3 )),
(( 3.3 ,  2.2  ), ( 4.2 , 2.2 )),
(( 3.3 ,  2.1  ), ( 4.2 , 2.1 )),
(( 3.3 ,  2.0  ), ( 4.2 , 2.0 )),
(( 3.3 ,  1.9  ), ( 4.2 , 1.9 )),
(( 3.3 ,  1.8  ), ( 4.2 , 1.8 )),
(( 3.3 ,  1.7  ), ( 4.1 , 1.7 )),
(( 0.1 ,  1.6  ), ( 0.2 , 1.6 )),
(( 3.3 ,  1.6  ), ( 4.1 , 1.6 )),
(( 0.0 ,  1.5  ), ( 0.3 , 1.5 )),
(( 3.3 ,  1.5  ), ( 4.0 , 1.5 )),
(( 0.0 ,  1.4  ), ( 0.3 , 1.4 )),
(( 3.3 ,  1.4  ), ( 4.0 , 1.4 )),
(( 0.0 ,  1.3  ), ( 0.3 , 1.3 )),
(( 3.3 ,  1.3  ), ( 3.9 , 1.3 )),
(( 0.1 ,  1.2  ), ( 0.4 , 1.2 )),
(( 3.2 ,  1.2  ), ( 3.9 , 1.2 )),
(( 0.1 ,  1.1  ), ( 0.4 , 1.1 )),
(( 3.2 ,  1.1  ), ( 3.8 , 1.1 )),
(( 0.1 ,  1.0  ), ( 0.5 , 1.0 )),
(( 3.2 ,  1.0  ), ( 3.7 , 1.0 )),
(( 0.1 ,  0.9  ), ( 0.6 , 0.9 )),
(( 3.1 ,  0.9  ), ( 3.6 , 0.9 )),
(( 0.2 ,  0.8  ), ( 0.6 , 0.8 )),
(( 3.0 ,  0.8  ), ( 3.5 , 0.8 )),
(( 0.2 ,  0.7  ), ( 0.7 , 0.7 )),
(( 3.0 ,  0.7  ), ( 3.4 , 0.7 )),
(( 0.2 ,  0.6  ), ( 0.8 , 0.6 )),
(( 2.9 ,  0.6  ), ( 3.3 , 0.6 )),
(( 0.3 ,  0.5  ), ( 0.9 , 0.5 )),
(( 2.7 ,  0.5  ), ( 3.2 , 0.5 )),
(( 0.3 ,  0.4  ), ( 1.1 , 0.4 )),
(( 2.6 ,  0.4  ), ( 3.0 , 0.4 )),
(( 0.3 ,  0.3  ), ( 1.3 , 0.3 )),
(( 2.3 ,  0.3  ), ( 2.9 , 0.3 )),
(( 0.3 ,  0.2  ), ( 2.7 , 0.2 )),
(( 0.6 ,  0.1  ), ( 2.4 , 0.1 )),
(( 1.0 ,  0.0  ), ( 2.0 , 0.0 ))],
        '4': [(( 3.3 ,  6.5  ), ( 3.5 , 6.5 )),
(( 3.0 ,  6.4  ), ( 3.5 , 6.4 )),
(( 2.8 ,  6.3  ), ( 3.5 , 6.3 )),
(( 2.7 ,  6.2  ), ( 3.5 , 6.2 )),
(( 2.6 ,  6.1  ), ( 3.5 , 6.1 )),
(( 2.5 ,  6.0  ), ( 3.5 , 6.0 )),
(( 2.5 ,  5.9  ), ( 3.5 , 5.9 )),
(( 2.4 ,  5.8  ), ( 3.5 , 5.8 )),
(( 2.3 ,  5.7  ), ( 3.5 , 5.7 )),
(( 2.3 ,  5.6  ), ( 3.5 , 5.6 )),
(( 2.2 ,  5.5  ), ( 3.5 , 5.5 )),
(( 2.1 ,  5.4  ), ( 2.6 , 5.4 )),
(( 2.7 ,  5.4  ), ( 3.5 , 5.4 )),
(( 2.1 ,  5.3  ), ( 2.5 , 5.3 )),
(( 2.7 ,  5.3  ), ( 3.5 , 5.3 )),
(( 2.0 ,  5.2  ), ( 2.4 , 5.2 )),
(( 2.7 ,  5.2  ), ( 3.5 , 5.2 )),
(( 1.9 ,  5.1  ), ( 2.3 , 5.1 )),
(( 2.7 ,  5.1  ), ( 3.5 , 5.1 )),
(( 1.9 ,  5.0  ), ( 2.3 , 5.0 )),
(( 2.7 ,  5.0  ), ( 3.5 , 5.0 )),
(( 1.8 ,  4.9  ), ( 2.2 , 4.9 )),
(( 2.7 ,  4.9  ), ( 3.5 , 4.9 )),
(( 1.8 ,  4.8  ), ( 2.2 , 4.8 )),
(( 2.7 ,  4.8  ), ( 3.5 , 4.8 )),
(( 1.7 ,  4.7  ), ( 2.1 , 4.7 )),
(( 2.7 ,  4.7  ), ( 3.5 , 4.7 )),
(( 1.6 ,  4.6  ), ( 2.0 , 4.6 )),
(( 2.7 ,  4.6  ), ( 3.5 , 4.6 )),
(( 1.6 ,  4.5  ), ( 2.0 , 4.5 )),
(( 2.7 ,  4.5  ), ( 3.5 , 4.5 )),
(( 1.5 ,  4.4  ), ( 1.9 , 4.4 )),
(( 2.7 ,  4.4  ), ( 3.5 , 4.4 )),
(( 1.4 ,  4.3  ), ( 1.8 , 4.3 )),
(( 2.7 ,  4.3  ), ( 3.5 , 4.3 )),
(( 1.4 ,  4.2  ), ( 1.8 , 4.2 )),
(( 2.7 ,  4.2  ), ( 3.5 , 4.2 )),
(( 1.3 ,  4.1  ), ( 1.7 , 4.1 )),
(( 2.7 ,  4.1  ), ( 3.5 , 4.1 )),
(( 1.3 ,  4.0  ), ( 1.7 , 4.0 )),
(( 2.7 ,  4.0  ), ( 3.5 , 4.0 )),
(( 1.2 ,  3.9  ), ( 1.6 , 3.9 )),
(( 2.7 ,  3.9  ), ( 3.5 , 3.9 )),
(( 1.1 ,  3.8  ), ( 1.5 , 3.8 )),
(( 2.7 ,  3.8  ), ( 3.5 , 3.8 )),
(( 1.1 ,  3.7  ), ( 1.5 , 3.7 )),
(( 2.7 ,  3.7  ), ( 3.5 , 3.7 )),
(( 1.0 ,  3.6  ), ( 1.4 , 3.6 )),
(( 2.7 ,  3.6  ), ( 3.5 , 3.6 )),
(( 1.0 ,  3.5  ), ( 1.4 , 3.5 )),
(( 2.7 ,  3.5  ), ( 3.5 , 3.5 )),
(( 0.9 ,  3.4  ), ( 1.3 , 3.4 )),
(( 2.7 ,  3.4  ), ( 3.5 , 3.4 )),
(( 0.8 ,  3.3  ), ( 1.2 , 3.3 )),
(( 2.7 ,  3.3  ), ( 3.5 , 3.3 )),
(( 0.8 ,  3.2  ), ( 1.2 , 3.2 )),
(( 2.7 ,  3.2  ), ( 3.5 , 3.2 )),
(( 0.7 ,  3.1  ), ( 1.1 , 3.1 )),
(( 2.7 ,  3.1  ), ( 3.5 , 3.1 )),
(( 0.7 ,  3.0  ), ( 1.1 , 3.0 )),
(( 2.7 ,  3.0  ), ( 3.5 , 3.0 )),
(( 0.6 ,  2.9  ), ( 1.0 , 2.9 )),
(( 2.7 ,  2.9  ), ( 3.5 , 2.9 )),
(( 0.5 ,  2.8  ), ( 1.0 , 2.8 )),
(( 2.7 ,  2.8  ), ( 3.5 , 2.8 )),
(( 0.5 ,  2.7  ), ( 0.9 , 2.7 )),
(( 2.7 ,  2.7  ), ( 3.5 , 2.7 )),
(( 0.4 ,  2.6  ), ( 0.8 , 2.6 )),
(( 2.7 ,  2.6  ), ( 3.5 , 2.6 )),
(( 0.4 ,  2.5  ), ( 0.8 , 2.5 )),
(( 2.7 ,  2.5  ), ( 3.5 , 2.5 )),
(( 0.3 ,  2.4  ), ( 0.7 , 2.4 )),
(( 2.7 ,  2.4  ), ( 3.5 , 2.4 )),
(( 0.3 ,  2.3  ), ( 0.7 , 2.3 )),
(( 2.7 ,  2.3  ), ( 3.5 , 2.3 )),
(( 0.2 ,  2.2  ), ( 4.5 , 2.2 )),
(( 0.1 ,  2.1  ), ( 4.5 , 2.1 )),
(( 0.1 ,  2.0  ), ( 4.5 , 2.0 )),
(( 0.0 ,  1.9  ), ( 4.5 , 1.9 )),
(( 0.1 ,  1.8  ), ( 4.5 , 1.8 )),
(( 0.1 ,  1.7  ), ( 4.5 , 1.7 )),
(( 2.7 ,  1.6  ), ( 3.5 , 1.6 )),
(( 2.7 ,  1.5  ), ( 3.5 , 1.5 )),
(( 2.7 ,  1.4  ), ( 3.5 , 1.4 )),
(( 2.7 ,  1.3  ), ( 3.5 , 1.3 )),
(( 2.7 ,  1.2  ), ( 3.5 , 1.2 )),
(( 2.7 ,  1.1  ), ( 3.5 , 1.1 )),
(( 2.6 ,  1.0  ), ( 3.5 , 1.0 )),
(( 2.6 ,  0.9  ), ( 3.5 , 0.9 )),
(( 2.6 ,  0.8  ), ( 3.5 , 0.8 )),
(( 2.6 ,  0.7  ), ( 3.5 , 0.7 )),
(( 2.6 ,  0.6  ), ( 3.5 , 0.6 )),
(( 2.6 ,  0.5  ), ( 3.5 , 0.5 )),
(( 2.5 ,  0.4  ), ( 3.6 , 0.4 )),
(( 2.2 ,  0.3  ), ( 3.8 , 0.3 )),
(( 1.5 ,  0.2  ), ( 4.5 , 0.2 )),
(( 1.5 ,  0.1  ), ( 4.5 , 0.1 )),
(( 1.5 ,  0.0  ), ( 4.5 , 0.0 ))],
        '5': [(( 0.6 ,  6.6  ), ( 1.1 , 6.6 )),
(( 3.5 ,  6.6  ), ( 4.0 , 6.6 )),
(( 0.6 ,  6.5  ), ( 4.0 , 6.5 )),
(( 0.6 ,  6.4  ), ( 4.0 , 6.4 )),
(( 0.6 ,  6.3  ), ( 4.0 , 6.3 )),
(( 0.6 ,  6.2  ), ( 4.0 , 6.2 )),
(( 0.7 ,  6.1  ), ( 4.0 , 6.1 )),
(( 0.7 ,  6.0  ), ( 4.0 , 6.0 )),
(( 0.7 ,  5.9  ), ( 4.0 , 5.9 )),
(( 0.7 ,  5.8  ), ( 1.1 , 5.8 )),
(( 0.7 ,  5.7  ), ( 1.1 , 5.7 )),
(( 0.7 ,  5.6  ), ( 1.1 , 5.6 )),
(( 0.7 ,  5.5  ), ( 1.1 , 5.5 )),
(( 0.7 ,  5.4  ), ( 1.0 , 5.4 )),
(( 0.7 ,  5.3  ), ( 1.0 , 5.3 )),
(( 0.7 ,  5.2  ), ( 1.0 , 5.2 )),
(( 0.7 ,  5.1  ), ( 1.0 , 5.1 )),
(( 0.7 ,  5.0  ), ( 1.0 , 5.0 )),
(( 0.7 ,  4.9  ), ( 1.0 , 4.9 )),
(( 0.7 ,  4.8  ), ( 1.0 , 4.8 )),
(( 0.7 ,  4.7  ), ( 1.0 , 4.7 )),
(( 0.7 ,  4.6  ), ( 1.0 , 4.6 )),
(( 0.7 ,  4.5  ), ( 1.0 , 4.5 )),
(( 0.7 ,  4.4  ), ( 1.0 , 4.4 )),
(( 1.9 ,  4.4  ), ( 2.9 , 4.4 )),
(( 0.7 ,  4.3  ), ( 1.0 , 4.3 )),
(( 1.6 ,  4.3  ), ( 3.2 , 4.3 )),
(( 0.7 ,  4.2  ), ( 1.0 , 4.2 )),
(( 1.4 ,  4.2  ), ( 3.4 , 4.2 )),
(( 0.7 ,  4.1  ), ( 1.0 , 4.1 )),
(( 1.2 ,  4.1  ), ( 3.6 , 4.1 )),
(( 0.7 ,  4.0  ), ( 1.0 , 4.0 )),
(( 1.1 ,  4.0  ), ( 3.7 , 4.0 )),
(( 0.7 ,  3.9  ), ( 3.8 , 3.9 )),
(( 0.6 ,  3.8  ), ( 3.9 , 3.8 )),
(( 0.6 ,  3.7  ), ( 1.6 , 3.7 )),
(( 2.5 ,  3.7  ), ( 4.0 , 3.7 )),
(( 0.6 ,  3.6  ), ( 1.3 , 3.6 )),
(( 2.8 ,  3.6  ), ( 4.1 , 3.6 )),
(( 0.6 ,  3.5  ), ( 1.2 , 3.5 )),
(( 2.9 ,  3.5  ), ( 4.1 , 3.5 )),
(( 0.6 ,  3.4  ), ( 1.0 , 3.4 )),
(( 3.0 ,  3.4  ), ( 4.2 , 3.4 )),
(( 0.6 ,  3.3  ), ( 0.9 , 3.3 )),
(( 3.2 ,  3.3  ), ( 4.2 , 3.3 )),
(( 0.7 ,  3.2  ), ( 0.8 , 3.2 )),
(( 3.2 ,  3.2  ), ( 4.2 , 3.2 )),
(( 3.3 ,  3.1  ), ( 4.3 , 3.1 )),
(( 3.4 ,  3.0  ), ( 4.3 , 3.0 )),
(( 3.4 ,  2.9  ), ( 4.3 , 2.9 )),
(( 3.4 ,  2.8  ), ( 4.3 , 2.8 )),
(( 3.5 ,  2.7  ), ( 4.3 , 2.7 )),
(( 3.5 ,  2.6  ), ( 4.3 , 2.6 )),
(( 3.5 ,  2.5  ), ( 4.3 , 2.5 )),
(( 3.5 ,  2.4  ), ( 4.3 , 2.4 )),
(( 3.5 ,  2.3  ), ( 4.3 , 2.3 )),
(( 3.5 ,  2.2  ), ( 4.3 , 2.2 )),
(( 3.5 ,  2.1  ), ( 4.3 , 2.1 )),
(( 3.5 ,  2.0  ), ( 4.3 , 2.0 )),
(( 3.5 ,  1.9  ), ( 4.2 , 1.9 )),
(( 3.5 ,  1.8  ), ( 4.2 , 1.8 )),
(( 3.5 ,  1.7  ), ( 4.2 , 1.7 )),
(( 0.1 ,  1.6  ), ( 0.3 , 1.6 )),
(( 3.4 ,  1.6  ), ( 4.1 , 1.6 )),
(( 0.0 ,  1.5  ), ( 0.4 , 1.5 )),
(( 3.4 ,  1.5  ), ( 4.1 , 1.5 )),
(( 0.1 ,  1.4  ), ( 0.4 , 1.4 )),
(( 3.4 ,  1.4  ), ( 4.0 , 1.4 )),
(( 0.1 ,  1.3  ), ( 0.5 , 1.3 )),
(( 3.3 ,  1.3  ), ( 4.0 , 1.3 )),
(( 0.2 ,  1.2  ), ( 0.6 , 1.2 )),
(( 3.3 ,  1.2  ), ( 3.9 , 1.2 )),
(( 0.2 ,  1.1  ), ( 0.6 , 1.1 )),
(( 3.2 ,  1.1  ), ( 3.8 , 1.1 )),
(( 0.2 ,  1.0  ), ( 0.7 , 1.0 )),
(( 3.1 ,  1.0  ), ( 3.7 , 1.0 )),
(( 0.3 ,  0.9  ), ( 0.8 , 0.9 )),
(( 3.0 ,  0.9  ), ( 3.7 , 0.9 )),
(( 0.3 ,  0.8  ), ( 0.9 , 0.8 )),
(( 2.8 ,  0.8  ), ( 3.6 , 0.8 )),
(( 0.4 ,  0.7  ), ( 1.0 , 0.7 )),
(( 2.7 ,  0.7  ), ( 3.5 , 0.7 )),
(( 0.4 ,  0.6  ), ( 1.3 , 0.6 )),
(( 2.4 ,  0.6  ), ( 3.3 , 0.6 )),
(( 0.4 ,  0.5  ), ( 3.2 , 0.5 )),
(( 0.5 ,  0.4  ), ( 3.1 , 0.4 )),
(( 0.5 ,  0.3  ), ( 2.9 , 0.3 )),
(( 0.6 ,  0.2  ), ( 2.7 , 0.2 )),
(( 0.8 ,  0.1  ), ( 2.4 , 0.1 )),
(( 1.1 ,  0.0  ), ( 2.0 , 0.0 ))],
        '6': [(( 3.3 ,  6.6  ), ( 3.5 , 6.6 )),
(( 3.0 ,  6.5  ), ( 3.7 , 6.5 )),
(( 2.7 ,  6.4  ), ( 3.6 , 6.4 )),
(( 2.5 ,  6.3  ), ( 3.3 , 6.3 )),
(( 2.3 ,  6.2  ), ( 3.1 , 6.2 )),
(( 2.1 ,  6.1  ), ( 2.9 , 6.1 )),
(( 1.9 ,  6.0  ), ( 2.7 , 6.0 )),
(( 1.8 ,  5.9  ), ( 2.5 , 5.9 )),
(( 1.7 ,  5.8  ), ( 2.4 , 5.8 )),
(( 1.5 ,  5.7  ), ( 2.3 , 5.7 )),
(( 1.4 ,  5.6  ), ( 2.1 , 5.6 )),
(( 1.3 ,  5.5  ), ( 2.0 , 5.5 )),
(( 1.2 ,  5.4  ), ( 1.9 , 5.4 )),
(( 1.1 ,  5.3  ), ( 1.8 , 5.3 )),
(( 1.0 ,  5.2  ), ( 1.7 , 5.2 )),
(( 0.9 ,  5.1  ), ( 1.7 , 5.1 )),
(( 0.8 ,  5.0  ), ( 1.6 , 5.0 )),
(( 0.8 ,  4.9  ), ( 1.5 , 4.9 )),
(( 0.7 ,  4.8  ), ( 1.4 , 4.8 )),
(( 0.6 ,  4.7  ), ( 1.4 , 4.7 )),
(( 0.6 ,  4.6  ), ( 1.3 , 4.6 )),
(( 0.5 ,  4.5  ), ( 1.3 , 4.5 )),
(( 0.5 ,  4.4  ), ( 1.2 , 4.4 )),
(( 0.4 ,  4.3  ), ( 1.2 , 4.3 )),
(( 0.4 ,  4.2  ), ( 1.2 , 4.2 )),
(( 0.3 ,  4.1  ), ( 1.1 , 4.1 )),
(( 0.3 ,  4.0  ), ( 1.1 , 4.0 )),
(( 2.1 ,  4.0  ), ( 3.0 , 4.0 )),
(( 0.3 ,  3.9  ), ( 1.1 , 3.9 )),
(( 1.8 ,  3.9  ), ( 3.3 , 3.9 )),
(( 0.2 ,  3.8  ), ( 1.1 , 3.8 )),
(( 1.7 ,  3.8  ), ( 3.5 , 3.8 )),
(( 0.2 ,  3.7  ), ( 1.0 , 3.7 )),
(( 1.5 ,  3.7  ), ( 3.6 , 3.7 )),
(( 0.2 ,  3.6  ), ( 1.0 , 3.6 )),
(( 1.4 ,  3.6  ), ( 3.7 , 3.6 )),
(( 0.1 ,  3.5  ), ( 1.0 , 3.5 )),
(( 1.3 ,  3.5  ), ( 3.8 , 3.5 )),
(( 0.1 ,  3.4  ), ( 1.0 , 3.4 )),
(( 1.1 ,  3.4  ), ( 1.7 , 3.4 )),
(( 2.5 ,  3.4  ), ( 3.9 , 3.4 )),
(( 0.1 ,  3.3  ), ( 1.5 , 3.3 )),
(( 2.7 ,  3.3  ), ( 4.0 , 3.3 )),
(( 0.1 ,  3.2  ), ( 1.3 , 3.2 )),
(( 2.9 ,  3.2  ), ( 4.0 , 3.2 )),
(( 0.1 ,  3.1  ), ( 1.2 , 3.1 )),
(( 3.0 ,  3.1  ), ( 4.1 , 3.1 )),
(( 0.1 ,  3.0  ), ( 1.1 , 3.0 )),
(( 3.1 ,  3.0  ), ( 4.1 , 3.0 )),
(( 0.0 ,  2.9  ), ( 1.1 , 2.9 )),
(( 3.2 ,  2.9  ), ( 4.1 , 2.9 )),
(( 0.0 ,  2.8  ), ( 1.0 , 2.8 )),
(( 3.2 ,  2.8  ), ( 4.1 , 2.8 )),
(( 0.0 ,  2.7  ), ( 1.0 , 2.7 )),
(( 3.2 ,  2.7  ), ( 4.2 , 2.7 )),
(( 0.0 ,  2.6  ), ( 0.9 , 2.6 )),
(( 3.3 ,  2.6  ), ( 4.2 , 2.6 )),
(( 0.0 ,  2.5  ), ( 0.9 , 2.5 )),
(( 3.3 ,  2.5  ), ( 4.2 , 2.5 )),
(( 0.0 ,  2.4  ), ( 0.9 , 2.4 )),
(( 3.3 ,  2.4  ), ( 4.2 , 2.4 )),
(( 0.0 ,  2.3  ), ( 0.9 , 2.3 )),
(( 3.4 ,  2.3  ), ( 4.2 , 2.3 )),
(( 0.0 ,  2.2  ), ( 0.9 , 2.2 )),
(( 3.4 ,  2.2  ), ( 4.2 , 2.2 )),
(( 0.0 ,  2.1  ), ( 0.9 , 2.1 )),
(( 3.4 ,  2.1  ), ( 4.2 , 2.1 )),
(( 0.1 ,  2.0  ), ( 0.9 , 2.0 )),
(( 3.4 ,  2.0  ), ( 4.2 , 2.0 )),
(( 0.1 ,  1.9  ), ( 0.9 , 1.9 )),
(( 3.4 ,  1.9  ), ( 4.2 , 1.9 )),
(( 0.1 ,  1.8  ), ( 0.9 , 1.8 )),
(( 3.4 ,  1.8  ), ( 4.2 , 1.8 )),
(( 0.1 ,  1.7  ), ( 0.9 , 1.7 )),
(( 3.4 ,  1.7  ), ( 4.1 , 1.7 )),
(( 0.1 ,  1.6  ), ( 0.9 , 1.6 )),
(( 3.4 ,  1.6  ), ( 4.1 , 1.6 )),
(( 0.1 ,  1.5  ), ( 1.0 , 1.5 )),
(( 3.3 ,  1.5  ), ( 4.1 , 1.5 )),
(( 0.2 ,  1.4  ), ( 1.0 , 1.4 )),
(( 3.3 ,  1.4  ), ( 4.0 , 1.4 )),
(( 0.2 ,  1.3  ), ( 1.0 , 1.3 )),
(( 3.3 ,  1.3  ), ( 4.0 , 1.3 )),
(( 0.2 ,  1.2  ), ( 1.0 , 1.2 )),
(( 3.3 ,  1.2  ), ( 4.0 , 1.2 )),
(( 0.3 ,  1.1  ), ( 1.1 , 1.1 )),
(( 3.3 ,  1.1  ), ( 3.9 , 1.1 )),
(( 0.3 ,  1.0  ), ( 1.1 , 1.0 )),
(( 3.2 ,  1.0  ), ( 3.9 , 1.0 )),
(( 0.4 ,  0.9  ), ( 1.2 , 0.9 )),
(( 3.2 ,  0.9  ), ( 3.8 , 0.9 )),
(( 0.4 ,  0.8  ), ( 1.2 , 0.8 )),
(( 3.1 ,  0.8  ), ( 3.7 , 0.8 )),
(( 0.5 ,  0.7  ), ( 1.3 , 0.7 )),
(( 3.0 ,  0.7  ), ( 3.6 , 0.7 )),
(( 0.6 ,  0.6  ), ( 1.4 , 0.6 )),
(( 3.0 ,  0.6  ), ( 3.5 , 0.6 )),
(( 0.7 ,  0.5  ), ( 1.5 , 0.5 )),
(( 2.9 ,  0.5  ), ( 3.4 , 0.5 )),
(( 0.8 ,  0.4  ), ( 1.6 , 0.4 )),
(( 2.7 ,  0.4  ), ( 3.3 , 0.4 )),
(( 0.9 ,  0.3  ), ( 1.8 , 0.3 )),
(( 2.5 ,  0.3  ), ( 3.2 , 0.3 )),
(( 1.1 ,  0.2  ), ( 3.0 , 0.2 )),
(( 1.3 ,  0.1  ), ( 2.8 , 0.1 )),
(( 1.6 ,  0.0  ), ( 2.5 , 0.0 ))],
        '7': [(( 0.1 ,  6.5  ), ( 0.5 , 6.5 )),
(( 3.8 ,  6.5  ), ( 4.4 , 6.5 )),
(( 0.0 ,  6.4  ), ( 4.4 , 6.4 )),
(( 0.0 ,  6.3  ), ( 4.4 , 6.3 )),
(( 0.0 ,  6.2  ), ( 4.3 , 6.2 )),
(( 0.1 ,  6.1  ), ( 4.3 , 6.1 )),
(( 0.1 ,  6.0  ), ( 4.2 , 6.0 )),
(( 0.1 ,  5.9  ), ( 4.2 , 5.9 )),
(( 0.1 ,  5.8  ), ( 4.1 , 5.8 )),
(( 0.1 ,  5.7  ), ( 0.6 , 5.7 )),
(( 3.6 ,  5.7  ), ( 4.1 , 5.7 )),
(( 0.1 ,  5.6  ), ( 0.5 , 5.6 )),
(( 3.5 ,  5.6  ), ( 4.0 , 5.6 )),
(( 0.1 ,  5.5  ), ( 0.5 , 5.5 )),
(( 3.5 ,  5.5  ), ( 4.0 , 5.5 )),
(( 0.1 ,  5.4  ), ( 0.4 , 5.4 )),
(( 3.4 ,  5.4  ), ( 3.9 , 5.4 )),
(( 0.1 ,  5.3  ), ( 0.4 , 5.3 )),
(( 3.4 ,  5.3  ), ( 3.8 , 5.3 )),
(( 0.1 ,  5.2  ), ( 0.4 , 5.2 )),
(( 3.3 ,  5.2  ), ( 3.8 , 5.2 )),
(( 0.1 ,  5.1  ), ( 0.4 , 5.1 )),
(( 3.3 ,  5.1  ), ( 3.7 , 5.1 )),
(( 0.1 ,  5.0  ), ( 0.4 , 5.0 )),
(( 3.2 ,  5.0  ), ( 3.7 , 5.0 )),
(( 0.1 ,  4.9  ), ( 0.4 , 4.9 )),
(( 3.1 ,  4.9  ), ( 3.6 , 4.9 )),
(( 0.1 ,  4.8  ), ( 0.4 , 4.8 )),
(( 3.1 ,  4.8  ), ( 3.6 , 4.8 )),
(( 0.1 ,  4.7  ), ( 0.4 , 4.7 )),
(( 3.0 ,  4.7  ), ( 3.5 , 4.7 )),
(( 0.0 ,  4.6  ), ( 0.3 , 4.6 )),
(( 3.0 ,  4.6  ), ( 3.5 , 4.6 )),
(( 0.0 ,  4.5  ), ( 0.3 , 4.5 )),
(( 2.9 ,  4.5  ), ( 3.4 , 4.5 )),
(( 2.9 ,  4.4  ), ( 3.3 , 4.4 )),
(( 2.8 ,  4.3  ), ( 3.3 , 4.3 )),
(( 2.7 ,  4.2  ), ( 3.2 , 4.2 )),
(( 2.7 ,  4.1  ), ( 3.2 , 4.1 )),
(( 2.6 ,  4.0  ), ( 3.1 , 4.0 )),
(( 2.6 ,  3.9  ), ( 3.1 , 3.9 )),
(( 2.5 ,  3.8  ), ( 3.0 , 3.8 )),
(( 2.4 ,  3.7  ), ( 3.0 , 3.7 )),
(( 2.4 ,  3.6  ), ( 2.9 , 3.6 )),
(( 2.3 ,  3.5  ), ( 2.9 , 3.5 )),
(( 2.3 ,  3.4  ), ( 2.8 , 3.4 )),
(( 2.2 ,  3.3  ), ( 2.8 , 3.3 )),
(( 2.1 ,  3.2  ), ( 2.7 , 3.2 )),
(( 2.1 ,  3.1  ), ( 2.7 , 3.1 )),
(( 2.0 ,  3.0  ), ( 2.6 , 3.0 )),
(( 2.0 ,  2.9  ), ( 2.6 , 2.9 )),
(( 1.9 ,  2.8  ), ( 2.5 , 2.8 )),
(( 1.8 ,  2.7  ), ( 2.5 , 2.7 )),
(( 1.8 ,  2.6  ), ( 2.4 , 2.6 )),
(( 1.7 ,  2.5  ), ( 2.4 , 2.5 )),
(( 1.7 ,  2.4  ), ( 2.3 , 2.4 )),
(( 1.6 ,  2.3  ), ( 2.3 , 2.3 )),
(( 1.5 ,  2.2  ), ( 2.2 , 2.2 )),
(( 1.5 ,  2.1  ), ( 2.2 , 2.1 )),
(( 1.4 ,  2.0  ), ( 2.1 , 2.0 )),
(( 1.4 ,  1.9  ), ( 2.1 , 1.9 )),
(( 1.3 ,  1.8  ), ( 2.0 , 1.8 )),
(( 1.2 ,  1.7  ), ( 2.0 , 1.7 )),
(( 1.2 ,  1.6  ), ( 1.9 , 1.6 )),
(( 1.1 ,  1.5  ), ( 1.9 , 1.5 )),
(( 1.0 ,  1.4  ), ( 1.8 , 1.4 )),
(( 1.0 ,  1.3  ), ( 1.8 , 1.3 )),
(( 0.9 ,  1.2  ), ( 1.7 , 1.2 )),
(( 0.9 ,  1.1  ), ( 1.7 , 1.1 )),
(( 0.8 ,  1.0  ), ( 1.6 , 1.0 )),
(( 0.7 ,  0.9  ), ( 1.6 , 0.9 )),
(( 0.7 ,  0.8  ), ( 1.6 , 0.8 )),
(( 0.6 ,  0.7  ), ( 1.5 , 0.7 )),
(( 0.6 ,  0.6  ), ( 1.5 , 0.6 )),
(( 0.5 ,  0.5  ), ( 1.4 , 0.5 )),
(( 0.4 ,  0.4  ), ( 1.4 , 0.4 )),
(( 0.4 ,  0.3  ), ( 1.3 , 0.3 )),
(( 0.3 ,  0.2  ), ( 1.3 , 0.2 )),
(( 0.2 ,  0.1  ), ( 1.3 , 0.1 )),
(( 0.3 ,  0.0  ), ( 1.2 , 0.0 ))],
        '8': [(( 1.7 ,  6.6  ), ( 2.8 , 6.6 )),
(( 1.4 ,  6.5  ), ( 3.1 , 6.5 )),
(( 1.1 ,  6.4  ), ( 3.3 , 6.4 )),
(( 1.0 ,  6.3  ), ( 1.7 , 6.3 )),
(( 2.6 ,  6.3  ), ( 3.5 , 6.3 )),
(( 0.9 ,  6.2  ), ( 1.5 , 6.2 )),
(( 2.8 ,  6.2  ), ( 3.6 , 6.2 )),
(( 0.7 ,  6.1  ), ( 1.4 , 6.1 )),
(( 2.9 ,  6.1  ), ( 3.7 , 6.1 )),
(( 0.7 ,  6.0  ), ( 1.3 , 6.0 )),
(( 3.0 ,  6.0  ), ( 3.8 , 6.0 )),
(( 0.6 ,  5.9  ), ( 1.2 , 5.9 )),
(( 3.1 ,  5.9  ), ( 3.8 , 5.9 )),
(( 0.5 ,  5.8  ), ( 1.1 , 5.8 )),
(( 3.2 ,  5.8  ), ( 3.9 , 5.8 )),
(( 0.5 ,  5.7  ), ( 1.1 , 5.7 )),
(( 3.2 ,  5.7  ), ( 3.9 , 5.7 )),
(( 0.4 ,  5.6  ), ( 1.0 , 5.6 )),
(( 3.2 ,  5.6  ), ( 3.9 , 5.6 )),
(( 0.4 ,  5.5  ), ( 1.0 , 5.5 )),
(( 3.3 ,  5.5  ), ( 4.0 , 5.5 )),
(( 0.3 ,  5.4  ), ( 1.0 , 5.4 )),
(( 3.3 ,  5.4  ), ( 4.0 , 5.4 )),
(( 0.3 ,  5.3  ), ( 1.0 , 5.3 )),
(( 3.3 ,  5.3  ), ( 4.0 , 5.3 )),
(( 0.3 ,  5.2  ), ( 1.0 , 5.2 )),
(( 3.3 ,  5.2  ), ( 4.0 , 5.2 )),
(( 0.3 ,  5.1  ), ( 1.0 , 5.1 )),
(( 3.3 ,  5.1  ), ( 4.0 , 5.1 )),
(( 0.3 ,  5.0  ), ( 1.1 , 5.0 )),
(( 3.3 ,  5.0  ), ( 3.9 , 5.0 )),
(( 0.3 ,  4.9  ), ( 1.1 , 4.9 )),
(( 3.3 ,  4.9  ), ( 3.9 , 4.9 )),
(( 0.3 ,  4.8  ), ( 1.1 , 4.8 )),
(( 3.3 ,  4.8  ), ( 3.9 , 4.8 )),
(( 0.3 ,  4.7  ), ( 1.2 , 4.7 )),
(( 3.2 ,  4.7  ), ( 3.8 , 4.7 )),
(( 0.3 ,  4.6  ), ( 1.3 , 4.6 )),
(( 3.2 ,  4.6  ), ( 3.8 , 4.6 )),
(( 0.3 ,  4.5  ), ( 1.4 , 4.5 )),
(( 3.1 ,  4.5  ), ( 3.7 , 4.5 )),
(( 0.4 ,  4.4  ), ( 1.5 , 4.4 )),
(( 3.1 ,  4.4  ), ( 3.6 , 4.4 )),
(( 0.4 ,  4.3  ), ( 1.6 , 4.3 )),
(( 3.0 ,  4.3  ), ( 3.5 , 4.3 )),
(( 0.5 ,  4.2  ), ( 1.8 , 4.2 )),
(( 2.9 ,  4.2  ), ( 3.4 , 4.2 )),
(( 0.5 ,  4.1  ), ( 2.0 , 4.1 )),
(( 2.8 ,  4.1  ), ( 3.3 , 4.1 )),
(( 0.6 ,  4.0  ), ( 2.2 , 4.0 )),
(( 2.6 ,  4.0  ), ( 3.2 , 4.0 )),
(( 0.7 ,  3.9  ), ( 2.4 , 3.9 )),
(( 2.5 ,  3.9  ), ( 3.0 , 3.9 )),
(( 0.8 ,  3.8  ), ( 2.9 , 3.8 )),
(( 0.9 ,  3.7  ), ( 2.9 , 3.7 )),
(( 1.1 ,  3.6  ), ( 3.0 , 3.6 )),
(( 1.2 ,  3.5  ), ( 3.2 , 3.5 )),
(( 1.3 ,  3.4  ), ( 3.4 , 3.4 )),
(( 1.2 ,  3.3  ), ( 3.6 , 3.3 )),
(( 1.0 ,  3.2  ), ( 1.6 , 3.2 )),
(( 1.9 ,  3.2  ), ( 3.7 , 3.2 )),
(( 0.9 ,  3.1  ), ( 1.5 , 3.1 )),
(( 2.1 ,  3.1  ), ( 3.8 , 3.1 )),
(( 0.7 ,  3.0  ), ( 1.3 , 3.0 )),
(( 2.3 ,  3.0  ), ( 3.9 , 3.0 )),
(( 0.6 ,  2.9  ), ( 1.2 , 2.9 )),
(( 2.5 ,  2.9  ), ( 4.0 , 2.9 )),
(( 0.5 ,  2.8  ), ( 1.1 , 2.8 )),
(( 2.7 ,  2.8  ), ( 4.1 , 2.8 )),
(( 0.4 ,  2.7  ), ( 1.0 , 2.7 )),
(( 2.8 ,  2.7  ), ( 4.1 , 2.7 )),
(( 0.3 ,  2.6  ), ( 1.0 , 2.6 )),
(( 3.0 ,  2.6  ), ( 4.2 , 2.6 )),
(( 0.3 ,  2.5  ), ( 0.9 , 2.5 )),
(( 3.1 ,  2.5  ), ( 4.2 , 2.5 )),
(( 0.2 ,  2.4  ), ( 0.9 , 2.4 )),
(( 3.2 ,  2.4  ), ( 4.2 , 2.4 )),
(( 0.2 ,  2.3  ), ( 0.8 , 2.3 )),
(( 3.3 ,  2.3  ), ( 4.2 , 2.3 )),
(( 0.1 ,  2.2  ), ( 0.8 , 2.2 )),
(( 3.4 ,  2.2  ), ( 4.2 , 2.2 )),
(( 0.1 ,  2.1  ), ( 0.8 , 2.1 )),
(( 3.4 ,  2.1  ), ( 4.2 , 2.1 )),
(( 0.1 ,  2.0  ), ( 0.7 , 2.0 )),
(( 3.4 ,  2.0  ), ( 4.2 , 2.0 )),
(( 0.1 ,  1.9  ), ( 0.7 , 1.9 )),
(( 3.5 ,  1.9  ), ( 4.2 , 1.9 )),
(( 0.1 ,  1.8  ), ( 0.7 , 1.8 )),
(( 3.5 ,  1.8  ), ( 4.2 , 1.8 )),
(( 0.0 ,  1.7  ), ( 0.7 , 1.7 )),
(( 3.5 ,  1.7  ), ( 4.2 , 1.7 )),
(( 0.0 ,  1.6  ), ( 0.7 , 1.6 )),
(( 3.5 ,  1.6  ), ( 4.2 , 1.6 )),
(( 0.1 ,  1.5  ), ( 0.7 , 1.5 )),
(( 3.5 ,  1.5  ), ( 4.2 , 1.5 )),
(( 0.1 ,  1.4  ), ( 0.7 , 1.4 )),
(( 3.5 ,  1.4  ), ( 4.1 , 1.4 )),
(( 0.1 ,  1.3  ), ( 0.8 , 1.3 )),
(( 3.5 ,  1.3  ), ( 4.1 , 1.3 )),
(( 0.1 ,  1.2  ), ( 0.8 , 1.2 )),
(( 3.4 ,  1.2  ), ( 4.0 , 1.2 )),
(( 0.1 ,  1.1  ), ( 0.8 , 1.1 )),
(( 3.4 ,  1.1  ), ( 4.0 , 1.1 )),
(( 0.2 ,  1.0  ), ( 0.8 , 1.0 )),
(( 3.4 ,  1.0  ), ( 3.9 , 1.0 )),
(( 0.2 ,  0.9  ), ( 0.9 , 0.9 )),
(( 3.3 ,  0.9  ), ( 3.9 , 0.9 )),
(( 0.3 ,  0.8  ), ( 1.0 , 0.8 )),
(( 3.3 ,  0.8  ), ( 3.8 , 0.8 )),
(( 0.3 ,  0.7  ), ( 1.0 , 0.7 )),
(( 3.2 ,  0.7  ), ( 3.7 , 0.7 )),
(( 0.4 ,  0.6  ), ( 1.1 , 0.6 )),
(( 3.1 ,  0.6  ), ( 3.6 , 0.6 )),
(( 0.5 ,  0.5  ), ( 1.3 , 0.5 )),
(( 3.0 ,  0.5  ), ( 3.5 , 0.5 )),
(( 0.6 ,  0.4  ), ( 1.4 , 0.4 )),
(( 2.8 ,  0.4  ), ( 3.4 , 0.4 )),
(( 0.7 ,  0.3  ), ( 1.6 , 0.3 )),
(( 2.5 ,  0.3  ), ( 3.2 , 0.3 )),
(( 0.9 ,  0.2  ), ( 3.0 , 0.2 )),
(( 1.1 ,  0.1  ), ( 2.8 , 0.1 )),
(( 1.4 ,  0.0  ), ( 2.4 , 0.0 ))],
        '9': [(( 1.6 ,  6.6  ), ( 2.6 , 6.6 )),
(( 1.3 ,  6.5  ), ( 3.0 , 6.5 )),
(( 1.1 ,  6.4  ), ( 3.2 , 6.4 )),
(( 0.9 ,  6.3  ), ( 1.7 , 6.3 )),
(( 2.4 ,  6.3  ), ( 3.3 , 6.3 )),
(( 0.8 ,  6.2  ), ( 1.5 , 6.2 )),
(( 2.6 ,  6.2  ), ( 3.5 , 6.2 )),
(( 0.7 ,  6.1  ), ( 1.3 , 6.1 )),
(( 2.8 ,  6.1  ), ( 3.6 , 6.1 )),
(( 0.6 ,  6.0  ), ( 1.2 , 6.0 )),
(( 2.9 ,  6.0  ), ( 3.7 , 6.0 )),
(( 0.5 ,  5.9  ), ( 1.1 , 5.9 )),
(( 2.9 ,  5.9  ), ( 3.7 , 5.9 )),
(( 0.4 ,  5.8  ), ( 1.1 , 5.8 )),
(( 3.0 ,  5.8  ), ( 3.8 , 5.8 )),
(( 0.3 ,  5.7  ), ( 1.0 , 5.7 )),
(( 3.1 ,  5.7  ), ( 3.9 , 5.7 )),
(( 0.3 ,  5.6  ), ( 1.0 , 5.6 )),
(( 3.1 ,  5.6  ), ( 3.9 , 5.6 )),
(( 0.2 ,  5.5  ), ( 0.9 , 5.5 )),
(( 3.2 ,  5.5  ), ( 4.0 , 5.5 )),
(( 0.2 ,  5.4  ), ( 0.9 , 5.4 )),
(( 3.2 ,  5.4  ), ( 4.0 , 5.4 )),
(( 0.1 ,  5.3  ), ( 0.9 , 5.3 )),
(( 3.2 ,  5.3  ), ( 4.1 , 5.3 )),
(( 0.1 ,  5.2  ), ( 0.8 , 5.2 )),
(( 3.3 ,  5.2  ), ( 4.1 , 5.2 )),
(( 0.1 ,  5.1  ), ( 0.8 , 5.1 )),
(( 3.3 ,  5.1  ), ( 4.1 , 5.1 )),
(( 0.0 ,  5.0  ), ( 0.8 , 5.0 )),
(( 3.3 ,  5.0  ), ( 4.1 , 5.0 )),
(( 0.0 ,  4.9  ), ( 0.8 , 4.9 )),
(( 3.3 ,  4.9  ), ( 4.2 , 4.9 )),
(( 0.0 ,  4.8  ), ( 0.8 , 4.8 )),
(( 3.3 ,  4.8  ), ( 4.2 , 4.8 )),
(( 0.0 ,  4.7  ), ( 0.8 , 4.7 )),
(( 3.3 ,  4.7  ), ( 4.2 , 4.7 )),
(( 0.0 ,  4.6  ), ( 0.8 , 4.6 )),
(( 3.3 ,  4.6  ), ( 4.2 , 4.6 )),
(( 0.0 ,  4.5  ), ( 0.8 , 4.5 )),
(( 3.3 ,  4.5  ), ( 4.2 , 4.5 )),
(( 0.0 ,  4.4  ), ( 0.8 , 4.4 )),
(( 3.3 ,  4.4  ), ( 4.2 , 4.4 )),
(( 0.0 ,  4.3  ), ( 0.8 , 4.3 )),
(( 3.3 ,  4.3  ), ( 4.2 , 4.3 )),
(( 0.0 ,  4.2  ), ( 0.8 , 4.2 )),
(( 3.3 ,  4.2  ), ( 4.2 , 4.2 )),
(( 0.0 ,  4.1  ), ( 0.9 , 4.1 )),
(( 3.3 ,  4.1  ), ( 4.2 , 4.1 )),
(( 0.0 ,  4.0  ), ( 0.9 , 4.0 )),
(( 3.3 ,  4.0  ), ( 4.2 , 4.0 )),
(( 0.0 ,  3.9  ), ( 0.9 , 3.9 )),
(( 3.3 ,  3.9  ), ( 4.2 , 3.9 )),
(( 0.0 ,  3.8  ), ( 1.0 , 3.8 )),
(( 3.2 ,  3.8  ), ( 4.2 , 3.8 )),
(( 0.1 ,  3.7  ), ( 1.0 , 3.7 )),
(( 3.2 ,  3.7  ), ( 4.2 , 3.7 )),
(( 0.1 ,  3.6  ), ( 1.1 , 3.6 )),
(( 3.1 ,  3.6  ), ( 4.2 , 3.6 )),
(( 0.1 ,  3.5  ), ( 1.2 , 3.5 )),
(( 3.1 ,  3.5  ), ( 4.2 , 3.5 )),
(( 0.2 ,  3.4  ), ( 1.2 , 3.4 )),
(( 3.0 ,  3.4  ), ( 4.2 , 3.4 )),
(( 0.2 ,  3.3  ), ( 1.3 , 3.3 )),
(( 2.9 ,  3.3  ), ( 4.2 , 3.3 )),
(( 0.3 ,  3.2  ), ( 1.5 , 3.2 )),
(( 2.7 ,  3.2  ), ( 3.2 , 3.2 )),
(( 3.3 ,  3.2  ), ( 4.2 , 3.2 )),
(( 0.4 ,  3.1  ), ( 1.7 , 3.1 )),
(( 2.5 ,  3.1  ), ( 3.0 , 3.1 )),
(( 3.3 ,  3.1  ), ( 4.1 , 3.1 )),
(( 0.4 ,  3.0  ), ( 2.9 , 3.0 )),
(( 3.2 ,  3.0  ), ( 4.1 , 3.0 )),
(( 0.5 ,  2.9  ), ( 2.8 , 2.9 )),
(( 3.2 ,  2.9  ), ( 4.1 , 2.9 )),
(( 0.6 ,  2.8  ), ( 2.7 , 2.8 )),
(( 3.2 ,  2.8  ), ( 4.1 , 2.8 )),
(( 0.8 ,  2.7  ), ( 2.5 , 2.7 )),
(( 3.2 ,  2.7  ), ( 4.0 , 2.7 )),
(( 1.0 ,  2.6  ), ( 2.4 , 2.6 )),
(( 3.2 ,  2.6  ), ( 4.0 , 2.6 )),
(( 1.3 ,  2.5  ), ( 2.1 , 2.5 )),
(( 3.1 ,  2.5  ), ( 4.0 , 2.5 )),
(( 3.1 ,  2.4  ), ( 3.9 , 2.4 )),
(( 3.1 ,  2.3  ), ( 3.9 , 2.3 )),
(( 3.0 ,  2.2  ), ( 3.8 , 2.2 )),
(( 3.0 ,  2.1  ), ( 3.8 , 2.1 )),
(( 2.9 ,  2.0  ), ( 3.7 , 2.0 )),
(( 2.9 ,  1.9  ), ( 3.6 , 1.9 )),
(( 2.8 ,  1.8  ), ( 3.6 , 1.8 )),
(( 2.8 ,  1.7  ), ( 3.5 , 1.7 )),
(( 2.7 ,  1.6  ), ( 3.4 , 1.6 )),
(( 2.6 ,  1.5  ), ( 3.4 , 1.5 )),
(( 2.5 ,  1.4  ), ( 3.3 , 1.4 )),
(( 2.4 ,  1.3  ), ( 3.2 , 1.3 )),
(( 2.3 ,  1.2  ), ( 3.1 , 1.2 )),
(( 2.2 ,  1.1  ), ( 3.0 , 1.1 )),
(( 2.1 ,  1.0  ), ( 2.9 , 1.0 )),
(( 2.0 ,  0.9  ), ( 2.8 , 0.9 )),
(( 1.9 ,  0.8  ), ( 2.6 , 0.8 )),
(( 1.7 ,  0.7  ), ( 2.5 , 0.7 )),
(( 1.5 ,  0.6  ), ( 2.3 , 0.6 )),
(( 1.3 ,  0.5  ), ( 2.2 , 0.5 )),
(( 1.1 ,  0.4  ), ( 2.0 , 0.4 )),
(( 0.8 ,  0.3  ), ( 1.8 , 0.3 )),
(( 0.4 ,  0.2  ), ( 1.6 , 0.2 )),
(( 0.4 ,  0.1  ), ( 1.3 , 0.1 )),
(( 0.6 ,  0.0  ), ( 0.9 , 0.0 ))],
'.': [(( 0.3 ,  1.0  ), ( 0.7 , 1.0 )),
(( 0.1 ,  0.9  ), ( 0.9 , 0.9 )),
(( 0.0 ,  0.8  ), ( 1.0 , 0.8 )),
(( 0.0 ,  0.7  ), ( 1.0 , 0.7 )),
(( 0.0 ,  0.6  ), ( 1.1 , 0.6 )),
(( 0.0 ,  0.5  ), ( 1.1 , 0.5 )),
(( 0.0 ,  0.4  ), ( 1.0 , 0.4 )),
(( 0.0 ,  0.3  ), ( 1.0 , 0.3 )),
(( 0.0 ,  0.2  ), ( 1.0 , 0.2 )),
(( 0.1 ,  0.1  ), ( 0.9 , 0.1 )),
(( 0.3 ,  0.0  ), ( 0.7 , 0.0 ))],
'/': [(( 3.4 ,  8.2  ), ( 4.1 , 8.2 )),
(( 3.3 ,  8.1  ), ( 4.0 , 8.1 )),
(( 3.3 ,  8.0  ), ( 4.0 , 8.0 )),
(( 3.3 ,  7.9  ), ( 3.9 , 7.9 )),
(( 3.2 ,  7.8  ), ( 3.9 , 7.8 )),
(( 3.2 ,  7.7  ), ( 3.8 , 7.7 )),
(( 3.1 ,  7.6  ), ( 3.8 , 7.6 )),
(( 3.1 ,  7.5  ), ( 3.8 , 7.5 )),
(( 3.1 ,  7.4  ), ( 3.7 , 7.4 )),
(( 3.0 ,  7.3  ), ( 3.7 , 7.3 )),
(( 3.0 ,  7.2  ), ( 3.6 , 7.2 )),
(( 2.9 ,  7.1  ), ( 3.6 , 7.1 )),
(( 2.9 ,  7.0  ), ( 3.6 , 7.0 )),
(( 2.9 ,  6.9  ), ( 3.5 , 6.9 )),
(( 2.8 ,  6.8  ), ( 3.5 , 6.8 )),
(( 2.8 ,  6.7  ), ( 3.4 , 6.7 )),
(( 2.7 ,  6.6  ), ( 3.4 , 6.6 )),
(( 2.7 ,  6.5  ), ( 3.3 , 6.5 )),
(( 2.6 ,  6.4  ), ( 3.3 , 6.4 )),
(( 2.6 ,  6.3  ), ( 3.3 , 6.3 )),
(( 2.6 ,  6.2  ), ( 3.2 , 6.2 )),
(( 2.5 ,  6.1  ), ( 3.2 , 6.1 )),
(( 2.5 ,  6.0  ), ( 3.1 , 6.0 )),
(( 2.4 ,  5.9  ), ( 3.1 , 5.9 )),
(( 2.4 ,  5.8  ), ( 3.1 , 5.8 )),
(( 2.4 ,  5.7  ), ( 3.0 , 5.7 )),
(( 2.3 ,  5.6  ), ( 3.0 , 5.6 )),
(( 2.3 ,  5.5  ), ( 2.9 , 5.5 )),
(( 2.2 ,  5.4  ), ( 2.9 , 5.4 )),
(( 2.2 ,  5.3  ), ( 2.8 , 5.3 )),
(( 2.1 ,  5.2  ), ( 2.8 , 5.2 )),
(( 2.1 ,  5.1  ), ( 2.8 , 5.1 )),
(( 2.1 ,  5.0  ), ( 2.7 , 5.0 )),
(( 2.0 ,  4.9  ), ( 2.7 , 4.9 )),
(( 2.0 ,  4.8  ), ( 2.6 , 4.8 )),
(( 1.9 ,  4.7  ), ( 2.6 , 4.7 )),
(( 1.9 ,  4.6  ), ( 2.6 , 4.6 )),
(( 1.9 ,  4.5  ), ( 2.5 , 4.5 )),
(( 1.8 ,  4.4  ), ( 2.5 , 4.4 )),
(( 1.8 ,  4.3  ), ( 2.4 , 4.3 )),
(( 1.7 ,  4.2  ), ( 2.4 , 4.2 )),
(( 1.7 ,  4.1  ), ( 2.3 , 4.1 )),
(( 1.6 ,  4.0  ), ( 2.3 , 4.0 )),
(( 1.6 ,  3.9  ), ( 2.3 , 3.9 )),
(( 1.6 ,  3.8  ), ( 2.2 , 3.8 )),
(( 1.5 ,  3.7  ), ( 2.2 , 3.7 )),
(( 1.5 ,  3.6  ), ( 2.1 , 3.6 )),
(( 1.4 ,  3.5  ), ( 2.1 , 3.5 )),
(( 1.4 ,  3.4  ), ( 2.1 , 3.4 )),
(( 1.4 ,  3.3  ), ( 2.0 , 3.3 )),
(( 1.3 ,  3.2  ), ( 2.0 , 3.2 )),
(( 1.3 ,  3.1  ), ( 1.9 , 3.1 )),
(( 1.2 ,  3.0  ), ( 1.9 , 3.0 )),
(( 1.2 ,  2.9  ), ( 1.8 , 2.9 )),
(( 1.1 ,  2.8  ), ( 1.8 , 2.8 )),
(( 1.1 ,  2.7  ), ( 1.8 , 2.7 )),
(( 1.1 ,  2.6  ), ( 1.7 , 2.6 )),
(( 1.0 ,  2.5  ), ( 1.7 , 2.5 )),
(( 1.0 ,  2.4  ), ( 1.6 , 2.4 )),
(( 0.9 ,  2.3  ), ( 1.6 , 2.3 )),
(( 0.9 ,  2.2  ), ( 1.5 , 2.2 )),
(( 0.9 ,  2.1  ), ( 1.5 , 2.1 )),
(( 0.8 ,  2.0  ), ( 1.5 , 2.0 )),
(( 0.8 ,  1.9  ), ( 1.4 , 1.9 )),
(( 0.7 ,  1.8  ), ( 1.4 , 1.8 )),
(( 0.7 ,  1.7  ), ( 1.3 , 1.7 )),
(( 0.6 ,  1.6  ), ( 1.3 , 1.6 )),
(( 0.6 ,  1.5  ), ( 1.3 , 1.5 )),
(( 0.6 ,  1.4  ), ( 1.2 , 1.4 )),
(( 0.5 ,  1.3  ), ( 1.2 , 1.3 )),
(( 0.5 ,  1.2  ), ( 1.1 , 1.2 )),
(( 0.4 ,  1.1  ), ( 1.1 , 1.1 )),
(( 0.4 ,  1.0  ), ( 1.0 , 1.0 )),
(( 0.4 ,  0.9  ), ( 1.0 , 0.9 )),
(( 0.3 ,  0.8  ), ( 1.0 , 0.8 )),
(( 0.3 ,  0.7  ), ( 0.9 , 0.7 )),
(( 0.2 ,  0.6  ), ( 0.9 , 0.6 )),
(( 0.2 ,  0.5  ), ( 0.8 , 0.5 )),
(( 0.2 ,  0.4  ), ( 0.8 , 0.4 )),
(( 0.1 ,  0.3  ), ( 0.8 , 0.3 )),
(( 0.1 ,  0.2  ), ( 0.7 , 0.2 )),
(( 0.0 ,  0.1  ), ( 0.7 , 0.1 )),
(( 0.0 ,  0.0  ), ( 0.6 , 0.0 ))],
'-': [(( 0.2 ,  0.6  ), ( 2.8 , 0.6 )),
(( 0.2 ,  0.5  ), ( 2.8 , 0.5 )),
(( 0.2 ,  0.4  ), ( 2.7 , 0.4 )),
(( 0.1 ,  0.3  ), ( 2.7 , 0.3 )),
(( 0.1 ,  0.2  ), ( 2.7 , 0.2 )),
(( 0.0 ,  0.1  ), ( 2.6 , 0.1 )),
(( 0.0 ,  0.0  ), ( 2.6 , 0.0 ))]
    }

def rasberitesb(sender,app_data):
    if app_data:
        if sender == 'change_order':
            dpg.set_value('add_text',False)
            dpg.set_value('movelines',False)
        if sender == 'add_text':
            dpg.set_value('change_order',False)
            dpg.set_value('movelines',False)
        if sender == 'movelines':
            dpg.set_value('change_order',False)
            dpg.set_value('add_text',False)

def plot_mouse_click_callback():
    global lines
    global ts
    global objects
    global active_obj
    x,y = dpg.get_plot_mouse_pos()
    if dpg.get_value('change_order'):

        l = find_closest_lines(lines,(x,y),range(len(lines)))
        
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
    elif dpg.get_value('add_text'):
        delta = 0
        val = dpg.get_value('insert_numbers')
        nice_path = val
        iter = 1
        while 1:
            for i in objects:
                if i == nice_path:
                    nice_path = val + f' (copy {iter})'
                    iter +=1
            else: 
                break
        dpg.add_button(label=nice_path,parent='butonss',tag=nice_path,callback=active_but)
        active_obj.append({'tag':nice_path,
                        'bool':0})
        for ch in val:
            for l in digit_lines[ch]:
                lines.append({
                    'start': (x+l[0][0] + delta, y+l[0][1]),
                    'end': (x+l[1][0] + delta, y+l[1][1])
                })
                ts.append(0)
                objects.append(nice_path)
            delta += 6
        redraw()
    elif dpg.get_value('movelines'):
        for t in active_obj:
            if t['bool'] == 1:
                flines = []  
                movedl = []
                for i,o in enumerate(objects):
                    if o == t['tag']:
                        flines.append(lines[i])      
                        movedl.append(i)     

                min_x = min(line['start'][0] for line in flines)
                min_y = min(line['start'][1] for line in flines)

                new_lines = []
                for j in range(len(lines)):
                    if j in movedl:
                        new_lines.append({
                            'start': (lines[j]['start'][0]+x - min_x, lines[j]['start'][1]+y - min_y),
                            'end': (lines[j]['end'][0]+x - min_x,lines[j]['end'][1] +y - min_y)
                            }) 

                    else:
                        new_lines.append(lines[j])
                lines = new_lines
                
        redraw()
          
def redraw():


    dpg.delete_item(Y_AXIS_TAG, children_only=True, slot=1)

    for i in range(len(lines)):
        start = lines[i]['start']
        end = lines[i]['end']
        
        dpg.add_line_series([start[0], end[0]], [start[1], end[1]],label=f"Line ", parent=Y_AXIS_TAG)
        ff = True
        for k in active_obj:
            if k['tag'] == objects[i]:
                ff = k['bool']        
        if ff == 1:
            dpg.bind_item_theme(dpg.last_item(), themes[5])
        else:
            dpg.bind_item_theme(dpg.last_item(), themes[ts[i]])
def set_color():
    global lines
    global ts
    global objects
    global active_obj
    for t in active_obj:
        if t['bool'] == 1:
            
            for i,o in enumerate(objects):
                if o == t['tag']:
                    if dpg.get_value('1'):
                        
                        ts[i] = 0
                    elif dpg.get_value('2'):
                        
                        ts[i] = 1
                    elif dpg.get_value('3'):
                        
                        ts[i] = 2
                    elif dpg.get_value('4'):
                        
                        ts[i] = 3
                    elif dpg.get_value('5'):
                       
                        ts[i] = 4  
                        

    redraw()
def delete_l():
    global lines
    global ts
    global objects
    global active_obj

    deleted_aciv = []
    for i,t in enumerate(active_obj):
        if t['bool'] == 1:
            dpg.delete_item(t['tag'])
            
            new_lines = []
            new_ts = []
            new_objects = []
            for i,o in enumerate(objects):
                if o != t['tag']:    
                    new_lines.append(lines[i])
                    new_ts.append(ts[i])
                    new_objects.append(objects[i])    

            lines = new_lines
            ts = new_ts
            objects = new_objects
        else:
            deleted_aciv.append(i)
    new_active_obj = []
    for i in deleted_aciv:
        new_active_obj.append(active_obj[i])
    active_obj = new_active_obj
    redraw()


def split_l():
    global lines
    global ts
    global objects
    global active_obj

    deleted_aciv = []
    new_active_obj = []
    new_lines = []
    new_ts = []
    new_objects = []
    for i,t in enumerate(active_obj):
        if t['bool'] == 1:
            dpg.delete_item(t['tag'])
           
            lines_for_split = []
            ts_for_split = []
           
            for i,o in enumerate(objects):
                if o != t['tag']:    
                    new_lines.append(lines[i])
                    new_ts.append(ts[i])
                    new_objects.append(objects[i])    
                else:
                    lines_for_split.append(lines[i])
                    ts_for_split.append(ts[i])
            sett = {i for i in range(len(lines_for_split))}
        
            v = 0
            while sett:
                i = next(iter(sett))
                l = find_closest_lines(lines_for_split,lines_for_split[i]['start'],sett)
                dpg.add_button(label=t['tag'] + f'__{v}',parent='butonss',tag=t['tag'] + f'__{v}',callback=active_but)
                new_active_obj.append({'tag':t['tag'] + f'__{v}','bool':0})
                #new_lines.append(lines_for_split[i])
                # new_ts.append(ts_for_split[i])
                # new_objects.append(t['tag'] + f'__{v}')   
                
                for h in l:
                    new_lines.append(lines_for_split[h])
                    new_ts.append(ts_for_split[h])
                    new_objects.append(t['tag'] + f'__{v}')   
                    sett.remove(h)
                v+=1
 
            

        else:
            deleted_aciv.append(i)


    lines = new_lines
    ts = new_ts
    objects = new_objects


    for i in deleted_aciv:
        new_active_obj.append(active_obj[i])
    


    active_obj = new_active_obj
    redraw()

def optimize_():
    
    
    optimize.create_continuous_lines('temp.dxf',lines )
    #plot_dxf('temp.dxf')

def normal_():
    normalize_lines(lines)
    redraw()

def rotate_x():
    invers_lines(lines)
    redraw()


def normalize_lines(lines):
    
    min_x = min(line['start'][0] for line in lines)
    min_y = min(line['start'][1] for line in lines)
    
    # Создаем новый массив для нормализованных линий
    normalized_lines = []
    
    for line in lines:
        normalized_start = (line['start'][0] - min_x, line['start'][1] - min_y)
        normalized_end = (line['end'][0] - min_x, line['end'][1] - min_y)
        normalized_lines.append({
            'start': normalized_start,
            'end': normalized_end
        })
    
    return normalized_lines

def invers_lines(lines):
    # Находим минимальные координаты по X и Y
    #min_x = min(line['start'][0] for line in lines)
    max_y = max(line['start'][1] for line in lines)
    
    # Создаем новый массив для нормализованных линий
    normalized_lines = []
    
    for line in lines:
        normalized_start = (line['start'][0],max_y - line['start'][1] )
        normalized_end = (line['end'][0], max_y - line['end'][1])
        normalized_lines.append({
            'start': normalized_start,
            'end': normalized_end
        })
    
    return normalized_lines
def esy_eda(selected_files):
    current_file = selected_files[0]
    global lines
    global ts
    global objects
    global active_obj
    if dpg.get_value('eraseold'):
        
        for i in active_obj:
            dpg.delete_item(i['tag'])
        lines = []
        ts = []
        active_obj = []
        objects = []
        lines,ts,objects  = read_dxf_lines_from_esyeda(current_file)
    else:
        li,t,obje  = read_dxf_lines_from_esyeda(current_file)
        
        lines+=li
        ts+=t
        
        objects+=obje
        
    redraw()


def pr(selected_files):
    
    current_file = selected_files[0]
    global lines
    global ts
    global objects
    global active_obj
    global esyedaflag
    if '.dxf' in current_file: 
        if dpg.get_value('eraseold'):
            
            for i in active_obj:
                dpg.delete_item(i['tag'])
            # lines = []
            # ts = []
            active_obj = []
            # objects = []
            if esyedaflag:
                esyedaflag = False
                lines,ts,objects  = read_dxf_lines_from_esyeda(current_file)
            else:
                lines,ts,objects  = read_dxf_lines(current_file)
        else:
            li,t,obje  = read_dxf_lines(current_file)
            
            lines+=li
            ts+=t
            
            objects+=obje
            
        redraw()
    if '.png' in current_file:
        
        if dpg.get_value('eraseold'):
            for i in active_obj:
                dpg.delete_item(i['tag'])
                # lines = []
                # ts = []
                # active_obj = []
                # objects = []

            
            lines,ts,active_obj,objects = extract_black_lines(current_file,0.1)

        else:
            line,t,active_ob,ob = extract_black_lines(current_file,0.1)         
            lines += line
            ts += t
            active_obj += active_ob
            objects += ob

       
        redraw()
###########################################
##########################################
#############################################
def test_callback():
    split_l()
    #redraw()
####################################################
####################################################
####################################################

def esye():
    global esyedaflag
    fd.show_file_dialog()
    esyedaflag = True
dpg.create_context()

X_AXIS_TAG = "x_axis_tag"
Y_AXIS_TAG = "y_axis_tag"

current_file = None
themes = []
components = []
lines =[]
ts = []
objects = []
active_obj = []
esyedaflag = False
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
with dpg.theme(tag="coloured_line_theme6") as coloured_line_theme6:
    with dpg.theme_component():
        coloured_line_component6 = dpg.add_theme_color(dpg.mvPlotCol_Line, (255, 255, 255, 255 ), category=dpg.mvThemeCat_Plots)

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
themes.append(coloured_line_theme6)
components.append(coloured_line_component6)

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




with dpg.theme() as enabled_theme:
    with dpg.theme_component(dpg.mvAll):
        dpg.add_theme_color(dpg.mvThemeCol_Text, (255, 255, 255), category=dpg.mvThemeCat_Core)


with dpg.theme() as disabled_theme:
    with dpg.theme_component(dpg.mvAll):
        dpg.add_theme_color(dpg.mvThemeCol_Text, (255, 0, 0), category=dpg.mvThemeCat_Core)

fd = FileDialog(callback=pr, show_dir_size=False, modal=False, allow_drag=False,width=800,height=400,filter_list=[".dxf",".png"],)
#fd_esyeda = FileDialog(callback=esy_eda)

with dpg.viewport_menu_bar():
    with dpg.menu(label="File"):
        dpg.add_menu_item(label="Open", callback=fd.show_file_dialog)
        dpg.add_menu_item(label="Open DXF from EsyEDA", callback=esye)
        dpg.add_menu_item(label="Save As Gcode", callback=save_as_gcode)
        dpg.add_menu_item(label="Save As", callback=save_dxf)
        
        
        with dpg.menu(label="Settings"):
            dpg.add_menu_item(label="Setting 1", callback=print_me, check=True)
            dpg.add_menu_item(label="Setting 2", callback=print_me)
    with dpg.menu(label="Functions"):
        dpg.add_menu_item(label="Optimize", callback=optimize_)
        dpg.add_menu_item(label="Normalize", callback=normal_)
        dpg.add_menu_item(label="Rotate X", callback=rotate_x)
        dpg.add_menu_item(label="Delete", callback=delete_l)
        dpg.add_menu_item(label="Set Color", callback=set_color)
        dpg.add_menu_item(label="test", callback=test_callback)

    with dpg.menu(label="Widget Items"):
        dpg.add_checkbox(label="Pick Me", callback=print_me)
        dpg.add_button(label="Press Me", callback=print_me)
        dpg.add_color_picker(label="Color Me", callback=print_me)      



with dpg.window(pos=(0,0),width=900, height=725,tag='papa'):
    
    with dpg.group(horizontal=True):
        with dpg.group():
            # with dpg.file_dialog(directory_selector=False, show=False, callback=callback_, id="file_dialog_id", width=700 ,height=400):
            #         dpg.add_file_extension("", color=(150, 255, 150, 255))
            #         dpg.add_file_extension(".dxf", color=(255, 0, 255, 255), custom_text="[DXF]")
            #         dpg.add_file_extension(".png", color=(255, 0, 0, 255), custom_text="[PNG]")
            with dpg.file_dialog(directory_selector=False, show=False, callback=callback_to_gcode, id="file_dialog_id2", width=700 ,height=400):
                    dpg.add_file_extension(".gcode", color=(255, 0, 255, 255), custom_text="[DXF]")
            
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
                    dpg.add_checkbox(label="1",tag='1',callback=check_callback,default_value=True)
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


                
                




        with dpg.group():
            dpg.add_input_text(multiline=True, label="", default_value="", tag="multiline_input", readonly=True,width=300,height=600)
            dpg.add_checkbox(label="erase old",default_value=True,tag='eraseold')
            with dpg.group(horizontal=True):
                
                dpg.add_checkbox(label="paste numbers",default_value=False,tag='add_text',callback=rasberitesb)
                dpg.add_input_text(width=50,scientific=True,tag='insert_numbers',default_value='123')
            dpg.add_checkbox(label="change order",default_value=False,tag='change_order',callback=rasberitesb)
            dpg.add_checkbox(label="move lines",default_value=False,tag='movelines',callback=rasberitesb)
    
with dpg.item_handler_registry() as registry:
    dpg.add_item_clicked_handler(button=dpg.mvMouseButton_Right, callback=plot_mouse_click_callback)
dpg.bind_item_handler_registry(plot, registry)


dpg.add_window(pos=(900,0),width=200, height=725,tag='butonss',label='lines')
   

dpg.create_viewport(width=1115, height=785, title="GCODE IDE")
dpg.setup_dearpygui()
dpg.show_viewport()
dpg.start_dearpygui()
dpg.destroy_context()