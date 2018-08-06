<!DOCTYPE html>
<html>
<head>
	<title>{{title}}</title>
	<meta charset="utf-8">
	<meta http-equiv="X-UA-Compatible" content="IE=edge,chrome=1">
	<meta name="description" content="{{description}}">
	<meta name="viewport" content="width=device-width, initial-scale=1">

	<link rel="shortcut icon" href="/images/favicon.ico" type="image/x-icon">
	<link rel="icon" href="/images/favicon.ico" type="image/x-icon">

	<script type='text/javascript' src='{{root_uri}}js/jquery.min.js'></script>
	<script type='text/javascript' src='{{root_uri}}js/tether.min.js'></script>
	<script type='text/javascript' src='{{root_uri}}js/bootstrap.min.js'></script>

	<link rel="stylesheet" href="{{root_uri}}css/font-awesome.min.css" type="text/css" />
	<link rel="stylesheet" href="{{root_uri}}css/bootstrap.min.css" type="text/css" />

	<link rel="stylesheet" href="{{root_uri}}css/fonts.css" type="text/css" />
	<link rel="stylesheet" href="{{root_uri}}css/style.css" type="text/css" />
	% if defined( 'custom_stylesheets' ):
	% for uri in custom_stylesheets:
	<link rel="stylesheet" href="css/{{uri}}" type="text/css" />
	% end
	% end
	% if defined( 'custom_root_stylesheets' ):
	% for uri in custom_root_stylesheets:
	<link rel="stylesheet" href="{{root_uri}}css/{{uri}}" type="text/css" />
	% end
	% end

    <!-- Polyfill(s) for older browsers -->
    <script src="jsm/core-js/client/shim.min.js"></script>

    <script src="jsm/zone.js/dist/zone.js"></script>
    <script src="jsm/reflect-metadata/Reflect.js"></script>
    <script src="jsm/systemjs/dist/system.src.js"></script>

    <script src="js/systemjs.config.js"></script>
    <script>
      System.import('app').catch(function(err){ console.error(err); });
    </script>
</head>
<body>
