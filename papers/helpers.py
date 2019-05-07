import bz2
import json


def read_compressed_json(file_path):
    with open(file_path, 'rb') as file:
        compressed_content = file.read()
    content = bz2.decompress(compressed_content)
    return json.loads(content)


def reverse_dictionary(original_dictionary):
    reversed_dictionary = {}
    for key, value in original_dictionary.items():
        for element in value:
            if element not in reversed_dictionary:
                reversed_dictionary[element] = []
            reversed_dictionary[element].append(key)
    return reversed_dictionary


if __name__ == '__main__':
    content = read_compressed_json('../datasets/scrapper/cache/20190501/films_tropes_20190501.json.bz2')
    reversed_content = reverse_dictionary(content)
