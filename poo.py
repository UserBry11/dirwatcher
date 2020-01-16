import sys
import logging
import signal
import os
import errno
import argparse
import time
from datetime import datetime as dt

author = "__Bryan__" + "__other-people__"

logger = logging.getLogger(__name__)
exit_flag = False


def signal_handler(sig_num, frame):
    global exit_flag
    logger.warn('Received OS process signal ' + str(sig_num))
    exit_flag = True


def search_for_magic(filename, pos, start_line, magic_string):

    with open(filename) as f:
        f.seek(pos)
        line_num = start_line
        for line_num, line in enumerate(f, start_line + 1):

            if not line.endswith('\n'):
                line_num -= 1
            if magic_string in line:
                logger.info('Magic text found: line {} of file {}'
                            .format(line_num - 1, f.name))
        return f.tell(), line_num


def dir_watcher(path, magic_string, ext, interval):

    abs_path = os.path.abspath(path)
    files = {}

    while not exit_flag:
        time.sleep(interval)

        for f in os.listdir(abs_path):
            if f not in files:
                logger.info('File added: ' + f)
                files[f] = (0, 1)

        for f in list(files):
            if f not in os.listdir(abs_path):
                logger.info('File removed: ' + f)
                files.pop(f)

        for f, v in files.items():
            pos, line = v
            if f.endswith(ext):
                fp = os.path.join(abs_path, f)
                files[f] = search_for_magic(fp, pos, line, magic_string)


def create_parser():
    parser = argparse.ArgumentParser(
        description='Watches directory')
    parser.add_argument('-e', '--ext', type=str, default='.txt',
                        help='Tezxdt')
    parser.add_argument('-i', '--interval', type=float,
                        default=1.0, help='asd')
    parser.add_argument('path', help="Tress")
    parser.add_argument('magic', help='asdf')

    return parser


def main():
    parser = create_parser()
    args = parser.parse_args()

    if not args:
        parser.print_usage()
        sys.exit(1)

    app_start_time = dt.now()

    logging.basicConfig(format='%(asctime)s.%(msecs)03d %(name)-12 %(levelname)-8 [%(threadName)-12] %(message)s',
                        datefmt='%Y-%m-%d %H:%M:%S')
    logger.setLevel(logging.DEBUG)
    logger.info('\n'
                '=============================\n'
                '   Has been running {0}\n'
                '   Started on {1}\n'
                '=============================\n'
                .format(__file__, app_start_time.isoformat())
                )

    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    while not exit_flag:

        try:
            dir_watcher(args.path, args.magic, args.ext, args.interval)

        except OSError as e:
            if e.errno == errno.ENOENT:
                logger.error(
                    'Not a Directory or file : {}\nCurrent directory is: {}'
                    .format(os.path.abspath(args.path), os.getcwd()))
            else:
                logger.error(e)
                time.sleep(5.0)
                continue

        except Exception as e:
            error_str = 'Unhandled Exception in MAIN\n{}\nRestarting ...'.format(str(e))
            logger.error(error_str, exc_info=True)
            time.sleep(5.0)
            continue

    uptime = dt.now() - app_start_time
    logger.info('\n'
                '-------------------------------\n'
                '   Stopped {}\n'
                '   Uptime was {}\n'
                '===============================\n'
                .format(__file__, str(uptime)))

    logging.shutdown()
    return 0


if __name__ == '__main__':
    exit(main())
