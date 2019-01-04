from setuptools import setup


setup(
    name='gmd',
    version='0.1',
    packages=['gmd'],
    entry_points='''
        [console_scripts]
        gmd=gmd.cli:main
    ''',
)
