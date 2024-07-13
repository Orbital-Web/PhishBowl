import logging
import os
from argparse import ArgumentParser

import uvicorn
from dotenv import load_dotenv
from utils import evaluate_phishnet, populate_phishbowl


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
    parser_dev = subparsers.add_parser(
        "dev",
        help="runs the api in the mode specified in the env file",
    )
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
        "-r",
        "--reset",
        help="flag to reset the phishnet before evaluating",
        action="store_true",
    )
    parser_eval.add_argument(
        "-b",
        "--batchsize",
        type=int,
        default=2048,
        help="number of emails per batch when evaluating the phishnet",
    )
    # populate
    parser_populate = subparsers.add_parser(
        "populate", help="populates the phishbowl with emails"
    )
    parser_populate.add_argument(
        "-r",
        "--reset",
        help="flag to reset the phishbowl before populating",
        action="store_true",
    )
    # test
    parser_test = subparsers.add_parser("test", help="runs all tests")

    return parser


def run():
    """Runs the backend api server. Will either run in development, staging, or
    production mode depending on the `env` environmental variable."""
    env = os.environ.get("env", "prod")
    match env:
        case "prod":
            autoreload = False
            loglevel = "warning"
        case "dev" | "stage":
            autoreload = True
            loglevel = "info"
            logging.basicConfig(level=logging.INFO)
        case _:
            raise ValueError(
                f"Unknown environment {env} provided. env should be one of prod, stage or dev"
            )
    uvicorn.run(
        "routers:app", host="0.0.0.0", port=8000, reload=autoreload, log_level=loglevel
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
            evaluate_phishnet(args.net, args.train, args.reset, args.batchsize)
        case "populate":
            logging.basicConfig(level=logging.INFO)
            populate_phishbowl(args.reset)
        case "test":
            logging.basicConfig(level=logging.INFO)
            run_tests()
        case "dev":
            os.environ["env"] = "dev"
            run()
        case _:
            run()
