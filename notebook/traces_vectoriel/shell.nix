# Run with nix-shell
let
  pkgs = import <nixpkgs> {};
in
pkgs.mkShell {
  packages = [
    (pkgs.python3.withPackages (ps: with ps; [
      pip
      jupyter
      ipykernel
      notebook
    ]))
  ];

shellHook = ''
      # Virtual Env
      export LD_LIBRARY_PATH="${pkgs.stdenv.cc.cc.lib.outPath}/lib:${pkgs.pythonManylinuxPackages.manylinux2014Package}/lib:$LD_LIBRARY_PATH";
      test -d .venv || ${pkgs.python3.interpreter} -m venv .venv
      source .venv/bin/activate
      pip install --upgrade pip
      pip install -r requirements.txt
      codium
    '';
}