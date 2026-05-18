{ sources ? import ../../nix/sources.nix
, asterixLibsJson ? builtins.readFile ../../nix/asterix-libs.json
}:

let
  pkgs = import sources.nixpkgs { };

  asterixlibsRef = builtins.fromJSON asterixLibsJson;
  asterixlibDir = pkgs.fetchgit {
    url = asterixlibsRef.url;
    rev = asterixlibsRef.rev;
    sha256 = asterixlibsRef.sha256;
  };

  haskellPackages = pkgs.haskellPackages.override {
    overrides = self: super: rec {
      libasterix = pkgs.callPackage "${asterixlibDir}/libs/haskell"
        {inShell=false; inherit sources pkgs;};
    };
  };

  ghc = haskellPackages.ghcWithPackages (p: [
    p.libasterix
    p.aeson
    p.optparse-applicative
    p.parallel
    p.threadscope
    p.hlint
  ]);

  env = pkgs.mkShell {
    buildInputs = [
      pkgs.stylish-haskell
      ghc
    ];
  };

in env

