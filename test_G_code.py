import dxfgrabber

def dxf_to_gcode(dxf_file, gcode_file):
    dxf = dxfgrabber.readfile(dxf_file)
    
    gcode_lines = []

    gcode_lines.append("G90")
    gcode_lines.append("M4 S0")
    
    temp_point = (0,0)
    for entity in dxf.entities:
        if entity.dxftype == 'LINE':
            start = entity.start
            end = entity.end
            if abs(temp_point[0] - start[0]) > 1 or abs(temp_point[1] - start[1]) > 1:
                gcode_lines.append(f"S0")
                gcode_lines.append(f"G0 X{start[0]} Y{start[1]}")
            
            gcode_lines.append(f"S1000")
            gcode_lines.append(f"G1 X{end[0]} Y{end[1]}F180")
            gcode_lines.append(f"S0")
    gcode_lines.append(f"M5 S0")
    with open(gcode_file, 'w') as f:
        f.write("\n".join(gcode_lines))

#dxf_to_gcode('asd.dxf', 'output.gcode')