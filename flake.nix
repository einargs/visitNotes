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

      azure-inputs = with pkgs; [
        stdenv.cc
        gcc
        openssl_1_1
        alsa-lib
        libuuid
        binutils
        util-linux
      ];

      # Still don't know if this properly has everything and I can actually run
      # stuff but we'll find out. I might need to use root path, I might be able
      # to use python module syntax to get at an installed version of it?
      # Probably just use root-path.
      backend-app-env = (pkgs.poetry2nix.mkPoetryEnv {
        projectDir = ./.;
        python = pkgs.python311;
        preferWheels = true;
        overrides = pkgs.poetry2nix.overrides.withDefaults (self: super: {
          azure-cognitiveservices-speech = super.azure-cognitiveservices-speech
            .overridePythonAttrs (old: {
              buildInputs = (old.buildInputs or [])
                ++ azure-inputs
                ++ [ pkgs.gst_all_1.gstreamer ];
            });
        });
      });
      # The actually built site.
      site-dist = import ./notes-site/site-dist.nix pkgs;
      # shell app with the app environment built in for testing instead of
      # rebuilding docker containers.
      shell-app = pkgs.writeShellApplication {
        name = "shell-app";
        # Do I need to include azure-inputs?
        runtimeInputs = [
          backend-app-env
        ];
        text = ''
          export STATIC_FILES=${site-dist}

          hypercorn ${./.}/app:asgi -b localhost:8000
        '';
      };

  in {
    devShells.x86_64-linux.default = (pkgs.buildFHSUserEnv {
      name = "audio";
      targetPkgs = pkgs: with pkgs; [
        # vlc
        docker
        python311
        nodejs_20
        nodePackages.pnpm
        prefetch-npm-deps
        poetry

        wget
        curl
        autoconf
        git
        gitRepo
        gnumake
        unzip
      ] ++ azure-inputs;

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

    nixosConfigurations.vm = nixpkgs.lib.nixosSystem {

    };

    # Doesn't have the environmental variables needed to talk to the apis.
    apps.x86_64-linux.default = {
      type = "app";
      program = "${shell-app}/bin/shell-app";
    };

    packages.x86_64-linux = {
      app-env = backend-app-env;
      site = site-dist;
      script = shell-app;
      docker = with pkgs; pkgs.dockerTools.buildImage {
        name = "visit-notes";
        tag = "latest";
        copyToRoot = buildEnv {
          name = "image-root";
          pathsToLink = [ "/bin" ];
          paths = [
            dockerTools.fakeNss
            backend-app-env
          ];
        };
        config = {
          Env = [
            "STATIC_FILES=${site-dist}"
          ];
          Cmd = [ "hypercorn" "${./.}/app:asgi" "-b" "0.0.0.0:80" ];
          ExposedPorts = {
            "80/tcp" = {};
          };
        };
      };
    };
  };
}
