#!/usr/bin/env python
# -*- coding: utf-8 -*-

import fileinput
import csv
import sys
import re
import StringIO

# This prevents prematurely closed pipes from raising
# an exception in Python
from signal import signal, SIGPIPE, SIG_DFL
signal(SIGPIPE, SIG_DFL)


def is_insert(line):
    """
    Returns true if the line begins a SQL insert statement.
    """
    return line.startswith('INSERT INTO') or False


def get_insert_prefix(line):
    """
    Return the string from the beginning of the insert statement to the "VALUES".
    """
    return re.search("INSERT INTO `.*` VALUES", line).group(0) 


def get_values(line):
    """
    Returns the portion of an INSERT statement containing values
    """
    values = line.partition('` VALUES ')[2]
    if values[-1] == ';':
        values = values[0:-1]

    return values


def values_sanity_check(values):
    """
    Ensures that values from the INSERT statement meet basic checks.
    """
    assert values
    assert values[0] == '('
    # Assertions have not been raised
    return True


def get_raw_row(values, sidx):
    """
    Find a row (one row of a DB table).
    """

    # Get to the start point
    eidx = -1
    
    # Return an empty string if there is no more data
    if sidx == -1:
        return ''

    # Find the end of a raw row
    b_inside_str= False
    for idx in xrange(sidx+1, len(values)):
        ###
        # Are we in the middle of a string value?
        ###
        # Is this part of a string value? then the right round 
        #   bracket does not maean the end of row.
        if values[idx] == '\'':
            b_inside_str = not b_inside_str
            # If this single quote is escaped by a preceding backslash, 
            #   it is still inside the string value.
            if idx > 0 and values[idx-1] == '\\':
                b_inside_str = not b_inside_str
                # But, this backslash is escaped by a another preceding 
                #   backslash, this is the end of the string value.
                if idx > 1 and values[idx-2] == '\\':
                    b_inside_str = not b_inside_str

        ###
        # Check the end of a row
        ###
        if b_inside_str == False and values[idx] == ')':
            # eidx points to the comma or the EOS
            eidx = idx+1
            break

    assert eidx != -1, 'Can not find the end of a row'
    return values[sidx:eidx]


def parse_values(values, outfile):
    """
    Given a file handle and the raw values from a MySQL INSERT
    statement, write the equivalent CSV to the file
    """

    # Read a table of rows for a given INSERT statement as an array
    tbl  = []
    sidx = 0
    while True:
        row = get_raw_row(values, sidx)
        # Stop if there is no more rows remain
        if row == '':
            break
        # Strip away a pair of parentheses and store it
        tbl.append(row[1:-1])
        # Find the left parenthesis of the next row from the end of current row
        sidx = values.find('(', sidx+len(row)) 

    # Parse the table
    reader = csv.reader(tbl, 
                        delimiter=',',
                        doublequote=False,
                        escapechar='\\',
                        quotechar='\'',
                        strict=True
    )

    # Print the output
    writer = csv.writer(outfile, delimiter='\t', quoting=csv.QUOTE_MINIMAL)
    for csv_row in reader:
        writer.writerow(csv_row)


def main():
    """
    Parse arguments and start the program
    """
    # Iterate over all lines in all files
    # listed in sys.argv[1:]
    # or stdin if no args given.
    try:
        for line in fileinput.input():
            # Look for an INSERT statement and parse it.
            if is_insert(line):
            # Print the prefix of the insert statement to show its table name.
                tbl_title = get_insert_prefix(line)
                print >> sys.stdout, tbl_title

                values = get_values(line)
                if values_sanity_check(values):
                    parse_values(values, sys.stdout)
    except KeyboardInterrupt:
        sys.exit(0)

if __name__ == "__main__":
    main()
