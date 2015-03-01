#!/usr/bin/env python3

from setuptools import setup, find_packages

setup(
    name='ppp_twitter_bot',
    version='0.1',
    description='Twitter bot that uses the PPP to answer mentions',
    url='https://github.com/ProgVal/TwitterPlatypus',
    author='Valentin Lorentz',
    author_email='valentin.lorentz+ppp@ens-lyon.org',
    license='MIT',
    classifiers=[
        'Environment :: No Input/Output (Daemon)',
        'Development Status :: 1 - Planning',
        'Intended Audience :: System Administrators',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.2',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
    ],
    install_requires=[
        'ppp_datamodel>=0.6.3,<0.7',
        'tweepy==3.1',
    ],
    packages=[
        'ppp_twitter_bot',
    ],
)


