# -*- coding: utf-8 -*-
"""Interfaz de línea de comandos: html2pptx archivo1 [archivo2 ...] [-o salida.pptx]"""
import argparse
import sys

from . import __version__
from .browser import BrowserNotFound
from .convert import UnsupportedFile, convert
from .extract import DumpError


def build_parser():
    ap = argparse.ArgumentParser(
        prog='html2pptx',
        description='Convierte wireframes HTML (o imágenes PNG/JPG) en un PPTX editable.')
    ap.add_argument('inputs', nargs='+', metavar='ARCHIVO',
                    help='archivos .html, .png o .jpg (el orden define las diapositivas)')
    ap.add_argument('-o', '--output', metavar='SALIDA.pptx',
                    help='archivo de salida (por defecto, junto al primer archivo)')
    ap.add_argument('--width', type=int, default=1440, metavar='PX',
                    help='ancho del lienzo en px (por defecto 1440)')
    ap.add_argument('--height', type=int, default=1024, metavar='PX',
                    help='alto del lienzo en px (por defecto 1024)')
    ap.add_argument('--version', action='version', version='html2pptx ' + __version__)
    return ap


def main(argv=None):
    args = build_parser().parse_args(argv)
    try:
        convert(args.inputs, output=args.output, width=args.width, height=args.height,
                on_progress=print)
    except (BrowserNotFound, DumpError, UnsupportedFile, FileNotFoundError, ValueError) as e:
        sys.stderr.write('Error: %s\n' % e)
        return 2
    except KeyboardInterrupt:
        sys.stderr.write('\nInterrumpido.\n')
        return 130
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
