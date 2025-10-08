from PIL import Image
import numpy as np

def extract_black_lines(image_path, pixel_distance):
    # Открываем изображение
    img = Image.open(image_path).convert('L')  # Конвертируем в градации серого
    img_array = np.array(img)

    # Получаем высоту и ширину изображения
    height, width = img_array.shape

    # Инициализируем массив линий
    lines = []

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
                    'start': (start[0], start[1]),
                    'end': (x - pixel_distance, y)
                    })
                    start = None
        # Проверяем, есть ли незавершенная линия в конце ряда
        if start is not None:
            lines.append((start, (width - pixel_distance, y)))

    return lines


image_path = 'im2.png'
pixel_distance = 1 
black_lines = extract_black_lines(image_path, pixel_distance)



for i, line in enumerate(black_lines):
    print(f'Line {i}: Start {line[0]}, End {line[1]}')