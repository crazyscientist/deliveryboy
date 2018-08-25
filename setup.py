from setuptools import setup, find_packages


setup(
    name="deliveryboy",
    version="0.1.0",
    packages=find_packages(),
    install_requires=["dill"],
    zip_safe=False,
    author="Andreas Hasenkopf",
    author_email="andi@hasenkopf2000.net",
    license="MIT",
    keywords="sudo ssh",
    project_urls={
        "Bug Tracker": "https://github.com/crazyscientist/deliveryboy/issues",
        "Documentation": "https://readthedocs.org/projects/deliveryboy/",
        "Source Code": "https://github.com/crazyscientist/deliveryboy"
    }
)
