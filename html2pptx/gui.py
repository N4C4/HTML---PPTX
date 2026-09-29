# -*- coding: utf-8 -*-
"""Interfaz gráfica (tkinter) para convertir HTML/imágenes a PPTX editable."""
import os
import queue
import subprocess
import sys
import threading

try:
    import tkinter as tk
    from tkinter import filedialog, messagebox, ttk
except ImportError:  # Python sin Tk
    tk = None

from . import __version__
from .browser import BrowserNotFound
from .convert import UnsupportedFile, convert
from .extract import DumpError

FILETYPES = [
    ('Archivos convertibles', '*.html *.htm *.png *.jpg *.jpeg'),
    ('Página web (HTML)', '*.html *.htm'),
    ('Imágenes', '*.png *.jpg *.jpeg'),
    ('Todos los archivos', '*.*'),
]


def _open_folder(path):
    folder = os.path.dirname(os.path.abspath(path))
    try:
        if sys.platform.startswith('win'):
            os.startfile(folder)  # noqa: S606
        elif sys.platform == 'darwin':
            subprocess.Popen(['open', folder])
        else:
            subprocess.Popen(['xdg-open', folder])
    except Exception:
        pass


class App(object):
    def __init__(self, root):
        self.root = root
        self.files = []
        self.queue = queue.Queue()
        self.running = False
        self.last_output = None
        root.title('html2pptx %s — HTML/imagen a PowerPoint editable' % __version__)
        root.geometry('720x560')
        root.minsize(600, 460)
        self._build()

    def _build(self):
        pad = {'padx': 8, 'pady': 4}
        frm_top = ttk.Frame(self.root)
        frm_top.pack(fill='x', **pad)
        ttk.Label(frm_top, text='Archivos (el orden define las diapositivas):',
                  font=('Segoe UI', 9, 'bold')).pack(anchor='w')

        mid = ttk.Frame(frm_top)
        mid.pack(fill='both', expand=True, pady=2)
        scroll = ttk.Scrollbar(mid)
        scroll.pack(side='right', fill='y')
        self.lst = tk.Listbox(mid, height=7, selectmode='extended',
                              yscrollcommand=scroll.set, font=('Consolas', 9))
        self.lst.pack(side='left', fill='both', expand=True)
        scroll.config(command=self.lst.yview)

        btns = ttk.Frame(frm_top)
        btns.pack(fill='x')
        for text, cmd in (('+ HTML…', lambda: self.add_files('html')),
                          ('+ Imágenes…', lambda: self.add_files('img')),
                          ('Quitar', self.remove_selected),
                          ('Limpiar', self.clear_all),
                          ('Subir', lambda: self.move(-1)),
                          ('Bajar', lambda: self.move(1))):
            ttk.Button(btns, text=text, command=cmd).pack(side='left', padx=3, pady=3)

        opts = ttk.Frame(self.root)
        opts.pack(fill='x', **pad)
        ttk.Label(opts, text='Lienzo:').grid(row=0, column=0, sticky='w')
        ttk.Label(opts, text='ancho').grid(row=0, column=1, sticky='e')
        self.var_w = tk.StringVar(value='1440')
        self.var_h = tk.StringVar(value='1024')
        ttk.Entry(opts, textvariable=self.var_w, width=6).grid(row=0, column=2, padx=(3, 8))
        ttk.Label(opts, text='alto').grid(row=0, column=3, sticky='e')
        ttk.Entry(opts, textvariable=self.var_h, width=6).grid(row=0, column=4, padx=3)
        ttk.Label(opts, text='px').grid(row=0, column=5, sticky='w', padx=(2, 16))

        ttk.Label(opts, text='Salida:').grid(row=1, column=0, sticky='w', pady=(6, 0))
        self.var_out = tk.StringVar()
        ttk.Entry(opts, textvariable=self.var_out).grid(row=1, column=1, columnspan=4,
                                                        sticky='ew', pady=(6, 0), padx=3)
        opts.columnconfigure(4, weight=1)
        ttk.Button(opts, text='Examinar…', command=self.browse_out).grid(row=1, column=5,
                                                                         pady=(6, 0), padx=(8, 0))

        act = ttk.Frame(self.root)
        act.pack(fill='x', **pad)
        self.btn_go = ttk.Button(act, text='Convertir', command=self.start)
        self.btn_go.pack(side='left')
        self.btn_open = ttk.Button(act, text='Abrir carpeta', command=lambda: self.last_output
                                   and _open_folder(self.last_output), state='disabled')
        self.btn_open.pack(side='left', padx=8)
        self.var_status = tk.StringVar(value='Listo.')
        ttk.Label(act, textvariable=self.var_status, foreground='#555').pack(side='right')

        logf = ttk.Frame(self.root)
        logf.pack(fill='both', expand=True, **pad)
        ttk.Label(logf, text='Registro:').pack(anchor='w')
        self.txt = tk.Text(logf, height=10, state='disabled', font=('Consolas', 9),
                           background='#1e1e1e', foreground='#d4d4d4', wrap='word')
        self.txt.pack(fill='both', expand=True)
        self._log('html2pptx %s — seleccione archivos y pulse Convertir.' % __version__)
        self._log('HTML: formas y texto editables (medidos en Chrome/Edge).')
        self._log('PNG/JPG: cada imagen entra como fondo de una diapositiva.')

    # ---------- archivos ----------
    def add_files(self, kind):
        exts = ('*.html', '*.htm') if kind == 'html' else ('*.png', '*.jpg', '*.jpeg')
        if kind == 'html':
            types = [FILETYPES[1], FILETYPES[3]]
        else:
            types = [FILETYPES[2], FILETYPES[3]]
        picks = filedialog.askopenfilenames(title='Agregar archivos', filetypes=types)
        added = 0
        for p in picks:
            if p.lower().endswith(tuple(exts)) and p not in self.files:
                self.files.append(p)
                self.lst.insert('end', p)
                added += 1
        if added:
            self.var_status.set('%d archivo(s) agregado(s).' % added)

    def remove_selected(self):
        for idx in reversed(self.lst.curselection()):
            self.lst.delete(idx)
            del self.files[idx]

    def clear_all(self):
        self.lst.delete(0, 'end')
        self.files = []

    def move(self, delta):
        sel = list(self.lst.curselection())
        if not sel:
            return
        if delta < 0 and sel[0] == 0:
            return
        if delta > 0 and sel[-1] == len(self.files) - 1:
            return
        items = [self.files[i] for i in sel]
        for i in reversed(sel):
            del self.files[i]
            self.lst.delete(i)
        pos = sel[0] + delta
        for k, item in enumerate(items):
            self.files.insert(pos + k, item)
            self.lst.insert(pos + k, item)
            self.lst.selection_set(pos + k)

    def browse_out(self):
        p = filedialog.asksaveasfilename(title='Guardar como', defaultextension='.pptx',
                                         filetypes=[('PowerPoint', '*.pptx')])
        if p:
            self.var_out.set(p)

    # ---------- conversión ----------
    def start(self):
        if self.running:
            return
        if not self.files:
            messagebox.showinfo('html2pptx', 'Agregue al menos un archivo HTML, PNG o JPG.')
            return
        try:
            width = int(self.var_w.get())
            height = int(self.var_h.get())
            if width < 200 or height < 200:
                raise ValueError
        except ValueError:
            messagebox.showerror('html2pptx', 'El lienzo debe ser un número de al menos 200 x 200 px.')
            return
        inputs = list(self.files)
        output = self.var_out.get().strip() or None
        self.running = True
        self.btn_go.config(state='disabled')
        self.btn_open.config(state='disabled')
        self.var_status.set('Convirtiendo…')
        threading.Thread(target=self._worker, args=(inputs, output, width, height),
                         daemon=True).start()
        self.root.after(80, self._poll)

    def _worker(self, inputs, output, width, height):
        try:
            out = convert(inputs, output=output, width=width, height=height,
                          on_progress=lambda m: self.queue.put(('msg', m)))
            self.queue.put(('ok', out))
        except (BrowserNotFound, DumpError, UnsupportedFile, FileNotFoundError, ValueError) as e:
            self.queue.put(('err', str(e)))
        except Exception as e:  # pragma: no cover - fallo inesperado
            self.queue.put(('err', '%s: %s' % (type(e).__name__, e)))

    def _poll(self):
        try:
            while True:
                kind, payload = self.queue.get_nowait()
                if kind == 'msg':
                    self._log(payload)
                elif kind == 'ok':
                    self._log('Listo: %s' % payload)
                    self.last_output = payload
                    self.var_status.set('Conversión finalizada.')
                    self.btn_open.config(state='normal')
                    self.running = False
                    self.btn_go.config(state='normal')
                elif kind == 'err':
                    self._log('ERROR: ' + payload)
                    self.var_status.set('Error.')
                    self.running = False
                    self.btn_go.config(state='normal')
                    messagebox.showerror('html2pptx', payload)
        except queue.Empty:
            pass
        if self.running:
            self.root.after(80, self._poll)

    def _log(self, msg):
        self.txt.config(state='normal')
        self.txt.insert('end', msg + '\n')
        self.txt.see('end')
        self.txt.config(state='disabled')


def main(argv=None):
    if tk is None:
        sys.stderr.write('Este Python no incluye tkinter. Instale el paquete tcl/tk de Python.\n')
        return 2
    root = tk.Tk()
    App(root)
    root.mainloop()
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
