import bz2
import json
import os
import textwrap
from io import StringIO
from pandas import DataFrame
import os
import matplotlib.pyplot as plt
import pandas as pd
import pygraphviz as pgv
from tabulate import tabulate

data = {}

def read_compressed_json(file_path):
    if file_path in data:
        return data[file_path]

    with open(file_path, 'rb') as file:
        compressed_content = file.read()
    content_bytes = bz2.decompress(compressed_content)
    content = json.loads(content_bytes.decode('utf-8'))

    data[file_path] = content
    return content


def reverse_dictionary(original_dictionary):
    reversed_dictionary = {}
    for key, value in original_dictionary.items():
        for element in value:
            if element not in reversed_dictionary:
                reversed_dictionary[element] = []
            reversed_dictionary[element].append(key)
    return reversed_dictionary


def draw_graphviz(dot, filename):
    new_dot = dot.replace('type="start"', 'shape="ellipse" margin=0.2')
    new_dot = new_dot.replace('type="database"', 'shape="cylinder" margin=0.2')
    new_dot = new_dot.replace('type="tool"', 'shape="box" margin=0.2')
    new_dot = new_dot.replace('type="process"', 'shape="box3d" margin=0.2 style="filled" fillcolor="gray91"')
    new_dot = new_dot.replace('type="data"', 'shape="polygon" skew=0.5 margin=0')

    G = pgv.AGraph(string=new_dot)
    G.layout(prog='dot')
    if not os.path.isdir('figures'):
        os.makedirs('figures')
    G.draw(os.path.join('figures', filename))


def get_table_for_dataframe(df, fixed_width=None, **kwargs):
    latex_code = tabulate(df, headers=df, tablefmt='latex_raw', **kwargs)
    latex_code = latex_code.replace('%', '\\%')
    if fixed_width is not None:
        latex_code = latex_code.replace('\\begin{tabular}','\\begin{tabularx}{\\textwidth}')
        latex_code = latex_code.replace('\\end{tabular}', '\\end{tabularx}')
        latex_code = latex_code.replace('{lr}','{Xr}')
    return latex_code


def tex_wrap_and_escape(text, length=40):
    if isinstance(text, str):
        wrapped_text = textwrap.fill(text, length)
        if '\n' in wrapped_text:
            wrapped_text = '\makecell[tl]{' + wrapped_text.replace('\n', ' \\\\ ') + '}'
        return tex_escape(wrapped_text)
    if isinstance(text, list):
        text = ', '.join([str(element) for element in text])
        return tex_wrap_and_escape(text)
    return text


def tex_escape(text):
    CHARS = {
        '&': '\&',
        '%': '\%',
        '$': '\$',
        '#': '\#',
        '_': '\_',
        '^': '\^',
    }

    if isinstance(text, str):
        return ("".join([CHARS.get(char, char) for char in text]))

    return text


def get_experiment_execution_information(log_file_path):
    with open(log_file_path, 'r') as scraper_log:
        lines = scraper_log.readlines()
        first_line = lines[0]
        last_line = lines[-1]

    parameters_as_text = first_line.split('Init script: ')[1]
    input_log = json.loads(parameters_as_text)
    keys = [tex_wrap_and_escape(key) for key in input_log.keys()]
    values = [tex_wrap_and_escape(key) for key in input_log.values()]
    processed_dictionary = dict(parameter=keys, value=values)
    input_dataframe = pd.DataFrame.from_dict(processed_dictionary)

    summary_as_text = last_line.split('Finish script: ')[1]
    output_log = json.loads(summary_as_text)
    keys = [tex_wrap_and_escape(key) for key in output_log.keys()]
    values = [tex_wrap_and_escape(key) for key in output_log.values()]
    processed_dictionary = dict(parameter=keys, value=values)
    output_dataframe = pd.DataFrame(processed_dictionary)
    return input_dataframe, output_dataframe


def read_dataframe(file_path, use_hdf=True):
    if file_path in data:
        return data[file_path]

    if file_path.endswith('csv.bz2'):
        content = None

        file_hdf = file_path.replace('csv.bz2', 'h5')
        if os.path.isfile(file_hdf):
            content = pd.read_hdf(file_hdf)
        else:
            with open(file_path, 'rb') as file:
                compressed_content = file.read()
            csv_content = bz2.decompress(compressed_content)
            content = pd.read_csv(StringIO(csv_content.decode('utf-8')))
            if use_hdf:
                content.to_hdf(file_hdf, 'tripdata')

    data[file_path] = content
    return content


def plot_regression(dataframe, x_column, y_column, color='red'):
    Y = dataframe[y_column]
    X = dataframe[x_column]

    X = X.values.reshape(len(X), 1)
    Y = Y.values.reshape(len(Y), 1)

    X_train = X[:-250]
    X_test = X[-250:]
    Y_train = Y[:-250]
    Y_test = Y[-250:]

    from sklearn import linear_model
    regr = linear_model.LinearRegression()

    regr.fit(X_train, Y_train)
    plt.plot(X_test, regr.predict(X_test), color=color, linewidth=3, )
