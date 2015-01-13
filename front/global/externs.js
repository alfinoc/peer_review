// Gather GET parameters from the URL.
window.URL_PARAMS = {};
window.location.search.substring(1).split('&').forEach(function(pair) {
   pair = pair.split('=');
   if (pair[0])
      URL_PARAMS[pair[0]] = pair[1];
});
