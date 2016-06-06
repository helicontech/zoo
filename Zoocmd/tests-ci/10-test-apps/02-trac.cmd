cmd /c zoocmd.cmd --log-level=debug --create-site --site-name="test trac 6302" --site-path="c:\inetpub\test trac 6302" --site-bindings=http://*:6302
cmd /c zoocmd.cmd --log-level=debug --install --product Trac --parameters virtual_path="test trac 6302"

cmd /c tools\curl -I -f http://localhost:6302/

cmd /c %SystemRoot%\system32\inetsrv\appcmd.exe delete site "test trac 6302"
cmd /c taskkill /f  /im w3wp.exe
cmd /c rmdir /s /q "c:\inetpub\test trac 6302"
