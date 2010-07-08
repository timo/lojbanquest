===========
Lojbanquest
===========
---------------------------------------------
An implementation of Matt Arnolds Game Design
---------------------------------------------

Lojbanquest
===========

Overview
--------

In the game Lojbanquest, the player roams the world of tersistu'as, a magical land where instead of north, east, south, west, up and down direction and position are based on words.

There is a big overworld and an underground dungeon, ready to be explored by the inclined Lojbanist. But beware! In this world, monsters abound! Grab a friend and hunt monsters, combatting them by casting spells in Lojban. Loot treasure chests to gain Word Cards for use in combat.

This Implementation
===================

Overview
--------

This implementation of Lojbanquest is based on the nagare web framework. It is thus played in a browser. Basic comet-like techniques enable the game to become an interactive multiplayer experience.

Installation
------------

Since at the moment there is no official lojbanquest installation that's persistent and constantly running, you have to either ask the author to set an instance up for testing or install your own local copy.

To do this, you first need to install nagare, as per the installation instructions on the website. Basically that's just 1. get stackless python, 2. create a virtualenv with it, 3. pip install "nagare[full]".

You also need to make sure, that you have graphviz installed. It will be used to create maps in the cache subdirectory.

The next step is to install lojbanquest in it. Running setup.py develop will do that for you. You then need the files gismu.txt and cmavo.txt from the debian package lojban-common, big_list from http://www.digitalkingdom.org/~rlpowell/hobbies/lojban/ and put them in the data directory.

Running nagare-admin create-db will create a database and fill it with a world. nagare-admin serve quest --host=0.0.0.0 -p 5000 will run a local server that others can connect to on http://yourmachine:5000/quest/. Register a user and have fun!
