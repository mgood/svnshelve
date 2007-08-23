#!/usr/bin/python

import sys

try:
    import pygments
except ImportError:
    def print_patch(*parts):
        print patch
else:
    from pygments.formatters import TerminalFormatter
    from pygments import highlight
    from pygments.lexers import get_lexer_by_name
    diff_lexer = get_lexer_by_name('diff')
    term_fmter = TerminalFormatter()
    def print_patch(*parts):
        for p in parts:
            highlight(p, diff_lexer, term_fmter, sys.stdout)

class HunkSelector:
    class Option:
        def __init__(self, char, action, help, default=False):
            self.char = char
            self.action = action
            self.default = default
            self.help = help

    standard_options = [
        Option('n', 'shelve', 'shelve this change for the moment.',
            default=True),
        Option('y', 'keep', 'keep this change in your tree.'),
        Option('d', 'done', 'done, skip to the end.'),
        Option('i', 'invert', 'invert the current selection of all hunks.'),
        Option('s', 'status', 'show status of hunks.'),
        Option('q', 'quit', 'quit')
    ]

    end_options = [
        Option('y', 'continue', 'proceed to shelve selected changes.',
            default=True),
        Option('r', 'restart', 'restart the hunk selection loop.'),
        Option('s', 'status', 'show status of hunks.'),
        Option('i', 'invert', 'invert the current selection of all hunks.'),
        Option('q', 'quit', 'quit')
    ]

    def __init__(self, patches):
        self.patches = patches
        self.total_hunks = 0
        for patch in patches:
            for hunk in patch.hunks:
                # everything's shelved by default
                hunk.selected = True
                self.total_hunks += 1

    def __get_option(self, char):
        for opt in self.standard_options:
            if opt.char == char:
                return opt
        raise Exception('Option "%s" not found!' % char)

    def __select_loop(self):
        j = 0
        for patch in self.patches:
            i = 0
            lasti = -1
            while i < len(patch.hunks):
                hunk = patch.hunks[i]
                if lasti != i:
                    print_patch(patch.get_header(), hunk)
                    j += 1
                lasti = i

                prompt = 'Keep this change? (%d of %d)' \
                            % (j, self.total_hunks)

                if hunk.selected:
                    self.__get_option('n').default = True
                    self.__get_option('y').default = False
                else:
                    self.__get_option('n').default = False
                    self.__get_option('y').default = True

                action = self.__ask_user(prompt, self.standard_options)

                if action == 'keep':
                    hunk.selected = False
                elif action == 'shelve':
                    hunk.selected = True
                elif action == 'done':
                    return True
                elif action == 'invert':
                    self.__invert_selection()
                    self.__show_status()
                    continue
                elif action == 'status':
                    self.__show_status()
                    continue
                elif action == 'quit':
                    return False

                i += 1
        return True

    def select(self):
        if self.total_hunks == 0:
            return []

        done = False
        while not done:
            if not self.__select_loop():
                return []

            while True:
                self.__show_status()
                prompt = "Shelve these changes, or restart?"
                action = self.__ask_user(prompt, self.end_options)

                if action == 'continue':
                    done = True
                    break
                elif action == 'quit':
                    return []
                elif action == 'status':
                    self.__show_status()
                elif action == 'invert':
                    self.__invert_selection()
                elif action == 'restart':
                    break


        for patch in self.patches:
            tmp = []
            for hunk in patch.hunks:
                if hunk.selected:
                    tmp.append(hunk)
            patch.hunks = tmp

        tmp = []
        for patch in self.patches:
            if len(patch.hunks):
                tmp.append(patch)
        self.patches = tmp

        return self.patches

    def __invert_selection(self):
        for patch in self.patches:
            for hunk in patch.hunks:
                if hunk.__dict__.has_key('selected'):
                    hunk.selected = not hunk.selected
                else:
                    hunk.selected = True

    def __show_status(self):
        print '\nStatus:'
        for patch in self.patches:
            print '  %s' % patch.oldname
            shelve = 0
            keep = 0
            for hunk in patch.hunks:
                if hunk.selected:
                    shelve += 1
                else:
                    keep += 1

            print '    %d hunks to be shelved' % shelve
            print '    %d hunks to be kept' % keep
            print

    if sys.platform == "win32":
        import msvcrt
        def __getchar(self):
            return msvcrt.getche()
    else:
        def __getchar(self):
            import tty
            import termios
            fd = sys.stdin.fileno()
            settings = termios.tcgetattr(fd)
            try:
                tty.setraw(fd)
                ch = sys.stdin.read(1)
            finally:
                termios.tcsetattr(fd, termios.TCSADRAIN, settings)
            return ch

    def __ask_user(self, prompt, options):
        while True:
            sys.stdout.write(prompt)
            sys.stdout.write(' [')
            for opt in options:
                if opt.default:
                    default = opt
                sys.stdout.write(opt.char)
            sys.stdout.write('?] (%s): ' % default.char)

            response = self.__getchar()

            # default, which we see as newline, is 'n'
            if response in ['\n', '\r', '\r\n']:
                response = default.char

            print response # because echo is off

            for opt in options:
                if opt.char == response:
                    return opt.action

            for opt in options:
                print '  %s - %s' % (opt.char, opt.help)
