from setuptools import setup, find_packages

with open('requirements.txt') as f:
    requirements = f.read().splitlines()

setup(
    install_requires=requirements,
    python_requires=">=3.6",

    packages=find_packages(where='src'),
    package_dir={
        '': 'src',
    },
    zip_safe=True
)
