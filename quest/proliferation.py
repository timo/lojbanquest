from __future__ import absolute_import

from pkg_resources import resource_string, resource_filename

__vowel_cycle = list("aeioua")
__conso_cycle = list("bcdfgjklmnprstvxzb")

def cycle(char, dir):
    cycle = __vowel_cycle if char in __vowel_cycle else __conso_cycle
    char = cycle[cycle.index(char) + dir]
    return char

class Charts(object):
    charts = list("aabb")

    def __init__(self):
        try:
            self.charts = resource_string("quest", "../data/charts.txt")
            self.charts = list(self.charts)
        except:
            self.charts = list("aabb")
            self.write_charts()

    def write_charts(self):
        chartfile = open(resource_filename("quest", "../data/charts.txt"), "w")
        chartfile.write("".join(self.charts))
        chartfile.close()

    def player_entry(self):
        self.charts = cycle(self.charts[0], 1), self.charts[1], cycle(self.charts[2], 1), self.charts[3]
        self.write_charts()

    def player_leave(self):
        self.charts = self.charts[0], cycle(self.charts[1], -1), self.charts[2], self.cycle(charts[3], -1)
        self.write_charts()

    def __str__(self):
        return "".join(self.charts)
    
    def __repr__(self):
        return "<charts: %s>" % self

charts = Charts()
