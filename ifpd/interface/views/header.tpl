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

	<script type='text/javascript' src='/js/jquery.min.js'></script>
	<script type='text/javascript' src='/js/popper.min.js'></script>
	<script type='text/javascript' src='/js/bootstrap.min.js'></script>
	<script type='text/javascript' src='/js/clipboard.min.js'></script>

	<link rel="stylesheet" href="/css/font-awesome.min.css" type="text/css" />
	<link rel="stylesheet" href="/css/bootstrap.min.css" type="text/css" />

	<link rel="stylesheet" href="/css/fonts.css" type="text/css" />
	<link rel="stylesheet" href="/css/style.css" type="text/css" />
	% if defined( 'custom_stylesheets' ):
	% for uri in custom_stylesheets:
	<link rel="stylesheet" href="/css/{{uri}}" type="text/css" />
	% end
	% end
</head>
<body>

<div class="container-fluid"><!-- open container-fluid -->
