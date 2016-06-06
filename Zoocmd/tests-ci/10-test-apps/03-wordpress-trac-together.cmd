cmd /c zoocmd.cmd --log-level=debug --create-site --site-name="test wordpress 6301" --site-path="c:\inetpub\test wordpress 6301" --site-bindings=http://*:6301
cmd /c zoocmd.cmd --log-level=debug --create-app  --site-name="test wordpress 6301"  --app-path="c:\inetpub\test wordpress 6301\blog 1" --app-name="blog 1"

cmd /c zoocmd.cmd --log-level=debug --create-site --site-name="test trac 6302" --site-path="c:\inetpub\test trac 6302" --site-bindings=http://*:6302

cmd /c zoocmd.cmd --log-level=debug --install --products Wordpress Trac --parameters Wordpress@virtual_path="test wordpress 6301/blog 1" Trac@virtual_path="test trac 6302"

cmd /c tools\curl -I -f http://localhost:6301/blog%%201/wp-admin/setup-config.php
cmd /c tools\curl -I -f http://localhost:6302/


cmd /c %SystemRoot%\system32\inetsrv\appcmd.exe delete site "test wordpress 6301"
cmd /c %SystemRoot%\system32\inetsrv\appcmd.exe delete site "test trac 6302"
cmd /c taskkill /f  /im w3wp.exe
cmd /c rmdir /s /q "c:\inetpub\test wordpress 6301"
cmd /c rmdir /s /q "c:\inetpub\test trac 6302"
