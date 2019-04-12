def humanize_list(list_of_elements: list):
    list_of_texts = [str(element) for element in list_of_elements]
    length = len(list_of_texts)
    if length == 0:
        return ''
    if length == 1:
        return list_of_texts[0]

    first_part = ', '.join(list_of_texts[:-1])
    second_part = list_of_texts[-1]
    return f'{first_part} and {second_part}'
