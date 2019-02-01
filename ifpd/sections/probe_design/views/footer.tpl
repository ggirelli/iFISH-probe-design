
<div class="row">
	<div id="footer" class="col col-12">
		iFISH Probe Designer v2.0.1.post4 - &copy; Gabriele Girelli 2016-19
	</div>
</div>

<script type="text/javascript">
$(function () {

	// Enable tooltips
	$('[data-toggle="tooltip"]').tooltip()

})
</script>

%if SHOW_COOKIE_CONSENT_BANNER:
<link rel="stylesheet" type="text/css" href="//cdnjs.cloudflare.com/ajax/libs/cookieconsent2/3.1.0/cookieconsent.min.css" />
<script src="//cdnjs.cloudflare.com/ajax/libs/cookieconsent2/3.1.0/cookieconsent.min.js"></script>
<script>
window.addEventListener("load", function(){
window.cookieconsent.initialise({
  "palette": {
    "popup": {
      "background": "#237afc"
    },
    "button": {
      "background": "transparent",
      "text": "#fff",
      "border": "#fff"
    }
  },
  "position": "top",
  "static": true
})});
</script>
%end

</body>
</html>
