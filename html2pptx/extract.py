# -*- coding: utf-8 -*-
"""Renderiza un HTML en el navegador y extrae la geometría real (mediciones)."""
import base64
import json
import os
import re
import subprocess
import tempfile
from importlib import resources

from .browser import find_browser


class DumpError(RuntimeError):
    """El navegador no devolvió mediciones del documento."""


def _dump_js():
    return resources.files('html2pptx').joinpath('dump.js').read_text(encoding='utf-8')


def _io_read(path, errors='strict'):
    with open(path, encoding='utf-8', errors=errors) as fh:
        return fh.read()


def measure_html(html_path, width=1440, height=1024, timeout=60, browser=None):
    """Abre html_path en modo headless y devuelve un dict con la geometría medida."""
    browser = browser or find_browser()
    src = _io_read(html_path)
    with tempfile.TemporaryDirectory(prefix='html2pptx-') as tmp:
        work = os.path.join(tmp, os.path.basename(html_path) + '.dump.html')
        with open(work, 'w', encoding='utf-8', newline='') as fh:
            fh.write(src + '\n<script>' + _dump_js() + '</script>')
        profile = os.path.join(tmp, 'profile')
        os.makedirs(profile, exist_ok=True)
        out = os.path.join(tmp, 'dom.html')
        url = 'file:///' + work.replace('\\', '/')
        cmd = [browser, '--headless=new', '--disable-gpu', '--no-first-run', '--dump-dom',
               '--window-size=%d,%d' % (width, height), '--virtual-time-budget=3000',
               '--user-data-dir=' + profile, url]
        with open(out, 'wb') as fh:
            try:
                subprocess.run(cmd, stdout=fh, stderr=subprocess.DEVNULL, timeout=timeout, check=True)
            except subprocess.TimeoutExpired:
                raise DumpError('El navegador tardó demasiado en medir %s' % html_path)
            except FileNotFoundError:
                raise DumpError('No se pudo ejecutar el navegador: %s' % browser)
        dom = _io_read(out, errors='replace')
    m = re.search(r'<pre id="d">([A-Za-z0-9+/=]+)</pre>', dom)
    if not m:
        raise DumpError('El navegador no devolvió mediciones para %s' % html_path)
    try:
        return json.loads(base64.b64decode(m.group(1)).decode('utf-8'))
    except Exception as e:
        raise DumpError('Datos corruptos para %s: %s' % (html_path, e))
