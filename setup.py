#!/usr/bin/env python3

"""
Mail sender with automatic failover
See:
    https://github.com/Anthony25/mail-sender-daemon
"""

from setuptools import setup, find_packages

setup(
    name="mail-sender-daemon",
    version="0.0.1",

    description="Mail sender with automatic failover",

    url="https://github.com/Anthony25/mail-sender-daemon",
    author="Anthony25 <Anthony Ruhier>",
    author_email="anthony.ruhier@gmail.com",

    license="Simplified BSD",

    classifiers=[
        "Operating System :: POSIX :: Linux",
        "Programming Language :: Python :: 3 :: Only",
        "License :: OSI Approved :: BSD License",
    ],

    keywords="mail",
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        "appdirs", "Flask", "Flask-Script", "flask-restplus",
    ],

    setup_requires=["pytest-runner", ],
    tests_require=[
        "pytest", "pytest-cov", "pytest-mock", "pytest-flask", "requests-mock"
    ],
)
