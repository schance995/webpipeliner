# Finished!
- Added documentation for all files
- Streamlined the process for adding new fields dynamically based on pipeline and genome
- Changed redirect of pipeline request, it sends back to the about page now
- Added screenshots in readme
- Might host online with Python Anywhere, will keep you updated...
- Can now complete the form from start to finish (but submitting doesn't do anything)
  - No access to Biowulf this summer :(

# Basic app functionality should work now, but...
- Did not add a JS alert after form submission
  - I think it requires transmitting the form data through Ajax, validating in Flask, then returning status back through Ajax
- If the user is on the details form and hits the back button, they have to refresh the page in order to resubmit
  - Does this have to do with page caching? I'm not sure.
- And of course there could always be bugs (hopefully not!)

# Thanks again!