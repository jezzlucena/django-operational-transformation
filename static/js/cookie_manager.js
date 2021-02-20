// CookieManager is a singleton javascript object
// that handles all the cookie frontend logic
var CookieManager = CookieManager || new function() {
  const self = this;

  // Cookie logic taken from https://stackoverflow.com/questions/1599287/create-read-and-erase-cookies-with-jquery
  this.setCookie = (name, value) => {
    var date = new Date();
    date.setTime(date.getTime() + (30 * 24 * 60 * 60 * 1000));
    // Set cookie valid for 30 days
    var expires = "; expires=" + date.toGMTString();
    document.cookie = name + "=" + value + expires + "; path=/";
  };

  // Read a given key from the local cookie
  this.readCookie = (name) => {
    var nameEQ = name + "=";
    var ca = document.cookie.split(';');
    for (var i = 0; i < ca.length; i++) {
      var c = ca[i];
      while (c.charAt(0) == ' ') c = c.substring(1, c.length);
      if (c.indexOf(nameEQ) == 0) return c.substring(nameEQ.length, c.length);
    }
    return null;
  };

  // Erase a given key from the local cookie
  this.eraseCookie = (name) => {
    self.setCookie(name, "", -1);
  };
}