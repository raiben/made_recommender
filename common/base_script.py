import logging
from functools import reduce

from tabulate import tabulate


class BaseScript(object):
    _logger = logging.getLogger(__name__)
    logging.basicConfig(level=logging.DEBUG, format='%(asctime)s %(name)-12s %(levelname)-8s %(message)s',
                        datefmt='%m-%d %H:%M:%m', )

    def _track_step(self, message):
        try:
            self.counter += 1
        except AttributeError:
            self.counter = 1

        self._logger.info(u'Step {}.- {}'.format(self.counter, message))

    def _track_error(self, message):
        self._logger.error(message)

    def _track_message(self, message):
        self._logger.debug(message)

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
        """
        A word-wrap function that preserves existing line breaks
        and most spaces in the text. Expects that existing line
        breaks are posix newlines (\n).
        """
        return reduce(lambda line, word, width=width: '%s%s%s' %
                                                      (line,
                                                       ' \n'[(len(line) - line.rfind('\n') - 1
                                                              + len(word.split('\n', 1)[0]
                                                                    ) >= width)],
                                                       word),
                      text.split(' ')
                      )
