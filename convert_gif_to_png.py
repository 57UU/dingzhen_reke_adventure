from PIL import Image
import os

def convert_gif_to_png(gif_path):

    with Image.open(gif_path) as im:

        output_dir = os.path.splitext(gif_path)[0]
        os.makedirs(output_dir, exist_ok=True)
        

        frame_count = 0
        while True:
            try:

                output_path = os.path.join(output_dir, f"{frame_count}.png")
                im.save(output_path)
                frame_count += 1
                

                im.seek(im.tell() + 1)
            except EOFError:
                break  

if __name__ == "__main__":

    images_dir = os.path.join(os.path.dirname(__file__), "images")
    for filename in os.listdir(images_dir):
        if filename.lower().endswith('.gif'):
            gif_path = os.path.join(images_dir, filename)
            convert_gif_to_png(gif_path)
            print(f"已转换: {filename}")