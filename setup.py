from distutils.core import setup

setup(
    name='steward',
    version='0.0.3',
    author='Andrew Svetlov',
    author_email='andrew.svetlov@gmail.com',
    url='https://github.com/asvetlov/steward',
    packages=['steward'],
    license='MIT License',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.2',
        'Programming Language :: Python :: 3.3',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
    description='Library for easy converting between plain JSON-like data '\
        'and compound structure of user defined class instances.',
    long_description="""
    """,
    platforms=['any'],
)
