import argparse


def build_parser() -> argparse.ArgumentParser:
    return argparse.ArgumentParser(prog="agent-browser")


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    parser.parse_args(argv)
    return 0
