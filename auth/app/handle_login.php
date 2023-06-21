<?php
$params = array (
    'client_id' =>$appid,
    'redirect_uri' =>getenv('REDIRECT_URL'),
    'response_type' =>'token',
    'response_mode' =>'form_post',
    'scope' =>'https://graph.microsoft.com/User.Read',
    'state' =>$_SESSION['state']
);

header ('Location: '.$login_url.'?'.http_build_query ($params));
