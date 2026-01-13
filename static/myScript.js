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


//LINKS

//https://www.perplexity.ai/search/if-you-have-a-github-repo-with-rrdGqopsSF2y2WHnJRB73g
//https://stackoverflow.com/questions/15231812/random-background-images-css3

//random images for each refresh
$(document).ready(function() {

    var bgArray = ['Space.jpg', 'River.jpg', 'Palm Trees.jpg', 'Flower Field.jpg', 'Desert Night.jpg'];
    var bg = bgArray[Math.floor(Math.random() * bgArray.length)];
    var path = 'static/';  // your images are directly in static/
    
    $('.game_background').css({
        'background-image': 'url("' + path + bg + '")',
        'background-repeat': 'no-repeat'
    });
}); 