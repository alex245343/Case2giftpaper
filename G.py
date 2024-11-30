import gradio as gr
import os
import logging

logging.basicConfig(filename='file_check.log', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

base_path = os.path.dirname(os.path.abspath(__file__))

config_path = os.path.join(base_path, "config.py")
output_image_path = os.path.join(base_path, "collage_a4.png")  # Путь к выходному изображению
images_directory = os.path.join(base_path, "фотки")  # Путь для сохранения загруженных фотографий

#натройки ширины и высоты
paper_sizes = {
    "A4": (2480, 3508),
    "A3": (3508, 4961),
    "A5": (1748, 2480),
}

#предустановленные фоны
preset_backgrounds = {
    "Белый": os.path.join(images_directory, "фоны", "walter.png"),
    "Черный": os.path.join(images_directory, "фоны", "black.png"),
    "Красный": os.path.join(images_directory, "фоны", "red.png"),
    "Зеленый": os.path.join(images_directory, "фоны", "green.png"),
    "Синий": os.path.join(images_directory, "фоны", "blue.png"),
    "Желтый": os.path.join(images_directory, "фоны", "yellow.png"),
    "Розовый": os.path.join(images_directory, "фоны", "pink.png"),
    "Серый": os.path.join(images_directory, "фоны", "grey.png"),
}

def check_file_exists(file_path):
    if os.path.exists(file_path):
        logging.info(f"Файл найден: {file_path}")
        return True
    else:
        logging.warning(f"Файл не найден: {file_path}")
        return False

def update_parameters(brightness, contrast, saturation, sharpness, num_rows, num_cols, spacing, image_files, background_file, paper_size, background_color):
    #сохранение загруженных изображений
    image_paths = []
    
    #проверка наличия директории для изображений
    if not os.path.exists(images_directory):
        logging.error(f"Директория не найдена: {images_directory}")
        return None

    #обработка
    for image in image_files:
        image_path = os.path.join(images_directory, os.path.basename(image.name))
        with open(image.name, "rb") as f_in:
            with open(image_path, "wb") as f_out:
                f_out.write(f_in.read())
        image_paths.append(repr(image_path))

    #работа с фоном
    if background_file:
        background_path = os.path.join(images_directory, os.path.basename(background_file.name))
        with open(background_file.name, "rb") as f_in:
            with open(background_path, "wb") as f_out:
                f_out.write(f_in.read())
    else:
        background_path = preset_backgrounds[background_color]  # Используем путь к предустановленному фону

    if not check_file_exists(config_path):
        return None

    if not check_file_exists(background_path):
        return None

    #обновление конфигов
    with open(config_path, 'r', encoding='utf-8') as file:
        lines = file.readlines()

    with open(config_path, 'w', encoding='utf-8') as file:
        for line in lines:
            if line.startswith("BRIGHTNESS"):
                file.write(f"BRIGHTNESS = {brightness}\n")
            elif line.startswith("CONTRAST"):
                file.write(f"CONTRAST = {contrast}\n")
            elif line.startswith("SATURATION"):
                file.write(f"SATURATION = {saturation}\n")
            elif line.startswith("SHARPNESS"):
                file.write(f"SHARPNESS = {sharpness}\n")
            elif line.startswith("NUM_ROWS"):
                file.write(f"NUM_ROWS = {num_rows}\n")
            elif line.startswith("NUM_COLS"):
                file.write(f"NUM_COLS = {num_cols}\n")
            elif line.startswith("SPACING"):
                file.write(f"SPACING = {spacing}\n")
            elif line.startswith("IMAGE_PATHS"):
                file.write(f"IMAGE_PATHS = [{', '.join(image_paths)}]\n")
            elif line.startswith("BACKGROUND_IMAGE_PATH"):
                file.write(f"BACKGROUND_IMAGE_PATH = r'{background_path}'\n")
            elif line.startswith("A4_WIDTH ") or line.startswith("A3_WIDTH") or line.startswith("A5_WIDTH"):
                width, height = paper_sizes[paper_size]
                file.write(f"A4_WIDTH = {width}\n")
                file.write(f"A4_HEIGHT = {height}\n")
            else:
                file.write(line)

    #запуск v.py
    os.system(r'python ' + os.path.join(base_path, "V.py"))

    return output_image_path  

#gradio
brightness_slider = gr.Slider(minimum=0.0, maximum=3.0, step=0.1, value=1.2, label="Яркость")
contrast_slider = gr.Slider(minimum=0.0, maximum=3.0, step=0.1, value=1.5, label="Контраст")
saturation_slider = gr.Slider(minimum=0.0, maximum=3.0, step=0.1, value=1.3, label="Насыщенность")
sharpness_slider = gr.Slider(minimum=0.0, maximum=3.0, step=0.1, value=1.0, label="Резкость")
num_rows_slider = gr.Slider(minimum=1, maximum=10, step=1, value=5, label="Количество строк")
num_cols_slider = gr.Slider(minimum=1, maximum=10, step=1, value=5, label="Количество столбцов")
spacing_slider = gr.Slider(minimum=0, maximum=100, step=1, value=20, label="Расстояние между изображениями")

#формат
paper_size_dropdown = gr.Dropdown(choices=list(paper_sizes.keys()), label="Формат бумаги", value="A4")

#фон
background_color_dropdown = gr.Dropdown(choices=list(preset_backgrounds.keys()), label="Фон", value="Белый")

#изображения
image_upload = gr.File(label="Загрузите фотографии", file_count="multiple", type="filepath")
background_upload = gr.File(label="Загрузите фоновое изображение", type="filepath")

interface = gr.Interface(fn=update_parameters, 
                         inputs=[brightness_slider, contrast_slider, saturation_slider, 
                                 sharpness_slider, num_rows_slider, num_cols_slider, spacing_slider, 
                                 image_upload, background_upload, paper_size_dropdown, background_color_dropdown], 
                         outputs=gr.Image(type="filepath"), 
                         title="Настройка параметров изображения", 
                         live=True)

# Запуск интерфейса
if __name__ == "__main__":
    interface.launch()
