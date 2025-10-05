import dxfgrabber

def dxf_to_gcode(dxf_file, gcode_file):
    dxf = dxfgrabber.readfile(dxf_file)
    
    gcode_lines = []

    gcode_lines.append("; G-code generated from DXF")
    gcode_lines.append("G21 ; Set units to mm")
    gcode_lines.append("G90 ; Absolute positioning")

    for entity in dxf.entities:
        if entity.dxftype == 'LINE':
            start = entity.start
            end = entity.end
            gcode_lines.append(f"G0 X{start[0]} Y{start[1]} ; Move to start")
            gcode_lines.append(f"G1 X{end[0]} Y{end[1]} ; Draw line")

    with open(gcode_file, 'w') as f:
        f.write("\n".join(gcode_lines))

dxf_to_gcode('asd.dxf', 'output.gcode')