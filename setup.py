VERSION = '0.0.1b'

from setuptools import setup, find_packages

setup(
      name = 'quest',
      version = VERSION,
      author = 'Timo Paulssen',
      author_email = 'timonator@perpetuum-immobile.de',
      description = 'An implementation of the "LojbanQuest" concept by Matt Arnold.',
      license = 'GPL3',
      keywords = '',
      url = '',
      packages = find_packages(),
      include_package_data = True,
      package_data = {'' : ['*.cfg']},
      zip_safe = False,
      install_requires = ('nagare',"lojbansuggest"),
      entry_points = """
      [nagare.applications]
      quest = quest.quest:app
      """,
      dependency_links = [
          "http://wakelift.de/lojban/software/",
      ]
    )
