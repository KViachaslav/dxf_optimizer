
import dearpygui.dearpygui as dpg
import ezdxf
import numpy as np
import math
import svgwrite
import test_G_code
from PIL import Image

X_AXIS_TAG = "x_axis_tag"
Y_AXIS_TAG = "y_axis_tag"
lines =[]
ts = []


    
    


def arc_to_lines(center, radius, start_angle, end_angle, num_segments):
    start_angle_rad = np.radians(start_angle)
    end_angle_rad = np.radians(end_angle)

    angles = np.linspace(start_angle_rad, end_angle_rad, num_segments + 1)

    points = [(center[0] + radius * np.cos(angle), center[1] + radius * np.sin(angle)) for angle in angles]
    return points
def extract_black_lines(image_path, pixel_distance):
    # Открываем изображение
    img = Image.open(image_path).convert('L')  # Конвертируем в градации серого
    img_array = np.array(img)

    # Получаем высоту и ширину изображения
    height, width = img_array.shape

    # Инициализируем массив линий
    lines = []
    tss = []
    # Проходим по каждому ряду изображения
    for y in range(height):
        start = None
        for x in range(0, width):
            
            if img_array[y, x] < 128:  
                if start is None:
                    start = (x, y) 
            else:
                if start is not None:
                    # Если нашли конец линии, добавляем ее
                    #lines.append((start, (x - pixel_distance, y)))
                    lines.append({
                    'start': (start[0]*pixel_distance, start[1]*pixel_distance),
                    'end': (x*pixel_distance, y*pixel_distance)
                    })
                    print(start[0], start[1])
                    tss.append(0)
                    start = None
        # Проверяем, есть ли незавершенная линия в конце ряда
        if start is not None:
            lines.append((start, (width - pixel_distance, y)))

    return lines,tss
def read_dxf_lines(file_path):
    dpg.set_value('file',file_path)
    tss = []
    doc = ezdxf.readfile(file_path)
    msp = doc.modelspace()
    lines = []

    for line in msp.query('LINE'):
        lines.append({
            'start': (line.dxf.start.x, line.dxf.start.y),
            'end': (line.dxf.end.x, line.dxf.end.y)
        })
        tss.append(0)
    for acdb_line in msp.query('AcDbLine'):
        lines.append({
            'start': (acdb_line.dxf.start.x, acdb_line.dxf.start.y),
            'end': (acdb_line.dxf.end.x, acdb_line.dxf.end.y)
        })
        tss.append(0)
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
    for polyline in msp.query('LWPOLYLINE'):
        w = polyline.dxf.const_width
        print(w)
        points = polyline.get_points()  
        for i in range(len(points) - 1):
            #boundaries = test.calculate_boundary_coordinates(points[i][0], points[i][1], points[i + 1][0], points[i + 1][1], w)
            lines.append({
                'start': (points[i][0], points[i][1]),
                'end': (points[i + 1][0], points[i + 1][1])
            })
            tss.append(0)
            # lines.append({
            #     'start': (boundaries['left_start'][0], boundaries['left_start'][1]),
            #     'end': (boundaries['left_end'][0],boundaries['left_end'][1])
            # })
            # tss.append(0)
            # lines.append({
            #     'start': (boundaries['right_start'][0], boundaries['right_start'][1]),
            #     'end': (boundaries['right_end'][0],boundaries['right_end'][1])
            # })
            # tss.append(0)
    for hatch in msp.query('HATCH'):
        for path in hatch.paths:
        
            points = path.vertices
            # print(points)
            lines.append({
                'start': (points[0][0], points[0][1]),
                'end': (points[1][0],points[1][1])
            })
            tss.append(3)
    return lines,tss

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
    delta = 0.8
    while Nums:
        fl = True
        for i in Nums:

            if abs(lines[i]['start'][0] - current_start[0]) < delta and abs(lines[i]['start'][1] - current_start[1]) < delta:
                lins.append(i)
                
                current_start = lines[i]['end']
                Nums.remove(i)
                fl = False
                break
            elif abs(lines[i]['end'][0] - current_start[0]) < delta and abs(lines[i]['end'][1] - current_start[1]) < delta:
                
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
def save_as_gcode():
    dpg.show_item("file_dialog_id2")
def callback_to_gcode(sender, app_data, user_data):
    global lines
    global ts
    #print(lines,ts)

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

            p,j,m = find_closest_pointt(lines,current_start,sett)
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
# def load_dxf():
#         dpg.show_item("file_dialog_id")

def check_callback(sender):
    for i in ['1','2','3','4','5']:
         if i != sender:
              dpg.set_value(i,False)


def print_me(sender):
    print(f"Menu Item: {sender}")