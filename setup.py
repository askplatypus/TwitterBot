#!/usr/bin/env python3

from setuptools import setup

setup(
    name='platypus_twitter',
    version='0.1',
    description='Twitter bot that uses Platypus to answer mentions',
    url='https://github.com/askplatypus/TwitterBot',
    license='MIT',
    classifiers=[
        'Environment :: No Input/Output (Daemon)',
        'Development Status :: 1 - Planning',
        'Intended Audience :: System Administrators',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6'
    ],
    install_requires=[
        'requests>=2.0,<3.0',
        'PyLD>=0.8,<0.9',
        'tweepy>=3.5,<4.0',
        'babel>=2.5,<3.0'
    ],
    packages=[
        'platypus_twitter',
    ],
)
