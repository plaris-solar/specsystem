<?php
if (array_key_exists ('access_token', $_POST)){
    $_SESSION['jwt_token'] = $_POST['access_token'];
    $t = $_SESSION['jwt_token'];

    $ch = curl_init ();
    curl_setopt ($ch, CURLOPT_HTTPHEADER, array ('Authorization: Bearer '.$t, 'Conent-type: application/json'));

    curl_setopt ($ch, CURLOPT_URL, "https://graph.microsoft.com/v1.0/me/");
    curl_setopt ($ch, CURLOPT_RETURNTRANSFER, 1);

    $rez = json_decode (curl_exec ($ch), 1);

    if (array_key_exists ('error', $rez)){
        var_dump ($rez['error']);
        die();
    }
}