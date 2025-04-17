from setuptools import setup, find_packages

setup(
    name="register-api",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "sqlalchemy_utils",
        "fastapi",
        "sqlalchemy",
        "cwl-utils",
        "ogc-ap-validator",
        "schema-salad",
    ],
) 
