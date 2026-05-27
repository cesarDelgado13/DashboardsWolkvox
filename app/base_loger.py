import os
import logging as lg
from pprint import pformat 
from datetime import datetime


class CustomLoggerName(lg.Filter):
    def filter(self, record):
        name = record.name.split('.')
        if len(name) > 2:
            record.custom_logger_name = f"boot.{'.'.join(name[2:])}"
        else:
            record.custom_logger_name = record.name
        return True


class WriteLogger:
    """
    ---------------------------------------------------------------------------

    Logger object based on Python's logging module

    ---------------------------------------------------------------------------

    Arguments
        
        name : str
            Logger's name

        path : str
            If not None, will save logs to a log file instead of displaying
            the logs in console

        filename_preffix : str
            In case path is not None, will add this preffix in the output
            log file; defualt='my_process'

        format : str
            Log format; 
            default='[%(asctime)s][%(levelname)s][%(name)s] %(message)s'

        datefmt : str
            Date format; default='%Y-%m-%d %H:%M:%S'
 
        level : loggin level or str
            Default=logging.INFO

    ---------------------------------------------------------------------------

    Usage:

    >>> # / ===================================================================

    >>> # vXXX is for the X version you are using
    >>> from bootPKG.vXXX import WriteLogger

    >>> # / ===================================================================

    >>> logger = WriteLogger()
    >>> logger('Holy')
    [2021-10-23 13:31:42][INFO][boot_logger] Holy

    >>> # You cant pass lists, dicts, tuples, etc...
    logger({'Message' : 'Holy'})
    [2021-10-23 13:33:13][INFO][boot_logger]
    {'Message': 'Holy'}

    >>> # / ===================================================================

    >>> # Changing log format
    >>> logger = WriteLogger(format='%(asctime)s -- %(message)s')
    >>> logger('Holy')
    2021-10-23 13:35:57 -- Holy

    >>> # / ===================================================================

    >>> # Working with more than on logger
    >>> debug_logger = WriteLogger(name='debug_logger', level='DEBUG')
    >>> warning_logger = WriteLogger(name='warning_logger', level='WARNING')

    >>> debug_logger('Holy from debug_logger', level='debug')
    [2021-10-23 13:41:13][DEBUG][debug_logger] Holy from debug_logger
    
    # This wont see in console
    warning_logger('Holy from warning_logger', level='debug')
    
    >>> debug_logger('Warning message from debug_logger', level='warning')
    [2021-10-23 13:41:13][WARNING][debug_logger] Warning message from debug_logger

    >>> warning_logger('Warning message from warning_logger', level='warning')
    [2021-10-23 13:41:13][WARNING][warning_logger] Warning message from warning_logger

    >>> # / ===================================================================
    
    >>> # Raising exceptions
    >>> logger = WriteLogger()
    >>> try:
    >>>     10 / 0
    >>> except ZeroDivisionError as exc:
    >>>     logger.exception(exc)
    >>>     raise(exc)
    [2021-10-23 13:47:16][ERROR][boot_logger] division by zero
    Traceback (most recent call last):
    File "main.py", line 5, in <module>
        10 / 0
    ZeroDivisionError: division by zero

    >>> # / ===================================================================

    ---------------------------------------------------------------------------
    """
    def __init__(
        self, name='boot_logger', path=None, 
        filename_preffix='my_process', 
        format='[%(asctime)s][%(levelname)s][%(custom_logger_name)s] %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S', level=lg.INFO,
        propagate=None
        ):

        self.name = name
        self.filename = None
        if path is not None:
            if filename_preffix is None:
                filename_preffix = 'my_process'
            if not os.path.exists(path):
                raise FileNotFoundError(f'Argument `path` doesn´t exists, add a valid path; path={path}')
            execution_timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f'{filename_preffix}_{execution_timestamp}.log'
            self.filename = os.path.join(path, filename)

        self.logger = lg.getLogger(self.name)
        if propagate is not None:
            if not isinstance(propagate, bool):
                raise TypeError(f'Arg `propagation` must be bool; provided={type(propagate)}')
            # self.logger.propagate = False     # Avoids duplicated messages from child/parent loggers
            self.logger.propagate = propagate

        if self.logger.hasHandlers():
            self.logger.handlers.clear() # Avoids duplicated messages from root logger
            
        self.logger.setLevel(level)
        self.formatter = lg.Formatter(format, datefmt)
        if self.filename is not None:
            handler = lg.FileHandler(self.filename)    
        else:
            handler = lg.StreamHandler()
        handler.setFormatter(self.formatter)
        self.logger.addHandler(handler)
        handler.addFilter(CustomLoggerName())

    def set_level(self, level):
        self.logger.setLevel(level)
        return None

    def exception(self, exception):
        self.logger.exception(exception)

    def __call__(self, *messages, level='info', **pformat_kwargs):
        try:
            func = getattr(self.logger, level)
        except Exception as exception:
            self.logger.exception(exception)
            raise ValueError(f'Cannot write log because `level`:{level} doesnt exists') from exception
        for message in messages:
            if not isinstance(message, str):
                message = pformat(message, **pformat_kwargs)
                message = f'\n{message}'
            func(message)
        return None


