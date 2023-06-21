<?php
session_start ();
$appid = getenv('APP_ID');
$secret = getenv('SECRET');
$login_url = getenv('LOGIN_URL');
$_SESSION['state'] = session_id();