# This week
- reverted to multi-page form and reordered form inputs
- removed login/logout functionality (got in the way of testing)
- implemented checks for peaks, pairs, and contrast.tab (singular)
  - more testing is needed
- web app is smarter about users skipping forms (it shouldn't happen now)
- added colors to flashed notifications
- file errors are reported via flash messages
  - but I can't get them to appear in the form field itself
    - which might be ok if the files have lots of errors
- web app reports the number of read-in samples
- disabled submit button when form is submitted (to avoid slowdowns)

# TODO
- mock a submit button?
- clean up code
- write documentation and add doc strings
- match Python naming conventions as time permits (some ides will complain for pep-8 compliance)