class BaseLogger:
    """
    ---------------------------------------------------------------------------

    Defined Parent Class to inherit logger attribute as 
    a metaclass attribute

    ---------------------------------------------------------------------------

    Usage:

    >>> # / ===================================================================

    >>> # vXXX is for the X version you are using
    >>> from bootPKG.vXXX import BaseLogger

    >>> # Both classes share the base logger

    >>> class MyCustomClassAAA(BaseLogger):
    >>>     def method(self):
    >>>         self.logger('Holy from MyCustomClassAAA')


    >>> class MyCustomClassBBB(BaseLogger):
    >>>     def method(self):
    >>>         self.logger('Holy from MyCustomClassBBB')


    >>> if __name__ == '__main__':        
    >>>     a = MyCustomClassAAA()
    >>>     b = MyCustomClassBBB()

    >>>     a.method()
    [2021-10-23 13:59:07][INFO][boot_logger] Holy from MyCustomClassAAA
    >>>     b.method()
    [2021-10-23 13:59:07][INFO][boot_logger] Holy from MyCustomClassBBB

    >>> # / ===================================================================

    ---------------------------------------------------------------------------
    """
    logger = WriteLogger()

    @staticmethod
    def set_base_logger(*args, **kwargs):
        """
        ---------------------------------------------------------------------------

        Sets base logger configuration.
        See WriteLogger documentation

        ---------------------------------------------------------------------------

        Usage:

        >>> # / ===================================================================

        >>> # vXXX is for the X version you are using
        >>> from bootPKG.vXXX import BaseLogger

        >>> BaseLogger.set_base_logger(level='WARNING')

        >>> class MyClass(BaseLogger):
        >>>     def info_method(self):
        >>>         self.logger('This message wont see :( ', level='info')

        >>>     def warning_method(self):
        >>>         self.logger('This is a warning message', level='warning')

        >>> if __name__ == '__main__':

        >>>     a = MyClass()
        >>>     a.info_method()
        >>>     a.warning_method()
        [2021-10-23 14:08:38][WARNING][boot_logger] This is a warning message

        >>> # / ===================================================================

        ---------------------------------------------------------------------------
        """
        logger = WriteLogger(*args, **kwargs)
        BaseLogger.logger = logger
        return logger

    @staticmethod
    def add_module_logger(name, level=lg.INFO):
        """
        ---------------------------------------------------------------------------

        Manage loggers from other modules or third-party
        libraries.

        ---------------------------------------------------------------------------

        Arguments
            
            name : str
                Logger's name
    
            level : loggin level or str
                Default=logging.INFO

        ---------------------------------------------------------------------------

        Usage:

        >>> # / ===================================================================

        >>> # vXXX is for the X version you are using
        import kafka
        from bootPKG.v_20230522 import BaseLogger

        BaseLogger.add_module_logger('kafka', level='DEBUG')

        producer = kafka.KafkaProducer(
            bootstrap_servers=['kafka:9092'])
        producer.send(topic='my_topic', value={'Message': 'Holy'})
        [2021-10-23 14:35:12][DEBUG][kafka.producer.kafka] Starting the Kafka producer
        [2021-10-23 14:35:12][DEBUG][kafka.metrics.metrics] Added sensor with name connections-closed
        [2021-10-23 14:35:12][DEBUG][kafka.metrics.metrics] Added sensor with name connections-created
        [2021-10-23 14:35:12][DEBUG][kafka.metrics.metrics] Added sensor with name select-time
        [2021-10-23 14:35:12][DEBUG][kafka.metrics.metrics] Added sensor with name io-time
        ...
        ...
        ...

        >>> # / ===================================================================

        ---------------------------------------------------------------------------
        """
        logger = lg.getLogger(name)
        logger.setLevel(level)
        if BaseLogger.logger.filename is not None:
            handler = lg.FileHandler(BaseLogger.logger.filename)
        else:
            handler = lg.StreamHandler()
        handler.setFormatter(BaseLogger.logger.formatter)
        logger.addHandler(handler)
        return logger

    @staticmethod
    def set_logger_level(logger_name, level):
        logger = lg.getLogger(logger_name)
        logger.setLevel(level)
        return None

    def __call__(self, *args, **kwargs):
        return BaseLogger.logger(*args, **kwargs)
