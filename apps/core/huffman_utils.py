import heapq
from bitarray import bitarray
import os

class HuffmanNode:
    def __init__(self, char, freq):
        self.char = char
        self.freq = freq
        self.left = None
        self.right = None

    def __lt__(self, other):
        return self.freq < other.freq

def calculate_frequency(data):
    frequency = {}
    if data is not None:
        for char in data:
            if char in frequency:
                frequency[char] += 1
            else:
                frequency[char] = 1
    return frequency

def build_huffman_tree(frequency):
    heap = [HuffmanNode(char, freq) for char, freq in frequency.items()]
    
    if not heap:
        return None

    heapq.heapify(heap)

    while len(heap) > 1:
        left = heapq.heappop(heap)
        right = heapq.heappop(heap)

        merged_node = HuffmanNode(None, left.freq + right.freq)
        merged_node.left = left
        merged_node.right = right

        heapq.heappush(heap, merged_node)

    return heap[0] if heap else None

def build_huffman_codes(node, current_code, codes):
    if node is not None:
        if node.char is not None:
            codes[node.char] = current_code
        build_huffman_codes(node.left, current_code + bitarray('0'), codes)
        build_huffman_codes(node.right, current_code + bitarray('1'), codes)

def huffman_encode(data):
    if not data:
        raise ValueError("Input data is empty. Cannot perform Huffman encoding.")

    frequency = calculate_frequency(data)
    
    if not frequency:
        raise ValueError("Cannot perform Huffman encoding on empty frequency data.")

    root = build_huffman_tree(frequency)
    
    if root is None:
        raise ValueError("Failed to build Huffman tree.")

    codes = {}
    build_huffman_codes(root, bitarray(), codes)

    encoded_data = bitarray()
    encoded_data.encode(codes, data)

    return encoded_data, root

def huffman_decode(encoded_data, root):
    if not encoded_data:
        raise ValueError("Input encoded data is empty. Cannot perform Huffman decoding.")

    current = root
    decoded_data = bitarray()

    for bit in encoded_data:
        if bit:
            current = current.right
        else:
            current = current.left

        if current.char is not None:
            decoded_data.append(current.char)
            current = root

    return decoded_data.tobytes()

def calculate_binary_size(file_path):
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"The file {file_path} does not exist.")
    
    return os.path.getsize(file_path) * 8

def write_binary_file(data, file_path):
    directory = os.path.dirname(file_path)
    if not os.path.exists(directory):
        os.makedirs(directory)

    with open(file_path, 'wb') as f:
        f.write(data.tobytes())

import array

def read_binary_file(file_path):
    try:
        with open(file_path, 'rb') as f:
            data = array.array('B', f.read())
            return data
    except Exception as e:
        print(f"Error reading binary file: {e}")
        import traceback
        traceback.print_exc()
        return array.array('B')