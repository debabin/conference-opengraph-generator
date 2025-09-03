#!/usr/bin/env python3

import argparse
import json
import os
import sys
from pathlib import Path
import requests
from PIL import Image, ImageDraw, ImageFont
import io

def download_avatar(url):
    response = requests.get(url, timeout=10)
    avatar = Image.open(io.BytesIO(response.content))
    return avatar.convert('RGBA')


def prepare_avatar(avatar, size=(150, 150)):
    avatar = avatar.resize(size, Image.Resampling.LANCZOS)
    
    # Создаем круглую маску
    mask = Image.new('L', size, 0)
    mask_draw = ImageDraw.Draw(mask)
    mask_draw.ellipse((0, 0) + size, fill=255)
    
    # Применяем маску
    output = Image.new('RGBA', size, (0, 0, 0, 0))
    output.paste(avatar, (0, 0))
    output.putalpha(mask)
    
    # Добавляем розовую рамку
    border_size = 4
    border_color = (255, 255, 255, 255)  # Розовый цвет
    
    bordered = Image.new('RGBA', (size[0] + border_size * 2, size[1] + border_size * 2), (0, 0, 0, 0))
    border_draw = ImageDraw.Draw(bordered)
    border_draw.ellipse((0, 0, size[0] + border_size * 2, size[1] + border_size * 2), fill=border_color)
    
    bordered.paste(output, (border_size, border_size), output)
    return bordered


def generate_image(speaker, fonts, logo_url):
    template_path = 'templates/template.png'
    template = Image.open(template_path).convert('RGBA')
    img = template.copy()
    draw = ImageDraw.Draw(img)
    
    name = speaker.get('name', 'Имя не указано')
    job_title = speaker.get('job_title', 'Должность не указана')
    talk_title = speaker.get('talk_title', 'Название доклада не указано')
    avatar_url = speaker.get('avatar_url', '')
    
    img_width = img.width  # 1920
    img_height = img.height  # 1061
    
    content_margin = 220

    title_y = 275
    title_line_width = img_width - (content_margin * 2)
    
    words = talk_title.split()
    lines = []
    current_line = []

    for word in words:
        line = ' '.join(current_line + [word])
        title_line_bbox = draw.textbbox((0, 0), line, font=fonts['title'])
        current_line_width = title_line_bbox[2] - title_line_bbox[0]
        
        if current_line_width <= title_line_width:
            current_line.append(word)
        else:
            if current_line:
                lines.append(' '.join(current_line))
                current_line = [word]
            else:
                lines.append(word)
    
    if current_line:
        lines.append(' '.join(current_line))
    
    line_height = 100
    title_block_height = 0
    for i, line in enumerate(lines[:4]):
        y_pos = title_y + i * line_height
        draw.text((content_margin, y_pos), line, font=fonts['title'], fill=(255, 255, 255))
        title_block_height = y_pos + line_height - title_y
    
    bottom_section_y = 800
    
    avatar_size = 120
    
    if avatar_url:
        avatar = download_avatar(avatar_url)
        avatar_prepared = prepare_avatar(avatar, (avatar_size, avatar_size))
        img.paste(avatar_prepared, (content_margin, bottom_section_y), avatar_prepared)

  
    speaker_x = content_margin + avatar_size + 40
    speaker_name_y = bottom_section_y

    draw.text((speaker_x, speaker_name_y), name, font=fonts['name'], fill=(255, 255, 255))
    
    name_bbox = draw.textbbox((0, 0), name, font=fonts['name'])
    name_height = name_bbox[3] - name_bbox[1]

    speaker_job_y = speaker_name_y + name_height + 20
    draw.text((speaker_x, speaker_job_y), job_title, font=fonts['job'], fill=(180, 180, 180))

    if logo_url:
        try:
            if logo_url.startswith('data:image/svg+xml;base64,'):
                import base64
                
                # Декодируем base64
                svg_data = base64.b64decode(logo_url.split(',')[1]).decode('utf-8')
                
                # Загружаем SVG напрямую как изображение через PIL с помощью cairosvg
                import cairosvg
                png_data = cairosvg.svg2png(bytestring=svg_data.encode('utf-8'), output_width=150, output_height=150)
                logo = Image.open(io.BytesIO(png_data)).convert('RGBA')
            elif logo_url.startswith('data:image/'):
                # Для других base64 изображений (PNG, JPG и т.д.)
                import base64
                image_data = base64.b64decode(logo_url.split(',')[1])
                logo = Image.open(io.BytesIO(image_data)).convert('RGBA')
                logo = logo.resize((150, 150), Image.Resampling.LANCZOS)
            else:
                # Если это обычный URL, загружаем как раньше
                response = requests.get(logo_url, timeout=10)
                response.raise_for_status()
                logo = Image.open(io.BytesIO(response.content)).convert('RGBA')
                logo = logo.resize((150, 150), Image.Resampling.LANCZOS)
            
            # Позиционируем логотип в правом верхнем углу
            logo_x = img_width - 150 - 50  # 50px отступ от края
            logo_y = 50  # 50px отступ сверху
            
            img.paste(logo, (logo_x, logo_y), logo)
            
        except Exception as e:
            print(f"Не удалось загрузить логотип: {e}")


    output_dir = Path("output")
    output_dir.mkdir(exist_ok=True)
    output_filename = f"{name.replace(' ', '_').replace('/', '_')}_opengraph.png"
    output_path = output_dir / output_filename
    
    img.save(output_path, 'PNG')
    return str(output_path)


def process_speakers(file, fonts):
    with open(file, 'r', encoding='utf-8') as file_data:
        data = json.load(file_data)

    created_images = []
    for speaker in data['speakers']:
        result = generate_image(speaker, fonts, data['logo'])
        created_images.append(result)
        
    return created_images


def main():
    parser = argparse.ArgumentParser(description='Генератор OpenGraph картинок для конференций')
    parser.add_argument('file', help='Путь к JSON файлу')
    parser.add_argument('--font', default='geist', choices=['geist', 'roboto'], help='Шрифт (по умолчанию: geist)')
    
    args = parser.parse_args()

    if not os.path.exists(args.file):
        print(f"JSON файл '{args.file}' не найден")
        sys.exit(1)
    
    fonts_dir = Path("fonts")
    fonts = {
        'job': ImageFont.truetype(str(fonts_dir / f"{args.font}/regular.ttf"), 36),
        'name': ImageFont.truetype(str(fonts_dir / f"{args.font}/bold.ttf"), 48),
        'title': ImageFont.truetype(str(fonts_dir / f"{args.font}/regular.ttf"), 90)
    }

    created_images = process_speakers(args.file, fonts)
    print(f"\nСоздано {len(created_images)} картинок:")


main()