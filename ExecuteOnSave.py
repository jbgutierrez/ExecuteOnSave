import sublime
import sublime_plugin
import re
import os
from string import Template


class ExecuteOnSave(sublime_plugin.EventListener):
    def on_post_save(self, view):
        view.window().run_command("execute_on_save", {"saving": True})


class ExecuteOnSaveCommand(sublime_plugin.TextCommand):
    def expand_variables(self):
        res = {
            "packages": sublime.packages_path(),
            "installed_packages": sublime.installed_packages_path()
        }
        window = self.view.window()
        if window.folders():
            res["folder"] = window.folders()[0]
        av = window.active_view()
        if av is None:
            return res
        filename = av.file_name()
        if not filename:
            return res
        filename = os.path.abspath(filename)
        res["file"] = filename
        res["file_path"] = os.path.dirname(filename)
        res["file_basename"] = os.path.basename(filename)
        if 'folder' not in res:
            res["folder"] = res["file_path"]
        return res

    def run(self, edit, saving=False):

        view = self.view
        global_settings = sublime.load_settings(__name__ + '.sublime-settings')
        build_on_save = view.settings().get('build_on_save', global_settings.get('build_on_save', False))
        filter_execute = view.settings().get('filter_execute', global_settings.get('filter_execute', []))
        variables = self.expand_variables()

        if saving and not build_on_save:
            return

        for filter, execute in filter_execute:
            if re.search(filter, view.file_name()):
                cmd = Template(execute).substitute(variables)
                view.window().run_command("exec", {"cmd": cmd})
