
:: use this script to run unit tests locally
::
@echo off
set CI=True

WHERE python3 >nul 2>&1 && (
    echo Found "python3" command
    set PYTHON=python3
) || (
    echo Did not found "python3" command. use "python" instead
    set PYTHON=python
)

::start %PYTHON% scripts/setup_repository.py

%PYTHON% -m coverage run -m unittest discover -s enmapboxtesting
%PYTHON% -m coverage report