import struct

# COMPSCI 365
# Spring 2020
# YOUR NAME HERE
# Assignment 3: JPEG Manipulation

# Complete the relevant functions.
# Make sure to test your implementations.
# You can import any standard library.
# You can define any new function you want.

import tags



def carve_jpeg(inputFile):
    """
    Description: Read the input file and extract ANY/ALL valid
    # sequences of bytes that conform to the JPEG standard.
    # The function should return a list of bytes objects, where each
    # bytes object is the extracted sequence of bytes corresponding
    # to one JPEG file. The ordering of the list does not matter. For
    # example, if l_1 = b'\xff\xd8\xff\xe0\x00\x10\x4a...', then
    # the list returned would be [l_1, l_2, ...]. If there is
    # just one valid JPEG file, then it would be [l_1]. If there are
    # no valid JPEG files, return an empty list.
    Input: string inputFile
    Output: list of bytes objects
    Example 1: carve_jpeg("main.py") = []
    Example 2: carve_jpeg("samples/sample1.jpg") = 
    # [b'\xff\xd8\xff\xe0...\xff\xd9', b'\xff\xd8\xff...\xff\xd9']
    """
    with open(inputFile, 'rb') as inFile:
        bytes_list = []

        bFile = inFile.read()
        jpg_start = bFile.find(bytes([255,216]))
        jpg_end = bFile.find(bytes([255, 217]))
        i = 0
        while jpg_start != -1 and jpg_end != -1: #while loop continuously checks that there are still remaining jpg files
            new_file = bFile[jpg_start: jpg_end + 2] #we find the corresponding jpg file based on start and end indives
            bytes_list.append(new_file)
            bFile = bFile[jpg_start + 2:]
            #a = len(list(remaining))

            old = jpg_end
            #remaining = bFile[jpg_start + 2:]
            #a = len(list(remaining))
            #remaining = bFile[jpg_start + 2:]
            jpg_start = bFile.find(bytes([255, 216]))
            #remaining = bFile[jpg_end + 2:]
            
            jpg_end = bFile[old + 2:].find(bytes([255,217]))
            if jpg_start == -1 or jpg_end == -1:
                break
            #bytes_list.append(new_file)
            
    return bytes_list

