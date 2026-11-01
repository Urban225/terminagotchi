# Correctif Windows de la version recente (.pyz)

La branche principale de ce fork contient un jeu PC plus ancien. Le fichier
`terminagotchi-essai.pyz` utilise une autre arborescence (notamment
`tg/scenes.py` et `tg/intro.py`). Il ne faut donc pas remplacer aveuglement
les fichiers du jeu historique.

Ce patcher agit directement sur **la version recente distribuee en .pyz**
sans toucher aux sauvegardes ni au depot principal.

## Utilisation

Depuis le dossier qui contient `terminagotchi-essai.pyz`, avec Python installe :

```powershell
py .\tools\patch_windows_pyz.py .\terminagotchi-essai.pyz
py .\terminagotchi-essai-windows.pyz
```

Ou avec un nom de sortie personnalise :

```powershell
py .\tools\patch_windows_pyz.py .\terminagotchi-essai.pyz -o .\terminagotchi-windows.pyz
```

Le script modifie uniquement quatre fichiers Python internes a l'archive :

- `tg/scenes.py` : evite le chargement de `termios` sur Windows pendant
  la detection des capacites du terminal ;
- `tg/plateforme.py` : declare des cmdlets et alias PowerShell usuels ;
- `tg/core.py` : reconnait ces commandes pour les verifications ;
- `tg/verif.py` : evite les faux avertissements "outil non installe".

Le script echoue explicitement si l'archive ne contient pas les fichiers ou
les passages de code attendus ; il ne modifie **jamais** l'archive source.

## Validation

Effectuee sur l'archive transmise le 1er novembre 2026 :
- Archive ZIP de sortie valide (178 membres, aucun membre corrompu).
- Les quatre modules Python modifies compilent.
- La detection Windows est verifiee par analyse du code.
- L'execution interactive complete doit etre confirmee sur un PC Windows.

Lorsque les sources recentes seront disponibles dans le depot, le correctif
pourra etre porte directement sur ces sources au lieu d'utiliser ce patcher.
