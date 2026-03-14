#!/usr/bin/env python3
import argparse
import sys
from core import setup_theme, generate_theme, update_theme

def main():
    parser = argparse.ArgumentParser(description="Fortnite GRUB Theme Manager")
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    parser_update = subparsers.add_parser("setup-theme", help="Setup theme files")
    parser_update.add_argument("--verbose", "-v", action="store_true", help="Show detailed logs")
    parser_generate = subparsers.add_parser("generate-theme", help="Generate theme files")
    subparsers.add_parser("update-theme", help="Update theme files with new cached images")
    args = parser.parse_args()

    if args.command == "setup-theme":
        setup_theme.run()

    if args.command == "generate-theme":
        generate_theme.run()

    if args.command == "update-theme":
        update_theme.update_theme()
        

if __name__ == "__main__":
    main()