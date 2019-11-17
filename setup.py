#!/usr/bin/env python3
from distutils.core import setup

setup(
    name='pyobs-gui',
    version='0.8',
    description='GUI for pyobs',
    author='Tim-Oliver Husser',
    author_email='thusser@uni-goettingen.de',
    packages=[
        'pyobs_gui',
        'pyobs_gui.qt'
    ],
    install_requires=[
        'astroquery',
        'astroplan',
        'colour',
        'PyQt5',
        'astropy',
        'aplpy',
        'matplotlib'
    ]
)
