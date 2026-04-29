{ sources ? import ../../nix/sources.nix
, inShell ? null
, asterixLibsJson ? builtins.readFile ../../nix/asterix-libs.json
}:

let
  pkgs = import sources.nixpkgs { overlays = [ replacePackages ]; };

  replacePackages = self: super: {
    pythonPackagesExtensions = super.pythonPackagesExtensions ++ [ (pyfinal: pyprev: {
    }) ];
  };

  asterixlibsRef = builtins.fromJSON asterixLibsJson;
  asterixlibDir = pkgs.fetchgit {
    url = asterixlibsRef.url;
    rev = asterixlibsRef.rev;
    sha256 = asterixlibsRef.sha256;
  };
  libasterix = pkgs.callPackage
    "${asterixlibDir}/libs/python" {inShell=false; inherit sources pkgs;};

  pythonDeps = [
    pkgs.python3
    pkgs.python3Packages.mypy
    pkgs.python3Packages.pytest
    pkgs.python3Packages.hypothesis
    pkgs.python3Packages.autopep8
    libasterix
  ];

  python = pkgs.python3.withPackages (python-pkgs: pythonDeps);

  env = pkgs.mkShell {
    name = "asterix-challenges-env";
    packages = [
      pkgs.which
      python
    ];
    LOCALE_ARCHIVE = "${pkgs.glibcLocales}/lib/locale/locale-archive";
    shellHook = ''
      export LC_ALL=C.UTF-8
      export PYTHONPATH=$(pwd):$PYTHONPATH
    '';
    };

in env

