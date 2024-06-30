from phishnet.utils import evaluate_phishnet
from dotenv import load_dotenv
from argparse import ArgumentParser
import uvicorn
import logging
from typing import Literal


def cli_parser() -> ArgumentParser:
    """Builds an ArgumentParser to handle different commands.

    Returns:
        argparse.ArgumentParser: The parser.
    """
    parser = ArgumentParser()
    subparsers = parser.add_subparsers(dest="command")
    # run
    parser_run = subparsers.add_parser("run", help="runs the api in production mode")
    # dev
    parser_dev = subparsers.add_parser("dev", help="runs the api in development mode")
    # evaluate
    parser_eval = subparsers.add_parser("eval", help="evaluates a phishnet")
    parser_eval.add_argument("net", help="name of phishnet to evaluate")
    parser_eval.add_argument(
        "-t",
        "--train",
        help="flag to train the phishnet before evaluating",
        action="store_true",
    )
    parser_eval.add_argument(
        "-b",
        "--batchsize",
        type=int,
        default=128,
        help="number of emails per batch when evaluating the phishnet",
    )
    # test
    parser_test = subparsers.add_parser("test", help="runs all tests")

    return parser


def run(mode: Literal["prod", "dev"] = "prod"):
    """Runs the backend api server.

    Args:
        mode (str, optional): Whether to run in production or development mode. Defaults
            to "prod".
    """
    if mode == "dev":
        appip = "127.0.0.1"
        autoreload = True
        loglevel = "info"
    else:
        appip = "0.0.0.0"
        autoreload = False
        loglevel = "warning"
    uvicorn.run(
        "router:app", host=appip, port=8000, reload=autoreload, log_level=loglevel
    )


def run_tests():
    pass


if __name__ == "__main__":
    load_dotenv()
    parser = cli_parser()

    # run appropriate command
    args = parser.parse_args()
    match args.command:
        case "eval":
            logging.basicConfig(level=logging.INFO)
            evaluate_phishnet(args.net, args.train, args.batchsize)
        case "test":
            logging.basicConfig(level=logging.INFO)
            run_tests()
        case "dev":
            run("dev")
        case _:
            run()
