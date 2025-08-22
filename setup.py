from setuptools import find_packages, setup

setup(
    name="tc_c2pa_py",
    packages=find_packages(exclude=["tests"]),
    version="0.1.0",
    description="Python library which provide C2PA standard functionality.",
    author="StarodubcevDV",
    license="MIT",
    test_suite="tests",
)