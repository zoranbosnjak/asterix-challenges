{ sources ? import ../../nix/sources.nix
, asterixLibsJson ? builtins.readFile ../../nix/asterix-libs.json
, astToolJson ? builtins.readFile ../../nix/asterix-tool.json
}:

let
  pkgs = import sources.nixpkgs { };

  asterixlibsRef = builtins.fromJSON asterixLibsJson;
  asterixlibDir = pkgs.fetchgit {
    url = asterixlibsRef.url;
    rev = asterixlibsRef.rev;
    sha256 = asterixlibsRef.sha256;
  };

  astToolRef = builtins.fromJSON astToolJson;
  astToolDir = pkgs.fetchgit {
    url = astToolRef.url;
    rev = astToolRef.rev;
    sha256 = astToolRef.sha256;
  };

  astToolPy = pkgs.callPackage
    "${astToolDir}/ast-tool-py/default.nix" {
      inherit sources pkgs asterixlibsRef;
      inShell = false;
    };

  env = pkgs.mkShell {
    buildInputs = [
      astToolPy
    ];
  };

in env

