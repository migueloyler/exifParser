import argparse
import jpeg
import wav
from os import path

if __name__ == "__main__":

    p = argparse.ArgumentParser()
    p.add_argument("file", type=str, help="name/path of the input file")
    p.add_argument("-w", action="store_true", help="extract and parse WAV files")
    p.add_argument("-j", action="store_true", help="extract and parse JPEG files")
    args = p.parse_args()

    if path.exists(args.file):
        if not path.isfile(args.file):
            raise Exception("Given path is not a file!")
    else:
        raise Exception("Given path does not exist!")

    if args.w:
        carved = wav.carve_wav(args.file)
        print("List of Sizes of Carved WAVs: %s" % ([len(x) for x in carved]))
        for i, x in enumerate(carved):
            print("Parsed WAV %s Headers: %s" % (i, wav.parse_wav_header(carved[i])))

    if args.j:
        carved = jpeg.carve_jpeg(args.file)
        print("List of Sizes of Carved JPEGs: %s" % ([len(x) for x in carved]))
        for i, x in enumerate(carved):
            print("Parsed JPEG %s EXIF Data: %s" % (i, jpeg.parse_exif(carved[i])))
