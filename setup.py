#!/usr/bin/env python3
from setuptools import setup

setup(
    name='pyobs-gui',
    version='0.10.1',
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
        'PyQt5==5.13',
        'astropy',
        'matplotlib',
        'qfitsview'
    ]
)
