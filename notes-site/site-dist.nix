{ lib, buildNpmPackage, ... }:

buildNpmPackage (rec {
  pname = "visit-notes-site";
  version = "0.0.1";
  # To regenerate do `prefetch-npm-deps ./notes-site/package-lock.json`
  npmDepsHash = "sha256-uHRKOZpRTjJ2PDM14o2Rbw2FKY7sRUl0ubfGdj1h1s8=";
  src = ./.;

  # We just copy dist into the out folder
  installPhase = ''
    cp -r ./dist $out/
  '';
})
