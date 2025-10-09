import matplotlib.pyplot as plt
import numpy as np

def draw_hatched_area(rect, circles):
    """
    Рисует горизонтальную штриховку в пределах прямоугольника, избегая кругов.
    
    :param rect: tuple (x_min, y_min, x_max, y_max)
    :param circles: list of tuples [(x_center, y_center, radius), ...]
    """
    x_min, y_min, x_max, y_max = rect
    y_lines = []

    step = 0.1

    for y in np.arange(y_min, y_max, step):

        x_start = x_min
        x_end = x_max
        points = [x_start,x_end]
        for (x_center, y_center, radius) in circles:
            
            if abs(y - y_center) <= radius:  
                delta_x = np.sqrt(radius**2 - (y - y_center)**2)
                x_left = x_center - delta_x
                x_right = x_center + delta_x
                points.append(x_left)
                points.append(x_right)

        for i in range(len(points)-1):
            y_lines.append((points[i], y, points[i+1], y))
        # else:
        #     y_lines.append((x_start, y, x_end, y))
               
        
        

    for (x_start, y, x_end, y) in y_lines:
        plt.plot([x_start, x_end], [y, y], color='black')

    # Устанавливаем границы и показываем график
    plt.xlim(x_min, x_max)
    plt.ylim(y_min, y_max)
    plt.gca().set_aspect('equal')
    plt.show()

# Пример использования
rect = (0, 0, 10, 10)
circles = [(2, 2, 1), (5, 5, 1), (8, 8, 1)]

draw_hatched_area(rect, circles)
# import matplotlib.pyplot as plt
# plt.figure()

# # Вывод результатов (первые несколько линий для примера)
# print(f"Сгенерировано отрезков: {len(hatch_segments)}")
# for i, segment in enumerate(hatch_segments[:6]):
#     print(f"Линия {i+1}: ({segment[0]:.2f}, {segment[1]:.2f}) -> ({segment[2]:.2f}, {segment[3]:.2f})")
#     plt.plot([segment[0],segment[2]], [segment[1],segment[3]], color='blue')

# plt.show()