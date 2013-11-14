"""
Support for reading and writing Ned Graphics pattern (.PAT) files. (Note: 
There is no support for compressed .PAT files.)

Examples >>
    import pat

    # Load a pattern file
    f = open('example.pat', 'rb')
    pattern = loads(f.read())
    f.close()
    
    # Save pattern file as an image
    pattern.to_image().save('example.png')
    
    # Save pattern file as an image converted to a full repeat
    pattern.to_image(True).save('example_full_repeat.png')
    
    # Create a pattern from an image
    pattern = Pattern.from_image(Image.open('example.png'), 162)
    
    # Save a pattern file
    f = open('example.pat', 'wb')
    f.write(dumps(pattern))
    f.close()
    
"""

import ctypes
import Image
import ImageChops
import struct

__all__ = [
    # Classes
    'Pattern',
    
    # Functions
    'dumps',
    'loads'
    ]


class Pattern(object):
    """
    A pattern.
    """
    
    def __init__(self, size, drop, channels, bitmap):
        self.size = size
        self.drop = drop
        self.channels = channels
        self.bitmap = bitmap
    
    def to_image(self, full_repeat=False):
        """
        Convert the pattern to an image. Optional you can specify to convert
        the image to a full repeat (based on the drop value).
        """
        
        # Calculate the repeats needed if creating a full repeat
        repeats = 1
        if full_repeat:
            repeats = int(self.size[1] / self.drop)
        
        # Create the image
        image = Image.new('RGB', (self.size[0] * repeats, self.size[1]))
        pixels = [self.channels[bit] for bit in self.bitmap]
        pattern = Image.new('RGB', self.size)
        pattern.putdata(pixels)
        
        # Paste the pattern on to the image
        for repeat in range(0, repeats):
            image.paste(pattern, (self.size[0] * repeat, 0))
            pattern = ImageChops.offset(pattern, 0, self.drop)
        
        return image
        
    @classmethod
    def from_image(cls, image, drop=None):
        """
        Convert an image to a pattern, if drop is not specified it is set to
        the height of the image (full drop).
        """
        
        # Extract unique colours to create channels from
        channels = [colour[1] for colour in image.getcolors()]
        
        # Convert pixel data to bitmap
        bitmap = [channels.index(pixel) for pixel in image.getdata()]
        
        return Pattern(image.size, drop or image.size[1], channels, bitmap)


def loads(s):
    """Load a pattern from a string"""
    
    # Extract dimensions
    width = struct.unpack_from('>H', s, 0)[0]
    height = struct.unpack_from('>H', s, 2)[0]
    drop = struct.unpack_from('<H', s, 30)[0]
    
    # Extract colour channels
    greens = struct.unpack_from('256B', s, 512)
    reds = struct.unpack_from('256B', s, 768)
    blues = struct.unpack_from('256B', s, 1024)
    channels = [(reds[i], greens[i], blues[i]) for i in range(0, 256)]
    
    # Extract the bitmap data
    bitmap = struct.unpack_from(str(width * height) + 'B', s, 1536)
    
    # Create and return a pattern instance
    return Pattern((width, height), drop, channels, list(bitmap))

def dumps(pattern):
    """Save a pattern to a string"""
    
    buf = ctypes.create_string_buffer(1536 + len(pattern.bitmap))
    
    # Write dimensions
    struct.pack_into('>H', buf, 0, pattern.size[0])
    struct.pack_into('>H', buf, 2, pattern.size[1])
    struct.pack_into('<H', buf, 30, pattern.drop)
    
    # Write colour channels (Green, Red, Blue)
    for i, channel in enumerate(pattern.channels):
        struct.pack_into('B', buf, 513 + i, channel[1])
        struct.pack_into('B', buf, 768 + i, channel[0])
        struct.pack_into('B', buf, 1025 + i, channel[2])
    
    # Write the bitmap
    struct.pack_into(str(len(pattern.bitmap)) + 'B', buf, 1536, *pattern.bitmap)
    
    return buf
