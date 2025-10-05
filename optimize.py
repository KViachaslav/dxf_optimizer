import ezdxf
import svgwrite

def dxf_to_svg(dxf_file, svg_file):

    doc = ezdxf.readfile(dxf_file)
    dwg = svgwrite.Drawing(svg_file, profile='tiny')

    for entity in doc.modelspace().query('LINE'):
        start = entity.dxf.start
        end = entity.dxf.end
        dwg.add(dwg.line(start=(start.x, start.y), end=(end.x, end.y), stroke=svgwrite.rgb(0, 0, 0, '%')))

    dwg.save()
def read_dxf_lines(file_path):
    doc = ezdxf.readfile(file_path)
    msp = doc.modelspace()
    lines = []

    for line in msp.query('LINE'):
        lines.append({
            'start': (line.dxf.start.x, line.dxf.start.y),
            'end': (line.dxf.end.x, line.dxf.end.y)
        })

    return lines

def create_continuous_lines(file_path_out, lines):
    doc = ezdxf.new()
    msp = doc.modelspace()

    if not lines:
        return
    msp.add_line(lines[0]['start'], lines[0]['end'])
    nums = set(range(len(lines)))
    
    current_start = lines[0]['end']
    nums.remove(0)
    print(lines[0]['start'], lines[0]['end'])
    
    while nums:
        fl = True
        for i in nums:

            if abs(lines[i]['start'][0] - current_start[0]) < 0.0000001 and abs(lines[i]['start'][1] - current_start[1]) < 0.0000001:
                #print(lines[i]['start'], lines[i]['end'])
                msp.add_line(current_start, lines[i]['end'])
                current_start = lines[i]['end']
                nums.remove(i)
                fl = False
                break
            elif abs(lines[i]['end'][0] - current_start[0]) < 0.0000001 and abs(lines[i]['end'][1] - current_start[1]) < 0.0000001:
                #print(lines[i]['start'], lines[i]['end'])
                msp.add_line( current_start,lines[i]['start'])
                current_start = lines[i]['start']
                nums.remove(i)
                fl = False
                break
        if fl: 
            i = next(iter(nums))
            msp.add_line(lines[i]['start'], lines[i]['end'])
            nums.remove(i)



        

    
    doc.saveas(file_path_out)

input_file = 'Sss.dxf' 
output_file = 'asd.dxf'  

lines = read_dxf_lines(input_file)

#print(lines)
create_continuous_lines(output_file, lines)
dxf_to_svg(output_file, 'output.svg')
print(f"Новый файл с непрерывными линиями сохранён как: {output_file}")