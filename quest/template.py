from pkg_resources import resource_string

def template(name, h, fragment=False):
    return h.parse_htmlstring(resource_string("quest", "../templates/%s.xhtml" % name), xhtml=True, fragment=fragment)
