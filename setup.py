#!/usr/bin/env python3

from setuptools import setup


def readme():
    with open('README.md', 'r', encoding="utf-8") as f:
        return f.read()


setup(name='upydevice',
      version='0.3.2',
      description='Python library to interface with wireless/serial MicroPython devices',
      long_description=readme(),
      long_description_content_type='text/markdown',
      url='http://github.com/Carglglz/upydevice',
      author='Carlos Gil Gonzalez',
      author_email='carlosgilglez@gmail.com',
      classifiers=[
        'Development Status :: 3 - Alpha',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'Intended Audience :: Science/Research',
        'Intended Audience :: Education',
        'Operating System :: MacOS :: MacOS X',
        'Operating System :: POSIX :: Linux',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Topic :: System :: Monitoring',
        'Topic :: Scientific/Engineering',
        'Topic :: Software Development :: Embedded Systems',
        'Topic :: Terminals'
      ],
      license='MIT',
      packages=['upydevice'],
      zip_safe=False,
      scripts=[],
      include_package_data=True,
      install_requires=['pyserial', 'dill', 'unsync',
                        'bleak>=0.12.1', 'bleak_sigspec>=0.0.4'])
