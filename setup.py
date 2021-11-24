from pip.req import parse_requirements
from setuptools import setup

install_reqs = parse_requirements("requirements.txt")

reqs = [str(entry.req) for entry in install_reqs]

setup(
    name="cots-mngt",
    version="0.1",
    description="Management platform for COTS conference",
    classifiers=[
        "Development Status :: 2 - Pre-Alpha",
        "Programming Language :: Python :: 3.9",
        "License :: OSI Approved :: BSD License",
    ],
    url="https://github.com/cots-conf/mngt",
    author="Krerkkiat Chusap",
    author_email="contact@kchusap.com",
    license_files=("LICENSE",),
    packages=["mngt"],
    install_requires=reqs,
    include_package_data=True,
    zip_safe=False,
)
