from setuptools import setup

setup(
    name='mctl',
    version='0.1.0',
    py_modules=['mctl'],
    install_requires=[
        'click==8.0.3',
        'mailchimp-marketing==3.0.72',
        'pylint'
    ],
    entry_points={
        'console_scripts': [
            'mctl = mctl:cli',
        ],
    },
)
