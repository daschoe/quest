"""QUEST - QUestionnaire Editor SysTem"""

from setuptools import setup

with open("README.md", 'r') as f:
    long_description = f.read()

setup(
    name='QUEST',
    version='1.0.0',
    description='An easy solution to create graphical user interfaces for offline questionnaires without programming knowledge.',
    license="GNU GPLv3",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author='Daphne Schössow',
    author_email='daphne.schoessow@ikt.uni-hannover.de',
    url="https://gitlab.uni-hannover.de/da.schoessow/quest",
    download_url='https://gitlab.uni-hannover.de/da.schoessow/quest/-/archive/v1.0/quest-v1.0.zip',
    packages=['QUEST'],
    keywords=['laboratory study', 'questionnaire', 'audio study', 'OSC', 'PyQt'],
    classifiers=[
       "Intended Audience :: Developers",
       "Intended Audience :: Education",
       "Intended Audience :: End Users/Desktop",
       "Programming Language :: Python :: 3", ],

    extras_require={
       'dev': ['pytest', 'pytest-cov', 'pytest-qt', 'keyboard', 'psutil'],
       'build': ['numpy', 'SoundFile']
    },

    # install_requires=[
    #   'ping3',
    #   'python_osc',
    #   'configobj',
    #   'fpdf',
    #   'msgpack_python',
    #   'PyQt5',
    #   'pyzmq',
    #   'timeloop',
    # ],

    python_requires='>=3.8'
)

