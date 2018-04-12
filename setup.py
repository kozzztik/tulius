from setuptools import setup, find_packages

__version__ = '0.1'

setup(
    name='tulius',
    version=__version__,
    description='Tulius game forum',
    long_description="""This is http://tulius.com project""",
    author='https://github.com/kozzztik',
    url='https://github.com/kozzztik/tulius',
    packages=find_packages(),
    include_package_data=True,
    license='https://github.com/kozzztik/tulius/blob/master/LICENSE',
    classifiers=[
        'License :: OSI Approved',
        'Programming Language :: Python :: 2.7',
        ],
)

