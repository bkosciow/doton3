from kivy.uix.image import Image
from kivy.lang import Builder
import pathlib

Builder.load_file(str(pathlib.Path(__file__).parent.absolute()) + pathlib.os.sep + 'image_rotate.kv')


class ImageRotate(Image):
    pass
