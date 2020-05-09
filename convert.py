# -*- coding: utf-8 -*-

from xml.dom import minidom
import os, re
import glob
import argparse
from collections import OrderedDict

def convert_coordinates(size, box):
    dw = 1.0/size[0]
    dh = 1.0/size[1]
    x = (box[0]+box[1])/2.0
    y = (box[2]+box[3])/2.0
    w = box[1]-box[0]
    h = box[3]-box[2]
    x = x*dw
    w = w*dw
    y = y*dh
    h = h*dh
    return (x,y,w,h)


def convert_xml2yolo(dir_in, dir_out, lbl_out):

    labels = OrderedDict()
    xml_files = [x for x in glob.glob(f"{dir_in}/*.xml")]
    
    for fname in xml_files:
        
        xmldoc = minidom.parse(fname)
        fname_out = re.sub(dir_in, dir_out, fname)
        fname_out = fname_out[:-4] + '.txt'

        with open(fname_out, "w") as f:

            itemlist = xmldoc.getElementsByTagName('object')
            size = xmldoc.getElementsByTagName('size')[0]
            width = int((size.getElementsByTagName('width')[0]).firstChild.data)
            height = int((size.getElementsByTagName('height')[0]).firstChild.data)

            for item in itemlist:
                # get class label
                classid =  (item.getElementsByTagName('name')[0]).firstChild.data
                if classid not in labels:
                    labels[classid] = len(labels) + 1
                lbl = str(labels[classid])

                # get bbox coordinates
                xmin = ((item.getElementsByTagName('bndbox')[0]).getElementsByTagName('xmin')[0]).firstChild.data
                ymin = ((item.getElementsByTagName('bndbox')[0]).getElementsByTagName('ymin')[0]).firstChild.data
                xmax = ((item.getElementsByTagName('bndbox')[0]).getElementsByTagName('xmax')[0]).firstChild.data
                ymax = ((item.getElementsByTagName('bndbox')[0]).getElementsByTagName('ymax')[0]).firstChild.data
                b = (float(xmin), float(xmax), float(ymin), float(ymax))
                bb = convert_coordinates((width,height), b)

                f.write(lbl + " " + " ".join([("%.6f" % a) for a in bb]) + '\n')

    if lbl_out is not None:
        with open(lbl_out, 'w') as f_out:
            for l in list(labels.keys()):
                f_out.write(l + '\n')

def initialize_params():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--label_directory_in',
        help="Directory to find .xml files",
        required=True,
    )
    parser.add_argument(
        '--label_directory_out',
        help="Directory to output yolo files. Defaults to same directory as input",
        required=False
    )
    parser.add_argument(
        '--label_file_out',
        help="Path to where to save labels.txt, if desired.",
        required=False
    )
    return parser.parse_args()


def main():
    args = initialize_params()
    dir_in = os.path.expanduser(args.label_directory_in)
    if args.label_directory_out is not None:
        dir_out = os.path.expanduser(args.label_directory_out)
    else:
        dir_out = dir_in
    if args.label_file_out is not None:
        lbl_out = os.path.expanduser(args.label_file_out)
    else:
        lbl_out = None
        
    convert_xml2yolo(dir_in, dir_out, lbl_out)


if __name__ == '__main__':
    main()
