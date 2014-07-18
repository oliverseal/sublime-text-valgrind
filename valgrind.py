import sublime, sublime_plugin
import re
import os


class ValgrindOpenCallstackFileCommand(sublime_plugin.TextCommand):
    def run(self, edit, *args, **kwargs):
        # if in valgrind context
        # if the line regexes to be a file
        # find the file
        # jump to the line
        scope_name = self.view.scope_name(self.view.sel()[0].b)
        if scope_name.find("string.other.link.valgrind.filename") > -1:
            line = self.view.line(self.view.sel()[0])
            self.lookupfile(line)
        else:
            system_command = args["command"] if "command" in args else None
            if system_command:
                system_args = dict({"event": args["event"]}.items() + args["args"].items())
                self.view.run_command(system_command, system_args)
        # return True

    def lookupfile(self, region):
        # find the filename in the line
        line = self.view.substr(region)
        regex = r'\(([0-9a-zA-Z\._\\\/\-]+):(\d+)\)'
        matches = re.search(regex, line)
        filename = matches.group(1)
        line_number = matches.group(2)

        results = []
        directories = self.view.window().folders()
        for directory in directories:
            for dirname, _, files in self.walk(directory):
                for file in files:
                    fileName = dirname + os.sep + file
                    if re.search(filename, fileName):
                        results += [fileName]
        
        if len(results) == 1:
            path = results[0]
            opened_view = self.view.window().open_file(path)
            # jump to the number
            opened_view.run_command('goto_line', {'line': int(line_number)})
        else:
            print('TODO: command window listing options.')
        return

    def walk(self, directory):
        for dir, dirnames, files in os.walk(directory):
            dirnames[:] = [dirname for dirname in dirnames]
            yield dir, dirnames, files
