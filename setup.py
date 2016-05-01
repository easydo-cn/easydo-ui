################################
import os
import xml.sax.saxutils
from setuptools import setup, find_packages

def read(*rnames):
    text = open(os.path.join(os.path.dirname(__file__), *rnames)).read()
    return xml.sax.saxutils.escape(text)

setup (
    name='zopen.kssaddons',
    version='0.1.1dev',
    author = "Chen Qiong",
    author_email = "zope-dev@zope.org",
    description = "operation center core for everydo over HTTP",
    long_description=(
        read('readme.txt')
        + '\n\n' +
        read ('changes.txt')
        ),
    license = "Private",
    keywords = "zope3 z3c rpc  server client",
    classifiers = [
        'Development Status :: 4 - Alpha',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'Programming Language :: Python',
        'Natural Language :: Chinese',
        'Operating System :: OS Independent',
        'Topic :: Internet :: WWW/HTTP',
        'Framework :: Zope3'],
    url = 'http://epk.zopen.cn/pypi/zopen.zopenaddons',
    packages = find_packages('src'),
    include_package_data = True,
    package_dir = {'':'src'},
    namespace_packages= ['zopen',],
    install_requires = [
        'setuptools',
        ],
    zip_safe = False,
)
