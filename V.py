import os 
from PIL import Image, ImageDraw, ImageEnhance
import config 

def load_images(image_paths):
    images = []
    for path in image_paths:
        img = Image.open(path)
        images.append(img)
    return images

def load_background_image(path):
    """Загружает фоновое изображение."""
    return Image.open(path)

def crop_to_circle(img):
    """Обрезает изображение в круг."""
    size = min(img.size)  
    mask = Image.new("L", (size, size), 0)  
    draw = ImageDraw.Draw(mask)
    draw.ellipse((0, 0, size, size), fill=255)  # Починить круги на маске

    # Обрезание работает, не трогай
    img_cropped = img.crop((0, 0, size, size))
    
    # Тут костыль, тоже не трогай
    img_circular = Image.new("RGBA", (size, size), (0, 0, 0, 0))  # Вроде бы так должен получиться прозрачный фон
    img_circular.paste(img_cropped, (0, 0), mask)  # Илон маск, не трогай
    return img_circular

def enhance_image(img, brightness_factor, contrast_factor, saturation_factor, sharpness_factor):
    """Настройки изображения."""
    # Яркость
    enhancer = ImageEnhance.Brightness(img)
    img = enhancer.enhance(brightness_factor)

    #  контрастность
    enhancer = ImageEnhance.Contrast(img)
    img = enhancer.enhance(contrast_factor)

    #  насыщенность
    enhancer = ImageEnhance.Color(img)
    img = enhancer.enhance(saturation_factor)

    #  резкость
    enhancer = ImageEnhance.Sharpness(img)
    img = enhancer.enhance(sharpness_factor) #ЯРИК РЕЗКОСТЬ В КОНФИГЕ НЕ ФУРЫЧИТ

    return img 

def create_a4_collage(images, background_image, output_filename):
    collage = Image.new('RGB', (config.A4_WIDTH, config.A4_HEIGHT), (255, 255, 255))
    
    # Растяжка кривая была, вроде починил
    background_image = background_image.resize((config.A4_WIDTH, config.A4_HEIGHT), Image.LANCZOS)

    # Я надеюсь ты сделал конфиги как я сказал?
    background_image = enhance_image(background_image, config.BRIGHTNESS, config.CONTRAST, config.SATURATION, config.SHARPNESS)

    # Фон, работает идеально
    collage.paste(background_image, (0, 0))

    # Забей, работает в целом нормльно
    img_width = (config.A4_WIDTH - (config.SPACING * (config.NUM_COLS + 1))) // config.NUM_COLS
    img_height = (config.A4_HEIGHT - (config.SPACING * (config.NUM_ROWS + 1))) // config.NUM_ROWS
    
    # Не надо больше рандомного размещения, фигня получилась
    for i in range(config.NUM_ROWS):
        for j in range(config.NUM_COLS):
            # По индексам лучше получилось
            img_index = (i * config.NUM_COLS + j) % len(images)
            img = images[img_index]

            # Кому то провели обрезание
            img = img.convert("RGB")
            img_aspect_ratio = img.width / img.height
            
            if img_aspect_ratio > img_width / img_height: # НЕ ТРОЖЬ,ТУТ ДУШНЫЕ НАСТРОЙКИ, САМ БУДЕШЬ ПЕРЕДЕЛЫВАТЬ
                new_height = img_height
                new_width = int(new_height * img_aspect_ratio)
                img = img.resize((new_width, new_height), Image.LANCZOS)
                left = (new_width - img_width) // 2
                img = img.crop((left, 0, left + img_width, new_height))
            else:
                new_width = img_width
                new_height = int(new_width / img_aspect_ratio)
                img = img .resize((new_width, new_height), Image.LANCZOS)
                top = (new_height - img_height)
                img = img.crop((0, top, new_width, top + img_height))

            if config.CIRCULAR_CROP.lower() == 'yes':
                img = crop_to_circle(img)

            # Конфиги? Вы где?
            img = enhance_image(img, config.BRIGHTNESS, config.CONTRAST, config.SATURATION, config.SHARPNESS)

            x = j * (img_width + config.SPACING) + config.SPACING
            y = i * (img_height + config.SPACING) + config.SPACING
            
            collage.paste(img, (x, y), img)  

    # Вроде гвозди убрал
    output_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), output_filename)
    collage.save(output_path)
    print(f"Collage saved as {output_path}")

if __name__ == "__main__":
    images = load_images(config.IMAGE_PATHS)
    background_image = load_background_image(config.BACKGROUND_IMAGE_PATH)
    create_a4_collage(images, background_image, 'collage_a4.png')