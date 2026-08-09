
def tif2jpg(tif_path, jpg_path) -> str:
    from PIL import Image
    im = Image.open(tif_path)
    rgb_im = im.convert('RGB')
    rgb_im.save(jpg_path)
    return jpg_path


def base64_to_image(base64_string, pic_path):
    import base64
    from PIL import Image
    from io import BytesIO

    # 解码Base64字符串
    decoded_data = base64.b64decode(base64_string)

    # 将二进制数据转换为图像
    image = Image.open(BytesIO(decoded_data))
    image.save(pic_path)
    print(pic_path, '已保存')
