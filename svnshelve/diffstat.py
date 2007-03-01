#!/usr/bin/python

class DiffStat(object):
    def __init__(self, lines):
        self.maxname = 0
        self.maxtotal = 0
        self.total_adds = 0
        self.total_removes = 0
        self.stats = {}
        self.__parse(lines)

    def __parse(self, lines):
        import string
        adds = 0
        removes = 0
        current = None

        for line in lines:
            if line.startswith('+') and not line.startswith('+++'):
                adds += 1
            elif line.startswith('-') and not line.startswith('---'):
                removes += 1
            elif line.startswith('--- '):
                next = line[4:].strip()
                if next == current:
                    continue
                self.__add_stats(current, adds, removes)

                adds = 0
                removes = 0
                context = 0
                current = next

        self.__add_stats(current, adds, removes)

    class Filestat:
        def __init__(self):
            self.adds = 0
            self.removes = 0
            self.total = 0

    def __add_stats(self, file, adds, removes):
        if file is None:
            return
        elif file in self.stats:
            fstat = self.stats[file]
        else:
            fstat = self.Filestat()

        fstat.adds += adds
        fstat.removes += removes
        fstat.total = adds + removes
        self.stats[file] = fstat

        self.maxname = max(self.maxname, len(file))
        self.maxtotal = max(self.maxtotal, fstat.total)
        self.total_adds += adds
        self.total_removes += removes

    def __str__(self):
        # Work out widths
        width = 78 - 5
        countwidth = len(str(self.maxtotal))
        graphwidth = width - countwidth - self.maxname
        factor = 1

        # The graph width can be <= 0 if there is a modified file with a
        # filename longer than 'width'. Use a minimum of 10.
        if graphwidth < 10:
            graphwidth = 10

        while (self.maxtotal / factor) > graphwidth:
            factor += 1

        s = ""

        for file, fstat in self.stats.iteritems():
            s += ' %-*s | %*.d ' % (self.maxname, file, countwidth, fstat.total)

            # If diffstat runs out of room it doesn't print anything, which
            # isn't very useful, so always print at least one + or 1
            s += '+' * max(fstat.adds / factor, 1)
            s += '-' * max(fstat.removes / factor, 1)
            s += '\n'

        s += ' %d files changed, %d insertions(+), %d deletions(-)' % \
                (len(self.stats), self.total_adds, self.total_removes)
        return s

if __name__ == '__main__':
    import sys
    ds = DiffStat(sys.stdin.readlines())
    print ds
