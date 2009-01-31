from __future__ import with_statement

import os
from nagare import presentation

class Quest(object):
    pass

@presentation.render_for(Quest)
def render(self, h, *args):
    this_file = __file__
    if this_file.endswith('.pyc'):
        this_file = __file__[:-1]

    models_file = os.path.join(os.path.dirname(__file__), 'models.py')

    h.head.css_url('/static/nagare/application.css')
    h.head << h.head.title('Up and Running !')

    with h.div(class_='mybody'):
        with h.div(id='myheader'):
            h << h.a(h.img(src='/static/nagare/img/logo.gif'), id='logo', href='http://www.nagare.org/', title='Nagare home')
            h << h.span('Congratulations !', id='title')

        with h.div(id='main'):
            h << h.h1('Your application is running')

            with h.p:
                h << 'You can now:'
                with h.ul:
                    h << h.li('If your application uses a database, add your database entities into ', h.i(models_file))
                    h << h.li('Add your application components into ', h.i(this_file), ' or create new files')

            h << h.p('To lean more, go to the ', h.a('official website', href='http://www.nagare.org/'))

            h << "Have fun !"

    h << h.div(class_='footer')

    return h.root

# ---------------------------------------------------------------

app = Quest