def parse_exif(inputBytes):
    """
    Description: Given a sequence of bytes inputBytes that is
    # interpreted as a JPEG file, parse through the bytes to find
    # ANY/ALL EXIF segments. For each EXIF segment:
    # 1. Determine its endianness and handle data accordingly.
    # 2. For each IFD, determine the number of entries. Then,
    # for each entry in each IFD:
    #
    # 2.a. Extract the tag and value IF the tag is in tags.TAGS, AND
    ## IF the tag's format is in [1, 2, 3, 4, 5, 7].
    # 2.b. The tag and value should be stored in a tuple (TagName, Value),
    ## noting that if the value has multiple components then store them
    ## in a list (otherwise just as a single variable),
    ## where the value type corresponds for the following formats:
    ## Formats 1, 3, 4: int
    ## Formats 2, 5: str (for Format 5, use "x/y"; for Format 2, strip
    ## the trailing NULL byte)
    ## Format 7: bytes
    ## The tag names can be obtained from tags.TAGS.
    # 2.c. Add the tuple to a list that corresponds to the IFD.
    #
    # 3. Each list of extracted tuples should be stored as a value
    # in a dictionary, where the key is the offset of the IFD starting byte
    # (i.e. the first byte in the two bytes that specify the number of
    # entries that the IFD has) as an integer.
    # 4. Return this dictionary. If there are no entries in a given
    # IFD to extract, use an empty list in the dictionary. If there
    # are no IFDs, then return an empty dictionary.
    Input: bytes object
    Output: dictionary
    Example: parse_exif(carve_jpeg("samples/exif1.jpg")[0]) =
    # { 0x14: [ ("ImageDescription", " " * 31), ("Make", "NIKON"), ... ],
    # 0x1172: [ ("Compression", 6), ("XResolution", "72/1"), ("YResolution", "72/1"), ...],
    # ... }
    """
    exif_dict = {}
    entry = []

    exif_start = inputBytes.find(bytes([69, 120, 105, 102, 00, 00]))
    
    if exif_start == -1:
        return {}
    
    while exif_start != -1:
        endianness = inputBytes[exif_start + 6 : exif_start + 8] # the next 4 bytes following exif start signature are the endianness bytes
        lookahead_index = exif_start + 6
        if endianness[0] == 73 and endianness[1] == 73:
            #little endian case <
            exif_id = inputBytes[exif_start + 8]
            starting_offset_bytes = inputBytes[exif_start + 10 : exif_start + 14]
            starting_offset = struct.unpack("<I", starting_offset_bytes)[0]
            if exif_id != 42:
                #invalid exiif file
                pass
            x = lookahead_index + starting_offset #placeholder
            #a = inputBytes[x : x + 2 ]
            num_entries = struct.unpack("<H",  inputBytes[x : x + 2 ])[0]
            block_start = x + 2
            block_end = (12 * num_entries) + (x + 2)
            ifd_block = inputBytes[block_start : block_end]
            for i in range(len(ifd_block) + 1):
                if i == 0:
                    continue
                if i % 12 == 0:
                    data = handle_line('little', ifd_block[i-12 : i], inputBytes, lookahead_index)
                    entry.append(data)
            exif_dict[(block_start - 2)] = entry
            next_block = inputBytes[block_end : block_end + 4]
            while struct.unpack("<I", next_block)[0] != 0:
                entry = []
                x = lookahead_index + struct.unpack("<I", next_block)[0]
                num_entries = struct.unpack("<H",  inputBytes[x : x + 2 ])[0]
                block_start = x + 2
                block_end = (12 * num_entries) + (x + 2)
                ifd_block = inputBytes[block_start : block_end]
                next_block = inputBytes[block_end : block_end + 4]
                for i in range(len(ifd_block) + 1):
                    if i == 0:
                        continue
                    if i % 12 == 0:
                        data = handle_line('little', ifd_block[i-12 : i], inputBytes, lookahead_index)
                        entry.append(data)
                exif_dict[(block_start - 2)] = entry
                

        if endianness[0] == 77 and endianness[1] == 77:
            #big endian scenario
            exif_id = inputBytes[exif_start + 9]
            starting_offset_bytes = inputBytes[exif_start + 10 : exif_start + 14]
            starting_offset = struct.unpack(">I", starting_offset_bytes)[0]
            if exif_id != 42:
                #invalid exiif file
                pass
            x = lookahead_index + starting_offset #placeholder
            num_entries = struct.unpack(">H",  inputBytes[x : x + 2 ])[0]
            block_start = x + 2
            block_end = (12 * num_entries) + (x + 2)
            ifd_block = inputBytes[block_start : block_end]
            for i in range(len(ifd_block) + 1):
                if i == 0:
                    continue
                if i % 12 == 0:
                    data = handle_line('big', ifd_block[i-12 : i], inputBytes, lookahead_index)
                    entry.append(data)
            exif_dict[(block_start - 2)] = entry
            next_block = inputBytes[block_end : block_end + 4]
            while struct.unpack(">I", next_block)[0] != 0:
                entry = []
                x = lookahead_index + struct.unpack(">I", next_block)[0]
                num_entries = struct.unpack(">H",  inputBytes[x : x + 2 ])[0]
                block_start = x + 2
                block_end = (12 * num_entries) + (x + 2)
                ifd_block = inputBytes[block_start : block_end]
                next_block = inputBytes[block_end : block_end + 4]
                for i in range(len(ifd_block) + 1):
                    if i == 0:
                        continue
                    if i % 12 == 0:
                        data = handle_line('big', ifd_block[i-12 : i], inputBytes, lookahead_index)
                        entry.append(data)
                exif_dict[(block_start - 2)] = entry
        exif_start = inputBytes[block_end:].find(bytes([69, 120, 105, 102, 00, 00]))

    return exif_dict



##########################
###########################
#############################
#############################

def handle_line(e, line, inputBytes, i):
    size_dict = {1: 1, 2: 1, 3: 2, 4:4, 5: 8, 7: 1}
    if e == 'little':
        tag_id = tags.TAGS[struct.unpack("<H", line[0:2])[0]]
        tag_type = struct.unpack("<H", line[2:4])[0]
        count = struct.unpack("<I", line[4:8])
        data_offset = struct.unpack("<I", line[8:12])[0]
        if size_dict[tag_type] * count[0] > 4:
            data = fetch_data(e, tag_id, tag_type, count[0], inputBytes[i + data_offset : i + data_offset + (size_dict[tag_type] * count[0])])
            return data
        else: 
            if tag_type == 1:
                lst = []
                for i in line[8:8 + count[0]]:
                    lst.append(int.from_bytes(i))
                if len(lst)== 1:
                    return (tag_id,  lst[0])
                return (tag_id,  lst)
            elif tag_type == 2:
                data = struct.unpack("<" + str(count[0]) + "c", line[8:8 + count[0]])
                return (tag_id,  decode(data[:-1]))
            elif tag_type == 3:
                data = struct.unpack("<" + str(count[0]) + "H", line[8 : 8 + (2*count[0])])
                if len(data) > 1:
                    return (tag_id,  list(data))
                return (tag_id,  data[0])
            elif tag_type == 4:
                data = struct.unpack("<I", line[8:12])
                if len(data) > 1:
                    return (tag_id,  list(data))
                return (tag_id,  data[0])
            #elif tag_type = 5:
            #    data = struct.unpack
            elif tag_type == 7:
                return (tag_id,  line[8:8 + count[0]])

    else:
        tag_id = tags.TAGS[struct.unpack(">H", line[0:2])[0]]
        tag_type = struct.unpack(">H", line[2:4])[0]
        count = struct.unpack(">I", line[4:8])
        data_offset = struct.unpack(">I", line[8:12])[0]
        if size_dict[tag_type] * count[0] > 4:
            data = fetch_data(e, tag_id, tag_type, count[0], inputBytes[i + data_offset : i + data_offset + (size_dict[tag_type] * count[0])])
            return data
        else: 
            if tag_type == 1:
                lst = []
                for i in line[8:8 + count[0]]:
                    lst.append(int.from_bytes(i))
                if len(lst)== 1:
                    return (tag_id,  lst[0])
                return (tag_id,  lst)
            elif tag_type == 2:
                data = struct.unpack(">" + str(count[0]) + "c", line[8:8 + count[0]])
                return (tag_id,  decode(data[:-1]))
            elif tag_type == 3:
                data = struct.unpack(">" + str(count[0]) + "H", line[8 : 8 + (2*count[0])])
                if len(data) > 1:
                    return (tag_id,  list(data))
                return (tag_id,  data[0])
            elif tag_type == 4:
                data = struct.unpack(">I", line[8:12])
                if len(data) > 1:
                    return (tag_id,  list(data))
                return (tag_id,  data[0])
            #elif tag_type = 5:
            #    data = struct.unpack
            elif tag_type == 7:
                return (tag_id,  line[8:8 + count[0]])

