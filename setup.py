import os
from setuptools import setup


def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(
    name = "appointment_reminder",
    version = "0.0.1",
    author = "Flowroute Developers",
    description = ("A time-zone aware SMS based reminder service."),
    packages=['appointment_reminder'],
    url='git@gitlab.internal:l-pod/appointment-reminder.git',
    classifiers=[
        "Development Status :: 1",
        "Topic :: Utilities",
    ],
)
