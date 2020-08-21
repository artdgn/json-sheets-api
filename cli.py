import argparse
import sys

from proxy import coingecko


def parser() -> argparse.ArgumentParser:
    if len(sys.argv) == 1:
        sys.argv.append("-h")  # print help if no args
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "symbols", type=str,
        help="List of sumbols separated by white space. "
             "To paste with newlines open quotes, paste, than close quotes.")
    parser.add_argument(
        "-c", "--currency", default='usd', type=str, required=False,
        help="Currency for rates")
    return parser


if __name__ == '__main__':
    args = parser().parse_args()
    symbols = args.symbols.split()
    prices = coingecko.Client().prices_for_symbols(
        symbols=symbols, currency=args.currency)
    print('  prices:')
    print('\n'.join([str(p) for p in prices]))
