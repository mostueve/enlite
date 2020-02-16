from setuptools import setup

setup(name='enlite',
      version='1.0',
      description='Python package for looking up compound and reaction id aliases and information based on ModelSEED data',
      author='Moritz Stüve',
      author_email='mostueve@gmail.com',
      url='https://gitlab.com/mostueve/enlite',
      packages=['enlite', 'enlite.classes'],
      install_requires=['PyYAML']
      )
