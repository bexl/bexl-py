from setuptools import setup, find_packages


setup(
    name='bexl',
    version='0.1.0',
    description='A parser and interpreter for the Basic EXpression Language'
    ' (BEXL)',
    long_description=open('README.rst', 'r').read(),
    keywords='bexl basic expression language',
    author='Jason Simeone',
    author_email='jay@classless.net',
    license='MIT',
    classifiers=[
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
    ],
    url='https://github.com/bexl/bexl-py',
    package_dir={'': 'src'},
    packages=find_packages('src'),
    zip_safe=True,
    include_package_data=True,
    install_requires=[
        'six',
    ],
    entry_points={
        'console_scripts': [
            'bexl = bexl.cli:main',
        ]
    },
)

