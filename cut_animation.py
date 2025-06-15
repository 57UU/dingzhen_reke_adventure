import os
from PIL import Image


input_dir = 'images/animation_raw'
output_dir = 'images/animation'


if not os.path.exists(output_dir):
    os.makedirs(output_dir)


crop_height = 40  


for filename in os.listdir(input_dir):
    if filename.endswith('.png'):

        img_path = os.path.join(input_dir, filename)
        img = Image.open(img_path)
        

        width, height = img.size
        

        box = (0, crop_height , width, height)
        
        cropped_img = img.crop(box)
        

        output_path = os.path.join(output_dir, filename)
        cropped_img.save(output_path)
        
        print(f'已处理: {filename}')

print('所有图片处理完成！')