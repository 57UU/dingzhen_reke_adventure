import os
from PIL import Image

# 输入和输出目录
input_dir = 'images/animation_raw'
output_dir = 'images/animation'

# 创建输出目录（如果不存在）
if not os.path.exists(output_dir):
    os.makedirs(output_dir)

# 指定要保留的高度（像素）
crop_height = 40  # 可以根据需要调整这个值

# 处理所有PNG文件
for filename in os.listdir(input_dir):
    if filename.endswith('.png'):
        # 打开图片
        img_path = os.path.join(input_dir, filename)
        img = Image.open(img_path)
        
        # 获取图片尺寸
        width, height = img.size
        
        # 计算裁切区域（保留底部指定高度）
        box = (0, crop_height , width, height)
        
        # 裁切图片
        cropped_img = img.crop(box)
        
        # 保存裁切后的图片
        output_path = os.path.join(output_dir, filename)
        cropped_img.save(output_path)
        
        print(f'已处理: {filename}')

print('所有图片处理完成！')