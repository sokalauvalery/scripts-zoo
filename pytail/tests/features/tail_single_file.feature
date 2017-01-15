Feature: Tail N lines of single file
  Outputs last N lines from given single file

  Scenario: Tail lines of existing file without N argument
    Given Generate "test.txt" text file of "15" lines
    Then Tail "test.txt" returns "10" lines from given file

  Scenario: Tail 3 lines of existing file
    Given Generate "test.txt" text file of "15" lines
    Then Tail "test.txt" "3" lines returns "3" lines from given file

  Scenario: Tail 0 lines of existing file
    Given Generate "test.txt" text file of "15" lines
    Then Tail "test.txt" "0" lines returns "0" lines from given file

  Scenario: Tail 10 lines of existing file when file contains only 3 lines
    Given Generate "test.txt" text file of "3" lines
    Then Tail "test.txt" "10" lines returns "3" lines from given file

  Scenario Outline:  Tail incorrect N variable
    Given Generate "test.txt" text file of "3" lines
    Then Tail "test.txt" "<n>" lines returns "<message>" exception message

    Examples: Incorrect script usage:
     | n         | message                                       |
     | abc       | Number of lines should be positive integer    |
     | -1        | Number of lines should be positive integer    |
     | $         | Number of lines should be positive integer    |
     | тест         | Number of lines should be positive integer |

  Scenario: Tail nonexistent file
    Then Tail nonexistent file "/fake/path" return exception "No such file /fake/path"

  Scenario: Tail binary file
    Given Generate "test.bin" binary file
    Then Tail "test.bin" "10" lines returns "Unable to  decode file with utf-8 encoding." exception message

  Scenario: Tail 3 lines of empty file
    Given Generate "test.txt" text file of "0" lines
    Then Tail "test.txt" "3" lines returns "0" lines from given file

    #TODO: Scenario for tailing huge file (implementation will work fine)