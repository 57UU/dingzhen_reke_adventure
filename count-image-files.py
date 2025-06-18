from pathlib import Path

IMAGE_FOLDER = Path(__file__).parent / 'images'

def count_image_files(directory):

    file_count = sum(1 for file in directory.rglob('*') if file.is_file())
    return file_count

if __name__ == "__main__":
    try:
        total = count_image_files(IMAGE_FOLDER)
        print(f"图片文件夹中共有 {total} 个文件")
    except Exception as e:
        print(f"统计失败: {str(e)}")