import struct
# COMPSCI 365
# Spring 2020
# YOUR NAME HERE
# Assignment 3: WAV Manipulation

# Complete the relevant functions.
# Make sure to test your implementations.
# You can import any standard library.
# You can define any new function you want.

# WARNING: As you work through parsing
# the WAV standard, keep the endianness
# of each field in the file header in mind.

def carve_wav(inputFile):
    """
    Description: Read the input file and extract ANY/ALL valid
    # sequences of bytes that conform to the WAV standard. Assume
    # that all WAV file headers will only have three chunks: the
    # RIFF chunk, the fmt chunk (the basic style, not a variant),
    # and the data chunk. That is, the WAV file will be a
    # 44-byte header followed by the audio data. Also assume that
    # all WAV files will follow the WAVE PCM format category (0x0001).
    # The function should return a list of bytes objects, where each
    # bytes object is the extracted sequence of bytes corresponding
    # to one WAV file. The ordering of the list does not matter. For
    # example, if l_1 = b'\x52\x49\x46\x46\x71\xaf\x00\x00...', then
    # the list returned would be [l_1, l_2, ...]. If there is
    # just one valid WAV file, then it would be [l_1]. If there are
    # no valid WAV files, return an empty list.
    Input: string inputFile
    Output: list of bytes objects
    Example 1: carve_wav("main.py") = []
    Example 2: carve_wav("samples/sample1.jpg") = 
    # [bytes([82, 73, 70, 70, 240, 4, 2, 0, 87, 65, 86, ...])]
    """
    with open (inputFile, "rb") as inpt:
        #invalid file
       # wav_size = file_bytes([4 + start : start + 8])
       # WAVEfmt = file_bytes.find(bytes([87, 65, 86, 69, 102, 109, 116, 32]))
      #  if WAVEfmt == -1:
            #invalid file
     #   if WAVEfmt - start != 8:
            #invalid file
     #   data = file_bytes.find(bytes([100, 97, 116, 97])) #the list we input here spells out "data" in ascii
      #  if data == -1:
            #invalid file
       # if data - start != 36:
            #invalid file
        #after all these checks it looks like we found a valid file, now we must grab it
        file_bytes = inpt.read()
        bytes_list = []
        start = file_bytes.find(bytes([82, 73, 70, 70])) #the list we input into this spells out "RIFF" in ascii
        while start != -1:
            wav_file = []
            reader = file_bytes[start:]
            sz = bytearray(reader)[4: 8]
            file_size = struct.unpack("<I", sz)[0]
            data = reader[0: file_size + 8]
            reader = file_bytes[file_size + 8 :]
            bytes_list.append(bytes(data))
            start = reader.find(bytes([82, 73, 70, 70]))
        return bytes_list

def parse_wav_header(inputBytes):
    """
    Description: Given a sequence of bytes inputBytes that is
    # interpreted as a WAV file, parse the header and return
    # the extracted fields. These fields should be returned
    # in a dictionary, where each key is the field name, and
    # the corresponding value is the value found in the WAV
    # header. The values should be parsed according to the
    # WAV standard, and then stored in the dictionary
    # according to the format specified in wav_format.txt. If
    # a field is not included in wav_format.txt, then do not
    # include it in your returned dictionary.
    # If a field cannot be parsed properly, set the corresponding
    # dictionary value to None. If all fields cannot be parsed,
    # such as due to the bytes not being a valid sequence of
    # WAV bytes, or empty bytes object, return None.
    Input: bytes object
    Output: dictionary or None
    Example: parse_wav_header(carve_wav("samples/sample1.jpg")[0]) =
    # {'nChannels': 1, 'samplesPerSecond': 22050, ...}
    """
    #an example  of a wav file being invalid is one that has 0 channels open for example, you can't have
    #you can't have a wave file with zero channels on

    if len(inputBytes) < 44:
        return {}
    output_dict = {}
    channels = struct.unpack("<H", inputBytes[22:24])[0]
    samples = struct.unpack("<I", inputBytes[24:28])[0]
    dataSizeBytes = struct.unpack("<I", inputBytes[4:8])[0]
    averageBytesPerSecond = struct.unpack("<I", inputBytes[28:32])[0]
    blockAlignment = struct.unpack("<H", inputBytes[32:34])[0]
    bitsPerSample = struct.unpack("<H", inputBytes[34:36])[0]
    output_dict['nChannels'] = channels
    output_dict['samplesPerSecond'] = samples
    output_dict['dataSizeBytes'] = dataSizeBytes - 36
    output_dict['averageBytesPerSecond'] = averageBytesPerSecond
    output_dict['blockAlignment'] = blockAlignment
    output_dict['bitsPerSample'] = bitsPerSample
    return output_dict

#print(parse_wav_header(carve_wav("samples/sample1.jpg")[0]))

"""{
'nChannels' : int,
'samplesPerSecond' : int,
'averageBytesPerSecond' : int,
'blockAlignment' : int,
'bitsPerSample' : int,
'dataSizeBytes' : int
}
"""

def pack_wav(audioBytes, fields):
    riff = [82, 73, 70, 70]
    wave = [87, 65, 86, 69]
    chunk = len(audioBytes) + 36
    chunk_hex = "{08x}".format(chunk)
    chunk_size = b2l(8, chunk_hex)
    #chunk_size.append(int(chunk_hex[6:], 16))
    #chunk_size.append(int(chunk_hex[4:6], 16))
    #chunk_size.append(int(chunk_hex[2:4], 16))
    #chunk_size.append(int(chunk_hex[:2], 16))
    fmt = [102, 109, 116, 32]
    subchunk_size = [16, 0, 0, 0]
    audio_fmt = [1, 0]
    #nChannels = fields[0]
    #nChan = []
    nChannels = "{04x}".format(fields[0])
    #nChan.append(int(nChannels[2:], 16))
    #nChan.append(int(nChannels[:2], 16))
    nChan = b2l(4, nChannels)
    sampPS = "{08x}".format(fields[1])
    sPS = b2l(8, sampPS)
    avgB = "{08x}".format(fields[2])
    avgB = b2l(8, avgB)

    block_algn = "{04x}".format(fields[3])
    block_algn = b2l(4, block_algn)

    bPS = "{04x}".format(fields[4])
    bPS = b2l(4, bPS)

    data = [100, 97, 116, 97]

    subchunk2size = "{08x}".format(len(audioBytes))
    subchunk2size = b2l(8, subchunk2size)

    packed_wav = bytes(riff + chunk_size + wave + fmt + subchunk_size + audio_fmt + nChan + sPS + avgB + block_algn + bPS + data + subchunk2size + list(audioBytes))

    return packed_wav
    


def b2l(digits, hex_str):
    output = []
    i = digits
    while i - 2 >= 0:
        output.append(int(hex_str[i - 2 : i], 16))
        i -= 2
    return output
#57 41 56 45

#64 61 74 61

#print(b2l(4, "00ff"))

#print(carve_wav("samples/sample1.jpg"))