import math

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






import numpy as np

def calculate_bending_boundaries(points, width):
    boundaries = []

    for i in range(1, len(points) - 1):
        A = np.array(points[i - 1])
        B = np.array(points[i])
        C = np.array(points[i + 1])

        # Векторы
        AB = B - A
        BC = C - B

        # Нормализация векторов
        d_AB = np.linalg.norm(AB)
        d_BC = np.linalg.norm(BC)

        if d_AB == 0 or d_BC == 0:
            raise ValueError("Две точки не могут совпадать.")

        u_AB = AB / d_AB
        u_BC = BC / d_BC

        # Перпендикулярные векторы
        n_AB = np.array([-u_AB[1], u_AB[0]])
        n_BC = np.array([-u_BC[1], u_BC[0]])

        # Границы в точке B
        left_B = B + (width / 2) * n_AB
        right_B = B - (width / 2) * n_AB

        # Добавление границ в список
        boundaries.append({
            "left": left_B,
            "right": right_B
        })

    # Обработка границ для первой и последней точек
    boundaries.insert(0, {
        "left": points[0] + (width / 2) * np.array([0, 1]),
        "right": points[0] - (width / 2) * np.array([0, 1])
    })

    boundaries.append({
        "left": points[-1] + (width / 2) * np.array([0, 1]),
        "right": points[-1] - (width / 2) * np.array([0, 1])
    })

    return boundaries

# Пример использования
# points = [(0, 0), (2, 3), (4, 1), (6, 4)]
# width = 2

# boundaries = calculate_bending_boundaries(points, width)
# for i, boundary in enumerate(boundaries):
#     print(f"Segment {i}: Left: {boundary['left']}, Right: {boundary['right']}")



# import cairosvg

# # Путь к вашему SVG файлу
# svg_file = "PCBB.svg"
# # Путь для сохранения PNG файла
# png_file = "outputPCB.png"

# # Конвертация SVG в PNG
# cairosvg.svg2png(url=svg_file, write_to=png_file)

# print("Конвертация завершена!")