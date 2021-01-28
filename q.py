from typing import List

import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, GLib

import itertools, time, os

from functools import partial
    

os.environ['NO_COLOR'] = '1'
class Handler:
    def onDestroy(self, *args):
        Gtk.main_quit()

    def search_changed(self, entry: Gtk.Entry):
        val = entry.get_text()
        if len(val) < 4:
            return
        GLib.idle_add(Helper.search, val)
        
builder = Gtk.Builder()
builder.add_from_file("z.glade")
resultslist = builder.get_object('resultslist')
results = Gtk.ListStore(str, str, str)
resultslist.set_model(results)

for i, title in enumerate(['name', 'version', 'source']):
    
    resultslist.append_column(column = Gtk.TreeViewColumn(title, Gtk.CellRendererText(), text=i))
builder.connect_signals(Handler())

window = builder.get_object("window1")
window.show_all()


class Helper(object):
    def __init__(self):
        pass
    
    def on_res(self, frm, query, res, *args):
        res = res.read()
        res = res.splitlines()
        
        results.clear()
        
        if query !=  builder.get_object('query').get_text():
            return
            

        for p in res:
            results.append([p, p, frm])
        window.show_all()
    
    def on_aur(self, res, a):
        res = res.read()
        print(res.splitlines())
        
    def search(self, query):
        dummy=lambda *args: 1
        
        self.execute(['pacman', '-Ssq', query], dummy, partial(self.on_res, 'pacman', query), dummy)
        self.execute(['aur', 'search', query], dummy, partial(self.on_res, 'aur', query), dummy)

    def execute(self, cmd, on_done, on_stdout, on_stderr):
        # fuck threads
        self.pid, self.idin, self.idout, self.iderr = \
            GLib.spawn_async(cmd,
                             flags=0,
                             standard_output=True,
                             standard_error=True)
        fout = os.fdopen(self.idout, "r")
        ferr = os.fdopen(self.iderr, "r")
        GLib.child_watch_add(self.pid, on_done)
        GLib.io_add_watch(fout, GLib.IO_IN, on_stdout)
        GLib.io_add_watch(ferr, GLib.IO_IN, on_stderr)
        return self.pid
    
Helper = Helper()


            

Gtk.main()
