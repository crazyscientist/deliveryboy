from setuptools import setup, find_packages

long_description = "DeliveryBoy is a lightweight and transparent intermediary" \
                   " for executing a Python callable – a function or method –" \
                   " in a new Python process such that a developer using this" \
                   " intermediary does not have to care about how the object " \
                   "and modules are passed."

with open("README.md", "r") as fh:
    long_description = fh.read()


setup(
    name="deliveryboy",
    short_description="Decorator for running function via sudo, etc.",
    long_description=long_description,
    version="0.1.0",
    packages=find_packages(),
    install_requires=["dill"],
    zip_safe=False,
    author="Andreas Hasenkopf",
    author_email="andi@hasenkopf2000.net",
    maintainer="Andreas Hasenkopf",
    maintainer_email="andi@hasenkopf2000.net",
    license="MIT",
    keywords="sudo ssh",
    platforms=[],
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Intended Audience :: System Administrators",
        "License :: OSI Approved :: MIT License",
        "Operating System :: POSIX :: Linux",
        "Programming Language :: Python :: 3 :: Only",
        "Topic :: System :: Distributed Computing"
    ],
    project_urls={
        "Bug Tracker": "https://github.com/crazyscientist/deliveryboy/issues",
        "Documentation": "https://readthedocs.org/projects/deliveryboy/",
        "Source Code": "https://github.com/crazyscientist/deliveryboy"
    }
)
