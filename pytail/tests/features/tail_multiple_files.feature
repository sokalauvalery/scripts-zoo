Feature: Tail N lines of multiple files
  Outputs last N lines for every given file

  Scenario: Tail lines of 3 existing files with default parameters
    Given Generate "test1.txt" text file of "15" lines
    Given Generate "test2.txt" text file of "15" lines
    Given Generate "test3.txt" text file of "15" lines
    When Run tail command for files "test1.txt, test2.txt, test3.txt" with default parameters
    Then Output contains filename and last "10" lines from "test1.txt" file
    And Output contains filename and last "10" lines from "test2.txt" file
    And Output contains filename and last "10" lines from "test3.txt" file

  Scenario: Tail 3 lines of 2 existing files with quiet mode
    Given Generate "test1.txt" text file of "15" lines
    Given Generate "test2.txt" text file of "15" lines
    When Tail "3" lines for files "test1.txt, test2.txt" with quiet mode
    Then Output contains last "3" lines from "test1.txt" file and no file names
    And Output contains last "3" lines from "test2.txt" file and no file names
