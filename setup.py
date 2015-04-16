#!/usr/bin/env python
from setuptools import setup


def readme():
    with open('README.md') as f:
        return f.read()

def requirements():
    with open('requirements.txt') as f:
        return f.readlines()


setup(name='mutt_ics',
      version='0.4',
      description='A tool to show calendar event details in Mutt.',
      long_description=readme(),
      classifiers=[
          'Development Status :: 3 - Alpha',
          'License :: OSI Approved :: MIT License',
      ],
      keywords='ics calendar mutt',
      url='https://github.com/dmedvinsky/mutt-ics',
      author='Dmitry Medvinsky',
      author_email='me@dmedvinsky.name',
      license='MIT',
      packages=[],
      scripts=['bin/mutt-ics'],
      install_requires=requirements(),
      include_package_data=True,
      zip_safe=False)
