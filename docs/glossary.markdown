---
sitemap: false
permalink: /glossary/
redirect_to: https://the-ai-alliance.github.io/glossary/
---
{% comment %}
We don't use the template redirect.html, because it is written with the assumption
that the redirects are relative to this site, rather than to redirecting to another website.
{% endcomment %}

<!DOCTYPE html>
<html>
<head>
	<link rel="canonical" href="{{ page.redirect_to }}"/>
	<meta http-equiv="content-type" content="text/html; charset=utf-8" />
	<meta http-equiv="refresh" content="0;url={{ page.redirect_to }}" />
</head>
<body>
    <h1>Redirecting...</h1>
    <a href="{{ page.redirect_to }}" target="_blank">Click here if you are not redirected.<a>
    <script>location='{{ page.redirect_to }}'</script>
</body>
</html>
