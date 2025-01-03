from setuptools import setup, find_packages

setup(
    name="linked-claims-extractor",
    version="0.1",  # match your current PyPI version
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    install_requires=[
        # your existing dependencies
    ],
)
