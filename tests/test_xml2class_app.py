# -*- coding: utf8 -*-

from pyxmlmapper import xml2class


def main():
    filename = "./purchaseNotice_Moskva_20190829_000000_20190829_235959_daily_002.xml"
    print(xml2class.create_classes_from_file(filename))


if __name__ == "__main__":
    main()
