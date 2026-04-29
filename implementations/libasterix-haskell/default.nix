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
    p.optparse-applicative
    p.libasterix
  ]);

  env = pkgs.mkShell {
    buildInputs = [
      ghc
    ];
  };

in env

