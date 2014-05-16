Scikit docset
=============

[Scikit-learn](http://scikit-learn.org/stable/) is an awesome Machine Learning library in Python.

__How to generate the docset:__

- It is as easy as:
`
	python scikit-to-dash.py
`

- Requirements:
	- [httrack](http://www.httrack.com/) must be installed.
	- Python package, [Beautiful Soup](https://pypi.python.org/pypi/beautifulsoup4/4.3.2).


Because doc2dash doesn't support scikit documentation format, I had to create this script to generate the docset.
> Documentation size is 55,42MiB so it may take a while to download after you run the script (if you don't want to download html files, comment line 11 in scikit-to-dash.py).