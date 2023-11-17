{
  description = "Find images of cats in a given URL.";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";
    flake-utils.url = "github:numtide/flake-utils";
  };

  outputs = { self, nixpkgs, flake-utils, ... }:
    flake-utils.lib.eachDefaultSystem (system:
      let
        pkgs = import nixpkgs {
          inherit system;
        };

        pythonEnv = pkgs.python311.withPackages (ps: with ps; [
          beautifulsoup4
          keras
          numpy
          pillow
          requests
          tensorflow
        ]);
      in
      {
        devShell = pkgs.mkShell {
          buildInputs = [
            pkgs.git
            pythonEnv
          ];

          PYTHONPATH = "${pythonEnv}/${pythonEnv.sitePackages}";
        };
      }
    );
}
