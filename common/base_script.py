import json
import logging
from datetime import datetime
from functools import reduce

from tabulate import tabulate


class BaseScript(object):
    _logger = logging.getLogger(__name__)
    logging.basicConfig(level=logging.INFO, format='%(asctime)s %(name)-12s %(levelname)-8s %(message)s',
                        datefmt='%m-%d %H:%M:%S', )

    def __init__(self, parameters_dictionary):
        self.datetime_start = datetime.now()
        self.datetime_end = None
        parameters_as_text = json.dumps(parameters_dictionary, sort_keys=True)
        self._logger.info(f'Init script: {parameters_as_text}')
        self.summary_dictionary = {}

    def _add_to_summary(self, key, value):
        self.summary_dictionary[key] = value
        self._info(f'{key}: {value}')

    def _finish_and_summary(self):
        self.datetime_end = datetime.now()

        diff = self.datetime_end - self.datetime_start

        days, seconds, microseconds = diff.days, diff.seconds, diff.microseconds
        milliseconds = int(microseconds/1000)
        hours = days * 24 + seconds // 3600
        minutes = (seconds % 3600) // 60
        seconds = seconds % 60

        self.summary_dictionary['total_execution'] = f'{hours:02d}:{minutes:02d}:{seconds:02d}.{milliseconds:03d}'
        summary_as_text = json.dumps(self.summary_dictionary, sort_keys=True)
        self._logger.info(f'Finish script: {summary_as_text}')

    @staticmethod
    def set_logger_file_id(*args):
        parameters_as_list = "_".join([str(parameter) for parameter in args])
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        file_name = f'./logs/{parameters_as_list}_{timestamp}.log'

        file_logger = logging.FileHandler(file_name)
        formatter = logging.Formatter('%(asctime)s | %(levelname)-8s | %(message)s')
        file_logger.setFormatter(formatter)

        logging.getLogger('').addHandler(file_logger)

    def _track_step(self, message):
        try:
            self.counter += 1
        except AttributeError:
            self.counter = 1

        self._logger.info(u'Step {}.- {}'.format(self.counter, message))

    def _step(self, message):
        self._track_step(message)

    def _track_error(self, message):
        self._logger.error(message)

    def _track_message(self, message):
        self._logger.info(message)

    def _info(self, message):
        self._track_message(message)

    def _show_query(self, title, headers, query, parameters=(), page=0, page_size=100):
        offset = page * page_size
        new_query = query + ' LIMIT ? OFFSET ?'
        values = list(self.connection.execute(new_query, list(parameters) + [page_size, offset]))

        new_values = []
        index = offset
        for row in values:
            new_row = []
            for element in row:
                if isinstance(element, str):
                    element = self.wrap(element, 60)
                new_row.append(element)
            new_values.append([index] + new_row)
            index += 1

        new_headers = ['#'] + list(headers)

        table = tabulate(new_values, headers=new_headers, tablefmt='fancy_grid')
        if title:
            self._track_message('\n{}\n{}\n'.format(title, table))
        else:
            self._track_message('\n{}\n'.format(table))

    def wrap(self, text, width):
        return reduce(lambda line, word, width=width:
                      '%s%s%s' % (line,
                                  ' \n'[(len(line) - line.rfind('\n') - 1
                                         + len(word.split('\n', 1)[0]
                                               ) >= width)],
                                  word),
                      text.split(' ')
                      )
