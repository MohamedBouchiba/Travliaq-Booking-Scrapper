"""Script de vérification de la syntaxe Python de tous les fichiers."""
import py_compile
import pathlib
import sys

def check_syntax():
    """Vérifie la syntaxe de tous les fichiers Python."""
    errors = []
    src_path = pathlib.Path("src")

    print("Verification de la syntaxe Python...")
    print("=" * 50)

    for py_file in src_path.rglob("*.py"):
        try:
            py_compile.compile(str(py_file), doraise=True)
            print(f"[OK] {py_file}")
        except py_compile.PyCompileError as e:
            errors.append((py_file, str(e)))
            print(f"[ERREUR] {py_file}")
            print(f"  Erreur: {e}")

    print("=" * 50)

    if errors:
        print(f"\n[ECHEC] {len(errors)} fichier(s) avec des erreurs de syntaxe:")
        for file, error in errors:
            print(f"  - {file}")
        sys.exit(1)
    else:
        print(f"\n[SUCCES] Tous les fichiers Python sont syntaxiquement corrects!")
        sys.exit(0)

if __name__ == "__main__":
    check_syntax()
