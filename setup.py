#!/usr/bin/env python3
from setuptools import setup

setup(
    name='pyobs-gui',
    version='0.14',
    description='GUI for pyobs',
    author='Tim-Oliver Husser',
    author_email='thusser@uni-goettingen.de',
    packages=['pyobs_gui', 'pyobs_gui.qt'],
    install_requires=[line.strip() for line in open("requirements.txt").readlines()]
)
