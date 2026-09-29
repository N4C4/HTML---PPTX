# -*- coding: utf-8 -*-
"""Localiza un navegador Chromium (Edge/Chrome) para renderizar el HTML."""
import os
import shutil
import sys


class BrowserNotFound(RuntimeError):
    """No se encontró ningún navegador compatible."""


def _candidates():
    if sys.platform.startswith('win'):
        pf86 = os.environ.get('ProgramFiles(x86)', r'C:\Program Files (x86)')
        pf = os.environ.get('ProgramFiles', r'C:\Program Files')
        local = os.environ.get('LOCALAPPDATA', '')
        for base in (pf86, pf, os.path.join(local, 'Programs') if local else ''):
            if not base:
                continue
            for app in ('Microsoft\\Edge', 'Google\\Chrome', 'Chromium', 'Microsoft\\Edge Beta', 'Google\\Chrome Beta'):
                yield os.path.join(base, app + '\\Application', 'msedge.exe' if 'Edge' in app else 'chrome.exe')
    elif sys.platform == 'darwin':
        yield '/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge'
        yield '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome'
        yield '/Applications/Chromium.app/Contents/MacOS/Chromium'
        yield os.path.expanduser('~/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge')
        yield os.path.expanduser('~/Applications/Google Chrome.app/Contents/MacOS/Google Chrome')
    else:
        for name in ('google-chrome-stable', 'google-chrome', 'chromium', 'chromium-browser',
                     'microsoft-edge-stable', 'microsoft-edge', 'brave-browser-stable', 'brave-browser'):
            found = shutil.which(name)
            if found:
                yield found


def find_browser():
    """Devuelve la ruta del navegador o lanza BrowserNotFound."""
    env = os.environ.get('HTML2PPTX_BROWSER')
    if env:
        if os.path.exists(env):
            return env
        raise BrowserNotFound('HTML2PPTX_BROWSER apunta a un archivo inexistente: %s' % env)
    for p in _candidates():
        if p and os.path.exists(p):
            return p
    for name in ('msedge', 'chrome', 'chromium', 'google-chrome'):
        found = shutil.which(name)
        if found:
            return found
    raise BrowserNotFound(
        'No se encontró Chrome ni Edge. Instale uno, o defina la variable de entorno '
        'HTML2PPTX_BROWSER con la ruta completa del navegador.')
