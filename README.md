# JUnit2Checkstyle

Simple python script that converts a JUnit XML to a Checkstyle XML. 

This might be useful because linting with JUnit output is not easily readable via Jenkins, whereas Checkstyle format can be easily readable via the Checkstyle plugin.

## Usage

from the command line:

```shell
python junit2checkstyle.py --input report.xml --output checkstyle.xml
```

Where `report.xml` is the JUnit linter report file to parse and `checkstyle.xml` is the Checkstyle report file to generate.
