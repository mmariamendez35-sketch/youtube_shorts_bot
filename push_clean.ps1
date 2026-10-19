# Este script se ejecuta una sola vez para hacer push.
# El PAT se lee de una variable de entorno para no exponerlo en el codigo.

$pat = $env:GH_PAT
$login = 'mmariamendez35-sketch'
$repoName = 'youtube_shorts_bot'

Set-Location 'C:\Users\Usuario\.gemini\scratch\youtube_shorts_bot'

# Eliminar push_repo.ps1 del tracking de git
git rm -f push_repo.ps1 --cached 2>$null
Remove-Item push_repo.ps1 -Force -ErrorAction SilentlyContinue

# Rehacer el historial limpio
git checkout --orphan temp_branch
git add -A
# Asegurarse de que push_repo.ps1 no esta incluido
git reset HEAD push_repo.ps1 -ErrorAction SilentlyContinue 2>$null
git commit -m 'Initial commit - YouTube Shorts autonomous bot'
git branch -D main -ErrorAction SilentlyContinue 2>$null
git branch -M main

# Push limpio
git remote remove origin -ErrorAction SilentlyContinue 2>$null
git remote add origin "https://${pat}@github.com/${login}/${repoName}.git"
git push -u origin main --force
