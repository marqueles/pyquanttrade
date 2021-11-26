import setuptools
from setuptools import find_packages
setuptools.setup(
    name="trading",  # Replace with your own username
    version="0.0.2",
    author="Miguel Martin, Marcos Jimenez",
    description="Library for backtesting algorithmic trading strategies",
    url="https://github.com/pypa/sampleproject",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
    install_requires=[
        "pandas",
        "numpy==1.19.0",
        "datetime",
        "IPython",
        "altair",
        "sklearn",
        "elasticsearch",
        "scipy",
        "ib_insync",
        "pymongo",
        "ray",
    ],
)
