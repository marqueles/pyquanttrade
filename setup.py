import setuptools
from setuptools import find_packages
setuptools.setup(
    name="pyquanttrade",  # Replace with your own username
    version="0.0.1",
    author="Miguel Martin, Marcos Jimenez",
    description="Library for backtesting algorithmic trading strategies using Quandl data",
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
        "scipy",
        "quandl"
    ],
)
