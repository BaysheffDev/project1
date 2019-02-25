toggle = 0;

function showValue(val, n) {
  document.getElementById('sliderValue' + n).innerHTML=val;

  const width = 240 - (val / 5 * 240);
  document.getElementById('starcover' + n).setAttribute("style", "width:" + width + "px");
  document.getElementById('rating' + n).setAttribute("style", "background:#ffd2d296");
  console.log(width);
}

function dropdown(n) {
  if (!toggle) {
    document.getElementById("reviewtextbox" + n).setAttribute("style", "display:flex");
    toggle = 1;
  }
  else {
    document.getElementById("reviewtextbox" + n).setAttribute("style", "display:none");
    toggle = 0;
  }
}

// function submitreview(name, n, isbn) {
//   document.getElementById("isbn_rating" + n).value = int(isbn);
//   console.log(n + " " + isbn);
// }
