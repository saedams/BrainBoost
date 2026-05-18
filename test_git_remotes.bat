@echo off
echo Testing Git remotes...
echo.

echo Testing GitLab SSH connection...
ssh -T git@gitlab.fdmci.hva.nl
if %errorlevel% neq 0 (
    echo GitLab SSH test failed!
) else (
    echo GitLab SSH test passed!
)
echo.

echo Testing GitHub SSH connection...
ssh -T git@github.com
if %errorlevel% neq 0 (
    echo GitHub SSH test failed! Please add your SSH key to GitHub.
    echo Go to: https://github.com/settings/keys
    echo Click "New SSH key"
    echo Title: "HVA Laptop"
    echo Paste this key:
    type %USERPROFILE%\.ssh\id_ed25519.pub
) else (
    echo GitHub SSH test passed!
)
echo.

echo Testing git fetch from both remotes...
git fetch --all
if %errorlevel% neq 0 (
    echo Git fetch test failed!
) else (
    echo Git fetch test passed!
)
echo.

echo All tests completed!