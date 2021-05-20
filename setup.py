import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="pymysqlpool",
    version="0.0.1",
    author="gengleiming",
    author_email="244277947@qq.com",
    description="db pool for pymysql",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/kormay/pymysqlpool",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)