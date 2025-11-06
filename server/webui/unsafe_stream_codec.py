import io
import struct
from PIL import Image
import numpy as np


class UnsafeStreamCodec:
    def __init__(self, image_quality=100, use_jpeg=True):
        self.use_jpeg = use_jpeg
        self.image_quality = image_quality
        self.cached_size = 0
        self.buffer_count = 1
        self.codec_options = "RequireSameSize"
        self.check_block = (50, 1)
        self.encoded_format = None
        self.encoded_width = 0
        self.encoded_height = 0
        self.encode_buffer = None
        self.decoded_bitmap = None

    def code_image(self, scan0, scan_area, image_size, format, out_stream):
        """
        Encode an image using differential encoding
        """
        # Determine bytes per pixel based on format
        if format in ['RGB', 'BGR']:
            bytes_per_pixel = 3
        elif format in ['RGBA', 'BGRA']:
            bytes_per_pixel = 4
        else:
            raise ValueError(f"Unsupported format: {format}")

        stride = image_size[0] * bytes_per_pixel
        image_size_bytes = stride * image_size[1]

        # If this is the first frame, send the full image
        if self.encode_buffer is None:
            self.encoded_format = format
            self.encoded_width = image_size[0]
            self.encoded_height = image_size[1]
            
            # Create image from raw data
            img_data = np.frombuffer(scan0, dtype=np.uint8)
            if bytes_per_pixel == 3:
                img_data = img_data.reshape((image_size[1], image_size[0], 3))
            else:
                img_data = img_data.reshape((image_size[1], image_size[0], 4))
            
            pil_img = Image.fromarray(img_data, mode='RGB' if bytes_per_pixel == 3 else 'RGBA')
            
            # Compress the image
            buffer = io.BytesIO()
            if self.use_jpeg:
                pil_img.save(buffer, format='JPEG', quality=self.image_quality)
            else:
                pil_img.save(buffer, format='PNG')  # Using PNG as LZW equivalent
            
            compressed_data = buffer.getvalue()
            
            # Write JPEG size and data
            out_stream.write(struct.pack('I', len(compressed_data)))
            out_stream.write(compressed_data)
            
            # Store the buffer for future comparisons
            self.encode_buffer = np.copy(img_data)
            return

        # Check format compatibility
        if self.encoded_format != format:
            raise Exception("PixelFormat is not equal to previous Bitmap")
        
        if self.encoded_width != image_size[0] or self.encoded_height != image_size[1]:
            raise Exception("Bitmap width/height are not equal to previous bitmap")

        # Find differences between frames
        img_data = np.frombuffer(scan0, dtype=np.uint8)
        if bytes_per_pixel == 3:
            img_data = img_data.reshape((image_size[1], image_size[0], 3))
        else:
            img_data = img_data.reshape((image_size[1], image_size[0], 4))

        # Save current position to write payload size later
        payload_position = out_stream.tell()
        out_stream.write(struct.pack('I', 0))  # Placeholder for payload size
        payload_size = 0

        # Find changed blocks
        vertical_diff_blocks = []
        block_height = self.check_block[1]
        
        # Check vertical blocks
        for y in range(0, image_size[1], block_height):
            # Handle remainder at bottom
            current_height = min(block_height, image_size[1] - y)
            
            # Extract current block
            if bytes_per_pixel == 3:
                current_block = img_data[y:y+current_height, 0:image_size[0], :]
                previous_block = self.encode_buffer[y:y+current_height, 0:image_size[0], :]
            else:
                current_block = img_data[y:y+current_height, 0:image_size[0], :]
                previous_block = self.encode_buffer[y:y+current_height, 0:image_size[0], :]
            
            # Compare blocks
            if not np.array_equal(current_block, previous_block):
                # Merge with previous block if adjacent
                if vertical_diff_blocks and vertical_diff_blocks[-1][1] + vertical_diff_blocks[-1][3] == y:
                    # Extend previous block
                    prev_block = vertical_diff_blocks[-1]
                    vertical_diff_blocks[-1] = (prev_block[0], prev_block[1], prev_block[2], prev_block[3] + current_height)
                else:
                    # Add new block
                    vertical_diff_blocks.append((0, y, image_size[0], current_height))

        # Process horizontal blocks within vertical differences
        horizontal_diff_blocks = []
        block_width = self.check_block[0]
        
        for x_start, y_start, width, height in vertical_diff_blocks:
            for x in range(0, width, block_width):
                current_width = min(block_width, width - x)
                
                # Extract block
                if bytes_per_pixel == 3:
                    current_block = img_data[y_start:y_start+height, x:x+current_width, :]
                    previous_block = self.encode_buffer[y_start:y_start+height, x:x+current_width, :]
                else:
                    current_block = img_data[y_start:y_start+height, x:x+current_width, :]
                    previous_block = self.encode_buffer[y_start:y_start+height, x:x+current_width, :]
                
                # Compare blocks
                if not np.array_equal(current_block, previous_block):
                    # Merge with previous block if adjacent
                    if (horizontal_diff_blocks and 
                        horizontal_diff_blocks[-1][1] == y_start and 
                        horizontal_diff_blocks[-1][0] + horizontal_diff_blocks[-1][2] == x):
                        # Extend previous block
                        prev_block = horizontal_diff_blocks[-1]
                        horizontal_diff_blocks[-1] = (prev_block[0], prev_block[1], prev_block[2] + current_width, prev_block[3])
                    else:
                        # Add new block
                        horizontal_diff_blocks.append((x, y_start, current_width, height))

        # Process changed blocks
        for x, y, width, height in horizontal_diff_blocks:
            # Update the encode buffer with new data
            if bytes_per_pixel == 3:
                self.encode_buffer[y:y+height, x:x+width, :] = img_data[y:y+height, x:x+width, :]
            else:
                self.encode_buffer[y:y+height, x:x+width, :] = img_data[y:y+height, x:x+width, :]
            
            # Extract block as new image
            block_img = img_data[y:y+height, x:x+width, :]
            pil_block = Image.fromarray(block_img, mode='RGB' if bytes_per_pixel == 3 else 'RGBA')
            
            # Write block coordinates
            out_stream.write(struct.pack('I', x))  # X
            out_stream.write(struct.pack('I', y))  # Y
            out_stream.write(struct.pack('I', width))  # Width
            out_stream.write(struct.pack('I', height))  # Height
            out_stream.write(struct.pack('I', 0))  # Placeholder for compressed size
            
            # Save current position to write compressed size later
            data_length_position = out_stream.tell()
            before_compression_position = out_stream.tell()
            
            # Compress block
            block_buffer = io.BytesIO()
            if self.use_jpeg:
                pil_block.save(block_buffer, format='JPEG', quality=self.image_quality)
            else:
                pil_block.save(block_buffer, format='PNG')
            
            compressed_block_data = block_buffer.getvalue()
            
            # Write compressed data
            out_stream.write(compressed_block_data)
            
            # Calculate and write compressed size
            compressed_data_length = len(compressed_block_data)
            return_position = out_stream.tell()
            out_stream.seek(data_length_position - 4)
            out_stream.write(struct.pack('I', compressed_data_length))
            out_stream.seek(return_position)
            
            payload_size += compressed_data_length + 20  # 20 bytes for header

        # Write final payload size
        return_position = out_stream.tell()
        out_stream.seek(payload_position)
        out_stream.write(struct.pack('I', payload_size))
        out_stream.seek(return_position)

    def decode_data(self, in_stream):
        """
        Decode image data from stream
        """
        try:
            # Read header
            header_buffer = in_stream.read(4)
            if len(header_buffer) != 4:
                return self.decoded_bitmap
            
            jpeg_size = struct.unpack('I', header_buffer)[0]
            
            # First frame - full image
            if self.decoded_bitmap is None:
                jpeg_data = in_stream.read(jpeg_size)
                if len(jpeg_data) != jpeg_size:
                    return None
                
                self.decoded_bitmap = Image.open(io.BytesIO(jpeg_data))
                return self.decoded_bitmap
            
            # Subsequent frames - differential updates
            remaining_data = jpeg_size
            while remaining_data > 0:
                # Read block header (20 bytes)
                block_header = in_stream.read(20)
                if len(block_header) != 20:
                    return None
                
                x, y, width, height, compressed_size = struct.unpack('IIIII', block_header)
                
                # Read compressed block data
                compressed_data = in_stream.read(compressed_size)
                if len(compressed_data) != compressed_size:
                    return None
                
                # Decompress block
                block_image = Image.open(io.BytesIO(compressed_data))
                
                # Paste block onto decoded image
                self.decoded_bitmap.paste(block_image, (x, y))
                
                remaining_data -= compressed_size + 20
            
            return self.decoded_bitmap
            
        except Exception as e:
            print(f"Error decoding data: {e}")
            return None