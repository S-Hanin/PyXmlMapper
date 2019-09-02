#!python
# -*- coding: utf8 -*-
import argparse
import glob
import os
import zipfile
from PyXmlMapper import xml2class

interface = argparse.ArgumentParser(description="Creates models from xml for PyXmlMapper lib")
interface.add_argument("in_dir", help="input directory, default - current directory", default="./")
interface.add_argument("out_dir", help="output directory, default - current directory", default="./")
interface.add_argument("-z", "--from_zip", help="gets files from zip archive", action="store_true")


def main():
    args = interface.parse_args()
    in_path = args.in_dir
    out_path = args.out_dir
    extension = "*.zip" if args.from_zip else "*.xml"
    in_path = os.path.join(in_path, extension)
    print("in_dir: {}, out_dir: {}".format(in_path, out_path))
    for item in glob.glob(in_path):
        print("processing {}".format(item))
        if args.from_zip:
            if zipfile.is_zipfile(item):
                xml_zip = zipfile.ZipFile(item)
                for item in xml_zip.namelist():
                    if not item.endswith("xml"):
                        continue
                    print(item)
                    xml_io = xml_zip.open(item)
                    models = xml2class.create_classes_from_file(xml_io)
                    py_filename = item + ".py"
                    with open(os.path.join(out_path, py_filename), "w") as fh:
                        fh.write(models)
        else:
            models = xml2class.create_classes_from_file(item)
            py_filename = item + ".py"
            with open(os.path.join(out_path, py_filename), "w") as fh:
                fh.write(models)


if __name__ == "__main__":
    main()
