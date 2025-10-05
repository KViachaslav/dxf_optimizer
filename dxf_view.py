import ezdxf
import matplotlib.pyplot as plt

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




def plot_lines(lines):
    colorr = 0
    colorg = 0
    colorb = 0
    plt.figure(figsize=(8, 8))
    
    for line in lines:
        start = line['start']
        end = line['end']

        plt.plot([start[0], end[0]], [start[1], end[1]],color= (colorr/255,colorg/255,colorb/255))
        # if colorr<255:
        #     colorr +=255
        # elif colorg<255:
        #     colorg += 255
        # elif colorb<255:
        #     colorb +=255
        # else:
        #     colorr = 0
        #     colorb = 0
        #     colorg = 0

    plt.title('Lines from DXF file')
    plt.xlabel('X')
    plt.ylabel('Y')
    plt.grid()
    plt.axis('equal')  
    plt.show()

file_path = 'dada.dxf'
lines = read_dxf_lines(file_path)
print(len(lines))
plot_lines(lines)