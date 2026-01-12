document.addEventListener("DOMContentLoaded", function() {
  var coll = document.getElementsByClassName("collapsible");

  for (let i = 0; i < coll.length; i++) {
    coll[i].addEventListener("click", function() {
      // Toggle header state
      this.classList.toggle("active");
      // Find the content block after the header
      var content = this.nextElementSibling;     
      if (content.style.display === "block") {
        content.style.display = "none";
      } else {
        content.style.display = "block";
      }
    });
  }
});