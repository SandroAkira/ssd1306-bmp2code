#!/usr/bin/python

import sys, getopt, os

image_width = 0
image_height = 0

def bytes2int(str):
 return int(str.encode('hex'), 16)

def read_rows(path):
    global image_width
    global image_height

    image_file = open(path, "rb")
    # image offset
    image_file.seek(10)
    bmp_last = image_file.read(1)
    bmp_start = image_file.read(1) + bmp_last
    # print int(bmp_start.encode('hex'), 16)
    image_file.seek(18)
    image_width = int(image_file.read(1).encode('hex'),16)
    image_file.seek(22)
    image_height = int(image_file.read(1).encode('hex'),16)

    # print str(image_width) + "x" + str(image_height)

    # Blindly skip the BMP header.
    image_file.seek(int(bmp_start.encode('hex'),16))

    # We need to read pixels in as rows to later swap the order
    # since BMP stores pixels starting at the bottom left.
    rows = []
    row = []
    bb = []
    pixel_index = 0

    while True:
        # if pixel_index == str(int(image_width.encode('hex'),16)):
        if pixel_index > 0 and pixel_index % image_width == 0:
            pixel_index = 0
            rows.insert(0, row)
            if len(row) != image_width:
                raise Exception("Row length is not " + image_width.encode('dec') + "*3 but " + str(len(row)) + " / 3.0 = " + str(len(row) / 3.0))
            row = []
        pixel_index += 1

        r_string = image_file.read(1)

        if len(r_string) != 0:
            if len(row) > 0 and len(row) % image_width == 0:
                print
            # print '0x'+bw.encode('hex')+', ',

        if len(r_string) == 0:
            # This is expected to happen when we've read everything.
            if len(rows) != image_height:
                print "Warning!!! Read to the end of the file at the correct sub-pixel (red) but we've not read 36 rows! (" + str(len(rows)) + ")"
            break

        r = ord(r_string)

        row.append(r)

        # print pixel_index,

    image_file.close()

    return rows

def repack_sub_pixels(rows, image_width, image_height):
    print "Repacking pixels..."
    sub_pixels = []
    for row in zip(*rows):
        for sub_pixel in row:
            sub_pixels.append(sub_pixel)
    diff = len(sub_pixels) - image_width * image_height
    print "Packed", len(sub_pixels), "sub-pixels."
    if diff != 0:
        print "Error! Number of sub-pixels packed does not match 60*36: (" + str(len(sub_pixels)) + " - 60 * 36 = " + str(diff) +")."

    return sub_pixels

def convert_bytes(sub_pixels, image_width, image_height):
    counter = 0
    rowidx = 0
    pixel = 0b0
    pixels = []
    remain_bits = image_height % 8
    for byte in sub_pixels:
        counter += 1
        rowidx += 1
        pixel = pixel >> 1
        if byte > 0:
            pixel = pixel & 0b01111111
        else:
            pixel = pixel | 0b10000000
        # print pixel,
        if counter == 8:
            # print "\npixel:",
            # print pixel
            # pixels.append(hex(pixel))
            px = "0x%02X" % pixel
            # print px
            pixels.append(px)
            pixel = 0
            counter = 0
        if remain_bits > 0:
            if rowidx == image_height:
                # print "\npixel:",
                # print pixel
                pixel = pixel >> remain_bits
                px = "0x%02X" % pixel
                pixels.append(px)
                pixel = 0
                counter = 0
                rowidx = 0
    return pixels

def main(argv):
    inputfile = ''
    outputfile = ''

    if len(sys.argv) > 1:
        inputfile = str(sys.argv[1])
    else:
        print 'readbmpbw.py <inputfile.bmp>'
        print
        sys.exit(2)

    # try:
    #   opts, args = getopt.getopt(argv,"hi:",["ifile="])
    # except getopt.GetoptError:
    #   print 'readbmpbw.py -i <inputfile>'
    #   sys.exit(2)
    # for opt, arg in opts:
    #   if opt == '-h':
    #      print 'readbmpbw.py -i <inputfile>'
    #      sys.exit()
    #   elif opt in ("-i", "--ifile"):
    #      inputfile = arg
    # print 'Input file is "', inputfile

    if not os.path.isfile(inputfile):
        print 'Input file', inputfile, 'does not exist.'
        sys.exit(2)

    rows = read_rows(inputfile)

    filename = os.path.split(inputfile)

    # irows = []
    # for i in range(len(rows)):
    #     for j in range(len(rows[i])):
    #         irows[i][j] = rows[i][j]
    # # irows = [[rows[i][j] for i in range(len(rows))] for j in range (len(rows[i]))]
    #
    # print irows
    # This list is raw sub-pixel values. A red image is for example (255, 0, 0, 255, 0, 0, ...).
    sub_pixels = repack_sub_pixels(rows, image_width, image_height)

    # print "sub_pixels:", sub_pixels

    pixels = convert_bytes(sub_pixels, image_width, image_height)

    # print "pixels:", pixels

    #
    # Print Formatted Output
    #
    print
    print "/* res: ",
    print image_width,"x",image_height,
    print "  */"
    print "PROGMEM const char", os.path.splitext(os.path.split(inputfile)[1])[0], "[] = {"
    counter = 0
    for px in pixels:
        counter += 1
        if counter == 1:
            print "  ",
        print px +', ',
        if counter % 16 == 0:
            print
            counter = 0
    print
    print "}"
    print

if __name__ == "__main__":
   main(sys.argv[1:])
