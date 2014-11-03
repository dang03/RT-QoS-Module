from setuptools import setup

setup(
    name='PathfinderProject',
    version='0.1.1',
    packages=['pathfinder'],
    package_data={'data': ['pathfinder/*.json']},
    url='None',
    license='None',
    author='Daniel',
    author_email='dani.guija@i2cat.net',
    description='Algorithm to find a suitable path for a QoS request',
    install_requires=[
        'networkX',
        'collections',
        'flask',
        'BeautifulSoup',
        'flask_RESTful',
        'simplejson',
        'matplotlib',
        'networkX',
        'numpy'
    ]
)
