import logging


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