function no_resubmit() {
  if ( window.history.replaceState ) {
    window.history.replaceState( null, null, window.location.href );
  }
}