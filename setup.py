import os
from setuptools import setup, find_packages

import mongo_coupons


def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(
    name='django-mongo-coupons',
    version=mongo_coupons.__version__,
    description='Django-coupons with mongoengine',
    long_description=read('README.md'),
    # license=read('LICENSE'),
    author='shiprashalini',
    author_email='code.shipra@gmail.com',
    url='https://github.com/ShipraShalini/django-mongo-coupons.git',
    include_package_data=True,
    packages=find_packages(),
    classifiers=[
        'Framework :: Django',
        'Intended Audience :: Developers',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
    ],
    keywords='django mongo coupons',
)
