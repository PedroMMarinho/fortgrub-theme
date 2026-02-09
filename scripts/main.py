#!/usr/bin/env python3
import argparse
import sys

from core import update_theme

def main():
    parser = argparse.ArgumentParser(description="Fortnite GRUB Theme Manager")
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    parser_update = subparsers.add_parser("update-theme", help="Regenerate theme files")
    parser_update.add_argument("--verbose", "-v", action="store_true", help="Show detailed logs")

    args = parser.parse_args()

    if args.command == "update-theme":
        update_theme.run()

if __name__ == "__main__":
    main()