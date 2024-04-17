from cameo import CameoDepth

if __name__ == "__main__":
    camera = CameoDepth('Cameo', _shouldMirrorPreview=True)
    CameoDepth.run(camera)