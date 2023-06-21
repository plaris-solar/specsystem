<form id="login" action="<?php echo getenv('SPEC_LOGIN_URL');?>" method="get">
    <?php
    foreach ($_SESSION as $a => $b) {
        echo '<input type="hidden" name="'.htmlentities($a).'" value="'.htmlentities($b).'">';
    }
    ?>
</form>
<script type="text/javascript">
    document.getElementById('login').submit();
</script>
