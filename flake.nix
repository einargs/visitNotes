{
  description = "Tool for doctors to summarize doctor-patient conversations";

  inputs = {
    nixpkgs.url = "nixpkgs/nixos-23.05";
    poetry2nix.url = "github:nix-community/poetry2nix";
    poetry2nix.inputs.nixpkgs.follows = "nixpkgs";
  };
  nixConfig = {
    bash-prompt = ''\[\033[1;32m\][\[\e]0;\u@\h: \w\a\]dev-shell:\w]\$\[\033[0m\] '';
  };

  outputs = { self, nixpkgs, poetry2nix }: 
  let system = "x86_64-linux";
      pkgs = import nixpkgs {
        inherit system;
        config.permittedInsecurePackages = [
          "openssl-1.1.1v"
        ];
        overlay = [ poetry2nix.overlay ];
      };

      backend-app = pkgs.poetry2nix.mkPoetryApplication {
        projectDir = ./.;
      };
  in {
    devShells.x86_64-linux.default = (pkgs.buildFHSUserEnv {
      name = "audio";
      targetPkgs = pkgs: with pkgs; [
        # vlc
        docker
        alsa-lib
        python311Packages.virtualenv
        python311
        nodejs_20
        nodePackages.pnpm
        gcc
        openssl_1_1
        libuuid
        autoconf
        binutils
        curl
        git
        gitRepo
        gnumake
        stdenv.cc
        unzip
        util-linux
        wget
        poetry
      ];

        # export PS1='\[\033[1;32m\][\[\e]0;\u@\h: \w\a\]dev-shell:\w]\$\[\033[0m\] '
      profile = ''
        source .venv/bin/activate
      ''; # may add commandline call to dotenv to load from .env
        # virtualenv .venv

      /*src = [
       ./flake.nix
       ./flake.lock
      ];*/

      /*shellHook = ''
        virtualenv .venv
        source .venv/bin/activate
      '';*/

      /*unpackPhase = ''
        for srcFile in $src; do
          cp $srcFile $(stripHash $srcFile)
        done
      '';*/ 
    }).env;

    packages.x86_64-linux.default = with pkgs; pkgs.dockerTools.buildImage {
      name = "visit-notes";
      tag = "latest";
      copyToRoot = buildEnv {
        name = "image-root";
        pathsToLink = [ "/bin" ];
        paths = [
          dockerTools.fakeNss
          backend-app.dependencyEnv
        ];
      };
      config = {
        Cmd = [ "hypercorn" "app:asgi" "-b" "localhost:80" ];
        ExposedPorts = {
          "80/tcp" = {};
        };
      };
    };
  };
}
