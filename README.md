# MySQL dump to CSV

## Change log
* 2014/10/27 - Master branch ignores empty columns. So it is difficult to track the column index of a value in a given CSV output. This branch will output empty string as it is and the number of columns of all rows will remain unchanged.
* 2014/10/27 - Fix for the previous bug that happens where one column is a string ending in `)` and the next column is a string starting in `(`. The previous logic suggested that the parentheses would be stripped. This bugfix ignores parentheses appearing inside string values.

## Background
A quickly-hacked-together Python script to turn mysqldump files to CSV files. Optimized for Wikipedia database dumps.

Extraordinarily large MySQL dumps can be difficult or impossible to import on fairly limited hardware. The annoying thing about a MySQL dump is that the only practical way to manipulate it is through MySQL, which essentially requires a hardware upgrade should one want to work with large dumps like the Wikipedia MySQL dumps.

Wouldn't it be great if there were some way to convert the MySQL dump format (which is a series of INSERT statements) into a *universal* format... like... CSV?

Well, now there is.

This short Python script takes advantage of the fact that the structure of a MySQL INSERT statement is not too different from CSV, and uses the Python CSV parser (before and after some text wrangling) to turn the MySQL dump file into a CSV file.

## Usage
Just run `python mysqldump_to_csv.py` followed by the filename of an SQL file. You can specify multiple SQL files, and they will all be concatenated into one CSV file. This script can also take in SQL files from standard input, which can be useful for turning a gzipped MySQL dump into a CSV file without uncompressing the MySQL dump.

`zcat dumpfile.sql.gz | python mysqldump_to_csv.py`

## How It Works
The following SQL:

    INSERT INTO `page` VALUES (1,0,'April','',1,0,0,0.778582929065,'20140312223924','20140312223929',4657771,20236,0),
    (2,0,'August','',0,0,0,0.123830928525,'20140312221818','20140312221822',4360163,11466,0);

is turned into the following CSV:

    1<tab/>0<tab/>April<tab/><tab/>1<tab/>0<tab/>0<tab/>0.778582929065<tab/>20140312223924<tab/>20140312223929<tab/>4657771<tab/>20236<tab/>0
    2<tab/>0<tab/>August<tab/><tab/>0<tab/>0<tab/>0<tab/>0.123830928525<tab/>20140312221818<tab/>20140312221822<tab/>4360163<tab/>11466<tab/>0

It's not too difficult to see what is going on, but you can certainly look at the source code to see exactly how the transformation is made.

## Todo
 * A rigorous series of unit tests, proving that this works on a diverse set of MySQL dump files without any side effects
 * Some more documentation
