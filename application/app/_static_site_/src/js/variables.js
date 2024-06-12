let currentURL = window.location.href;
let currentHost = currentURL.split("/")[0] + "//" + currentURL.split("/")[2];
let currentHostWithoutProtocol = currentURL.split("/")[2];
const API_URI = `${currentHostWithoutProtocol}`;