from cameo import Cameo

if __name__ == "__main__":
    camera = Cameo('Cameo', _shouldMirrorPreview=True)
    Cameo.run(camera)