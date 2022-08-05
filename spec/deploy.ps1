$currentPrincipal = New-Object Security.Principal.WindowsPrincipal([Security.Principal.WindowsIdentity]::GetCurrent())
if ( ! $currentPrincipal.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator) ) 
{
	Write-Output "This script must be run as Administrator"
	exit -1
}

.venv\Scripts\activate

git pull

pip install -r .\requirements.txt

py manage.py migrate

Push-Location
cd .\ui\
npm install --force
npm run build

Pop-Location
py manage.py collectstatic --noinput

# Force IIS to reload the application
iisreset