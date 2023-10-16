{ lib, buildNpmPackage, ... }:

buildNpmPackage (rec {
  pname = "visit-notes-site";
  version = "0.0.1";
  npmDepsHash = "sha256-56tpfnp77ckyTxBDVpoa01n3hrS7D83jxwWRqV18V6U=";
  src = ./.;

  # We just copy dist into the out folder
  installPhase = ''
    cp -r ./dist $out/
  '';
})
