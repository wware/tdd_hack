import argparse
import logging
import logging.handlers

from log_aggregator import getLogger

logger = logging.getLogger()   # default to root logger


class MockFoo(object):
    def doSomething(self, msg="doing something"):
        logger.info(msg)


class RealFoo(MockFoo):
    def doSomething(self, msg="REALLY doing something"):
        MockFoo.doSomething(self, msg)


def main(args=None):
    global logger
    parser = argparse.ArgumentParser()
    parser.add_argument("-v", "--verbose", action="store_true")
    args = parser.parse_args(args)

    logger = getLogger(
        'hack',
        level=(logging.DEBUG if args.verbose else logging.INFO)
    )
    logger.info("Hello")
    MockFoo().doSomething()
    RealFoo().doSomething()


if __name__ == "__main__":
    main()
