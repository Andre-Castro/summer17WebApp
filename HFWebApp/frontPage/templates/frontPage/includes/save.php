<?php 
  // saving sample text to file (it doesn't include validation!)
  file_put_contents('file.txt', $_POST['text']);

  die('file has been saved');
?>