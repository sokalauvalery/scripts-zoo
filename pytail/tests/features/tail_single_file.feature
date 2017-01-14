Feature: Tail N lines of single file
  Outputs last N lines from given single file

  Scenario: Tail lines of existing file without N argument
    Given Generate text file of "15" lines
    Then Tail returns "10" lines from given file

  Scenario: Tail 3 lines of existing file
    Given Generate text file of "15" lines
    Then Tail "3" lines returns "3" lines from given file

  Scenario: Tail 0 lines of existing file
    Given Generate text file of "15" lines
    Then Tail "0" lines returns "0" lines from given file

  Scenario: Tail 10 lines of existing file when file contains only 3 lines
    Given Generate text file of "3" lines
    Then Tail "10" lines returns "3" lines from given file

  Scenario Outline:  Tail incorrect N variable
    Given Generate text file of "3" lines
    Then Tail "<n>" lines returns "<message>" exception message

    Examples: Incorrect script usage:
     | n         | message                                       |
     | abc       | Number of lines should be positive integer    |
     | -1        | Number of lines should be positive integer    |
     | $         | Number of lines should be positive integer    |

  Scenario: Tail nonexistent file file
    Then Tail nonexistent file "{/fake/path}" return exception "{exception}"