def fetch_data(e, tag_id, tag_type, count, bits):
    if e == 'little':
        if tag_type == 1:
            lst = []
            for i in bits:
                lst.append(int.from_bytes(i))
            return (tag_id,  lst)
        elif tag_type == 2:
            data = struct.unpack("<" + str(count) + "c", bits)
            return (tag_id,  decode(data[:-1]))
        elif tag_type == 3:
            data = struct.unpack("<" + str(count) + "H", bits)
            if len(data) > 1:
                return (tag_id,  list(data))
            return (tag_id,  data[0])
        elif tag_type == 4:
            data = struct.unpack("<" + str(count) +  "I", bits)
            if len(data) > 1:
                return (tag_id,  list(data))
            return (tag_id,  data[0])
        elif tag_type == 5:
            nums_lst = []
            str_list = []
            for i in range(8 * count):

                if i == 0:
                    continue
                if (i + 1) % 8 != 0:
                    continue
                new_arr = bits[i + 1 - 8: i + 1]
                nums_lst.append(new_arr)
            for i in nums_lst:
                num1 = str(struct.unpack("<I", i[:4])[0])
                num2 = str(struct.unpack("<I", i[4:])[0])
                new_str = num1 + "/" + num2
                if len(nums_lst) == 1:
                    return (tag_id,  new_str)
                else:
                    str_list.append(new_str)
            return (tag_id,  str_list)
        elif tag_type == 7:
            data = []
            for i in bits:
                data.append(i)
            return (tag_id,  data)
                    


    if e == 'big':
        if tag_type == 1:
            lst = []
            for i in bits:
                lst.append(int.from_bytes(i))
            return (tag_id,  lst)
        elif tag_type == 2:
            data = struct.unpack(">" + str(count) + "c", bits)
            return (tag_id,  decode(data[:-1]))
        elif tag_type == 3:
            data = struct.unpack(">" + str(count) + "H", bits)
            if len(data) > 1:
                return (tag_id,  list(data))
            return (tag_id,  data[0])
        elif tag_type == 4:
            data = struct.unpack(">" + str(count) +  "I", bits)
            if len(data) > 1:
                return (tag_id,  list(data))
            return (tag_id,  data[0])
        elif tag_type == 5:
            nums_lst = []
            str_list = []
            for i in range(8 * count):

                if i == 0:
                    continue
                if (i + 1) % 8 != 0:
                    continue
                new_arr = bits[i + 1 - 8: i + 1]
                nums_lst.append(new_arr)
            for i in nums_lst:
                num1 = str(struct.unpack(">I", i[:4])[0])
                num2 = str(struct.unpack(">I", i[4:])[0])
                new_str = num1 + "/" + num2
                if len(nums_lst) == 1:
                    return (tag_id,  new_str)
                else:
                    str_list.append(new_str)
            return (tag_id,  str_list)
        elif tag_type == 7:
            data = []
            for i in bits:
                data.append(i)
            return (tag_id,  data)

def decode(bits):
    s = ""
    for i in bits:
        s += i.decode("utf-8")
    return s

#print(carve_jpeg("samples/exif1.jpg")[1][-1])
#print(len(carve_jpeg("samples/exif1.jpg")))
#print(parse_exif(carve_jpeg("samples/exif1.jpg")[0]))

