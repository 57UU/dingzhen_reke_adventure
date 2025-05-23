from PIL import Image
import os

def convert_gif_to_png(gif_path):
    # 打开GIF文件
    with Image.open(gif_path) as im:
        # 创建输出目录
        output_dir = os.path.splitext(gif_path)[0]
        os.makedirs(output_dir, exist_ok=True)
        
        # 逐帧保存为PNG
        frame_count = 0
        while True:
            try:
                # 保存当前帧
                output_path = os.path.join(output_dir, f"{frame_count}.png")
                im.save(output_path)
                frame_count += 1
                
                # 移动到下一帧
                im.seek(im.tell() + 1)
            except EOFError:
                break  # 到达GIF末尾

if __name__ == "__main__":
    # 处理images目录下的所有GIF文件
    images_dir = os.path.join(os.path.dirname(__file__), "images")
    for filename in os.listdir(images_dir):
        if filename.lower().endswith('.gif'):
            gif_path = os.path.join(images_dir, filename)
            convert_gif_to_png(gif_path)
            print(f"已转换: {filename}")